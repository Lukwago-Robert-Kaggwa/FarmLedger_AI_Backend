from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Location
from animals.models import Animal  # Import the Animal model
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from django.http import JsonResponse
from .models import Animal, Location
from django.db import transaction


@csrf_exempt
def store_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        animal_id = data.get("animal_id")

        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"error": "Animal not found"}, status=404)

        # Get the current time
        current_time = timezone.now()

        # Check for existing locations older than 1 minute and delete them
        old_locations = Location.objects.filter(
            timestamp__lt=current_time - timezone.timedelta(minutes=1)
        )
        for loc in old_locations.iterator():
            loc.delete()

        # Creew location entry associated with the animal
        Location.objects.create(animal=animal, latitude=latitude, longitude=longitude)

        return JsonResponse({"status": "success"}, status=201)


@csrf_exempt
def get_locations(request):
    try:
        body = json.loads(request.body)
        animal_id = body.get("animal_id")

        if not animal_id:
            return JsonResponse({"error": "Animal ID is required."}, status=400)

        animal = get_object_or_404(Animal, rfid_uid=animal_id)

        # Get locations based on the animal ID
        locations = Location.objects.filter(animal=animal).values(
            "animal__rfid_uid", "latitude", "longitude", "timestamp"
        )

        return JsonResponse(list(locations), safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)


@csrf_exempt
def get_latest_location(request):
    try:
        data = json.loads(request.body)
        rfid = data.get("rfid")
        # Fetch the animal using its RFID
        animal = Animal.objects.get(rfid_uid=rfid)

        # Fetch the latest location for the given animal
        location = Location.objects.filter(animal=animal).order_by("-timestamp").first()

        if location:
            # Return the location details
            return JsonResponse(
                {
                    "rfid": animal.rfid_uid,  # Use animal's RFID here
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "timestamp": location.timestamp,
                }
            )
        else:
            # If no location found for the animal
            return JsonResponse(
                {"error": "No location data found for this animal"}, status=404
            )

    except Animal.DoesNotExist:
        # If the animal is not found
        return JsonResponse({"error": "Animal not found"}, status=404)

    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract required fields
            animal_id = data.get("animalId")
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if not animal_id or latitude is None or longitude is None:
                return JsonResponse({"error": "Missing required fields."}, status=400)

            try:
                # Fetch the animal instance
                animal = Animal.objects.get(rfid_uid=animal_id)

                # Fetch location entries
                loc_1 = Location.objects.filter(animal=animal, loc_id=1).first()
                loc_2 = Location.objects.filter(animal=animal, loc_id=2).first()
                loc_3 = Location.objects.filter(animal=animal, loc_id=3).first()
                loc_4 = Location.objects.filter(animal=animal, loc_id=4).first()
                loc_5 = Location.objects.filter(animal=animal, loc_id=5).first()

                if not all([loc_1, loc_2, loc_3, loc_4, loc_5]):
                    return JsonResponse({"error": "One or more location entries are missing."}, status=400)

                # Update locations in a transactional block
                with transaction.atomic():
                    loc_1.latitude, loc_1.longitude, loc_1.timestamp = loc_2.latitude, loc_2.longitude, loc_2.timestamp
                    loc_1.save()

                    loc_2.latitude, loc_2.longitude, loc_2.timestamp = loc_3.latitude, loc_3.longitude, loc_3.timestamp
                    loc_2.save()

                    loc_3.latitude, loc_3.longitude, loc_3.timestamp = loc_4.latitude, loc_4.longitude, loc_4.timestamp
                    loc_3.save()

                    loc_4.latitude, loc_4.longitude, loc_4.timestamp = loc_5.latitude, loc_5.longitude, loc_5.timestamp
                    loc_4.save()

                    loc_5.latitude, loc_5.longitude, loc_5.timestamp = latitude, longitude, timezone.now()
                    loc_5.save()

                return JsonResponse({"message": "Location updated successfully."}, status=200)

            except Animal.DoesNotExist:
                return JsonResponse({"error": "Animal does not exist."}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
