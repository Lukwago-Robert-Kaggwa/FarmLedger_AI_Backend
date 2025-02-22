from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
import joblib
import pandas as pd
from django.db.models import F
from django.db import transaction
import logging
import numpy as np
from django.utils.timezone import now

from animals.models import Animal
from .models import ActivityAnomaly, ActivityDurations, AnimalActivity


logger = logging.getLogger(__name__)
model = joblib.load("activities/model/multi_label_animal_behavior_model.pkl")


def increment_activity_counters():
    """
    This function goes through each AnimalActivity instance and adds 10 to the counter.
    """
    AnimalActivity.objects.all().update(counter=F("counter") + 10)


@api_view(["POST"])
def predict_animal_behavior(request):
    try:
        # Extract x, y, z values from the POST request
        data = request.data
        x = float(data.get("x"))
        y = float(data.get("y"))
        z = float(data.get("z"))
        animal_id = data.get("animalId")

        # Create a DataFrame with the same structure as the training data
        input_data = pd.DataFrame([[x, y, z]], columns=["x", "y", "z"])

        # Make predictions
        prediction = model.predict(input_data)

        # Format the response with the activity names
        activities = ["sitting", "standing", "walking", "grazing", "ruminating"]
        result = dict(zip(activities, prediction[0]))

        update_activity(animal_id, result)
        increment_activity_counters()
        update_activity_durations()

        return Response({"prediction": result})

    except Exception as e:
        return Response({"error": str(e)}, status=400)


def update_activity(animal_id, activities):
    try:
        animal = Animal.objects.get(rfid_uid=animal_id)
        behaviour = ""

        for activity, value in activities.items():
            if int(value) == 1:  # Convert np.int64 to Python int
                try:
                    behaviour += f"*{activity}*"
                    activity_instance = AnimalActivity.objects.get(
                        animal=animal, activity=activity
                    )
                    activity_instance.duration += 10  # Increment duration by 10 seconds
                    activity_instance.save()
                except AnimalActivity.DoesNotExist:
                    return Response(
                        {
                            "error": f"Animal Activity '{activity}' does not exist for this animal"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

        animal.behaviour = behaviour
        animal.save()
        return Response(
            {"message": "Activity updated successfully"}, status=status.HTTP_200_OK
        )

    except Animal.DoesNotExist:
        return Response(
            {"error": "Animal does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


def update_activity_durations():
    """
    Updates ActivityDurations for each AnimalActivity based on counter values.
    Resets duration after updating each day.
    Resets counter after 3 days.
    """
    # Define day thresholds in seconds (corrected values)
    one_day = 86400 # 24 hours
    two_days = 172800  # 48 hours
    three_days = 259200  # 72 hours

    with transaction.atomic():  # Ensures atomic updates
        for activity in AnimalActivity.objects.filter(counter__gte=one_day):
            try:
                # Get or create corresponding ActivityDurations record
                activity_duration, created = ActivityDurations.objects.get_or_create(
                    animal=activity.animal
                )

                # Check and update activity durations based on counter values
                if activity.activity == "sitting":
                    if activity.counter >= one_day and activity.counter < two_days:
                        activity_duration.sitting_day_1 += activity.duration
                    elif activity.counter >= two_days and activity.counter < three_days:
                        activity_duration.sitting_day_2 += activity.duration
                    elif activity.counter >= three_days:
                        activity_duration.sitting_day_3 += activity.duration

                elif activity.activity == "standing":
                    if activity.counter >= one_day and activity.counter < two_days:
                        activity_duration.standing_day_1 += activity.duration
                    elif activity.counter >= two_days and activity.counter < three_days:
                        activity_duration.standing_day_2 += activity.duration
                    elif activity.counter >= three_days:
                        activity_duration.standing_day_3 += activity.duration

                elif activity.activity == "walking":
                    if activity.counter >= one_day and activity.counter < two_days:
                        activity_duration.walking_day_1 += activity.duration
                    elif activity.counter >= two_days and activity.counter < three_days:
                        activity_duration.walking_day_2 += activity.duration
                    elif activity.counter >= three_days:
                        activity_duration.walking_day_3 += activity.duration

                elif activity.activity == "grazing":
                    if activity.counter >= one_day and activity.counter < two_days:
                        activity_duration.grazing_day_1 += activity.duration
                    elif activity.counter >= two_days and activity.counter < three_days:
                        activity_duration.grazing_day_2 += activity.duration
                    elif activity.counter >= three_days:
                        activity_duration.grazing_day_3 += activity.duration

                elif activity.activity == "ruminating":
                    if activity.counter >= one_day and activity.counter < two_days:
                        activity_duration.ruminating_day_1 += activity.duration
                    elif activity.counter >= two_days and activity.counter < three_days:
                        activity_duration.ruminating_day_2 += activity.duration
                    elif activity.counter >= three_days:
                        activity_duration.ruminating_day_3 += activity.duration

                # Reset duration after updating
                activity.duration = 0

                # Reset counter after 3 days
                if activity.counter >= three_days:
                    activity.counter = 0
                    # After every three days, we assume the animal is healthy, then perform anomaly detection
                    activity.animal.status = "healthy"
                    activity.animal.save(update_fields=["status"])
                    detect_anomalies()

                # Save updates
                activity_duration.save()
                activity.save()

            except Exception as e:
                logger.error(f"Error updating activity for {activity.animal}: {e}")

def detect_anomalies():
    """
    Detects anomalies in ActivityDurations using percentiles (IQR method).
    Saves anomalies in ActivityAnomaly and deletes old ones.
    """
    with transaction.atomic():
        for activity_duration in ActivityDurations.objects.all():
            # Collect all durations for each activity over 3 days
            activities = {
                "sitting": [activity_duration.sitting_day_1, activity_duration.sitting_day_2, activity_duration.sitting_day_3],
                "standing": [activity_duration.standing_day_1, activity_duration.standing_day_2, activity_duration.standing_day_3],
                "walking": [activity_duration.walking_day_1, activity_duration.walking_day_2, activity_duration.walking_day_3],
                "grazing": [activity_duration.grazing_day_1, activity_duration.grazing_day_2, activity_duration.grazing_day_3],
                "ruminating": [activity_duration.ruminating_day_1, activity_duration.ruminating_day_2, activity_duration.ruminating_day_3],
            }

            for activity, durations in activities.items():
                # Convert durations to numpy array for percentile calculations
                data = np.array(durations)
                Q1 = np.percentile(data, 25)  # 25th percentile
                Q3 = np.percentile(data, 75)  # 75th percentile
                IQR = Q3 - Q1  # Interquartile Range

                # Define anomaly thresholds
                lower_bound = Q1 - (1.5 * IQR)
                upper_bound = Q3 + (1.5 * IQR)

                # Check each day's duration for anomalies
                for day_idx, value in enumerate(durations):
                    if value < lower_bound or value > upper_bound:
                        # Update animal status if grazing or ruminating anomaly is detected
                        if activity in ["grazing", "ruminating"]:
                            activity.animal.status = "sick"
                            activity.animal.save(update_fields=["status"])

                        # Anomaly detected, save it in ActivityAnomaly
                        ActivityAnomaly.objects.create(
                            animal=activity_duration.animal,
                            activity=activity,
                            day=day_idx + 1,  # Convert index to day (1, 2, or 3)
                            recorded_value=value,
                            detected_at=now(),
                        )

        # Cleanup anomalies older than 3 days
        ActivityAnomaly.cleanup_old_anomalies()


@api_view(["POST"])
def get_anomalies_for_animal(request):
    animal_id = request.data.get("animalId")

    if not animal_id:
        return Response({"error": "animal_id is required"}, status=400)

    anomalies = ActivityAnomaly.objects.filter(animal_id=animal_id).order_by("-detected_at")

    result = [
        {
            "id": anomaly.id,
            "activity": anomaly.activity,
            "day": anomaly.day,
            "recorded_value": anomaly.recorded_value,
            "detected_at": anomaly.detected_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for anomaly in anomalies
    ]

    return Response({"anomalies": result}, status=200)

