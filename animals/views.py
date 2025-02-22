import json
from django.http import JsonResponse
from activities.models import ActivityAnomaly, ActivityDurations, AnimalActivity
from authuser.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Animal, BlockchainCredentials
from location.models import Location
from django.views.decorators.csrf import csrf_exempt
from location.models import Location


@api_view(["POST"])
def create_animal(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                rfid_uid = data.get("rfid_uid")
                user_id = data.get("userId")
                status = data.get("status", "healthy")

                if not rfid_uid or not user_id:
                    return JsonResponse({"error": "rfid_uid and username are required."}, status=400)

                if Animal.objects.filter(rfid_uid=rfid_uid).exists():
                    return JsonResponse({"error": f"Animal with rfid tag {rfid_uid} already exists."}, status=400)

                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return JsonResponse({"error": "User does not exist."}, status=404)

                animal = Animal.objects.create(rfid_uid=rfid_uid, user=user, status=status)
                animal.save()

                activity_choices = ['sitting', 'standing', 'walking', 'grazing','ruminating']
                for activity in activity_choices:
                    AnimalActivity.objects.create(animal=animal, activity=activity, duration=0)

                # Create a new activity record with default values
                ActivityDurations.objects.create(animal=animal)

                i = 0
                while i in range(0,5):        
                    Location.objects.create(loc_id= i+1, animal=animal, latitude=0.00000, longitude=0.00000)
                    i = i+1

                return JsonResponse({"message": "Animal added successfully."}, status=201)

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data."}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

@api_view(["POST"])
def get_healthy_animals(request):
    param = json.loads(request.body)
    user = User.objects.get(id=param.get("userId"))

    data = []

    animals = Animal.objects.filter(status="healthy", user=user)

    for animal in animals:
        location = Location.objects.filter(
            animal=animal
        ).first()

        anomalies = ActivityAnomaly.objects.filter(animal=animal).order_by("-detected_at") 
        anomaly = [[anom.activity, anom.detected_at] for anom in anomalies] if anomalies.exists() else []

        data.append(
            {
                "rfid": animal.rfid_uid,
                "behaviour": animal.behaviour,
                "healthStatus": animal.status,
                "statusLastModified": location.timestamp if location else None,
                "latitude": location.latitude if location else None,
                "longitude": location.longitude if location else None,
                "anomalies": anomaly,
            }
        )

    return JsonResponse(data, safe=False)


@api_view(["POST"])
def get_sick_animals(request):
    param = json.loads(request.body)
    user = User.objects.get(id=param.get("userId"))

    data = []

    # Fetch all sick animals
    animals = Animal.objects.filter(status="sick", user=user)

    for animal in animals:
        location = Location.objects.filter(
            animal=animal
        ).first()

        anomalies = ActivityAnomaly.objects.filter(animal=animal).order_by("-detected_at") 
        anomaly = [[anom.activity, anom.detected_at] for anom in anomalies] if anomalies.exists() else []

        data.append(
            {
                "rfid": animal.rfid_uid,
                "behaviour": animal.behaviour,
                "healthStatus": animal.status,
                "statusLastModified": location.timestamp if location else None,
                "latitude": location.latitude if location else None,
                "longitude": location.longitude if location else None,
                "anomalies": anomaly,
            }
        )

    return JsonResponse(data, safe=False)

@api_view(["POST"])
def delete_animal_activities(request):
    try:
        param = json.loads(request.body)
        animal = Animal.objects.get(rfid_uid=param.get("rfid"))
        animal.status = "removed"
        animal.save()
        AnimalActivity.objects.filter(animal=animal).delete()
        return Response({"Activities deleted successfully"}, status=200)
    except Animal.DoesNotExist:
            return JsonResponse({"error": "Animal not found"}, status=status.HTTP_404_NOT_FOUND)
    except Location.DoesNotExist:
            return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def delete_animal_locations(request):
    try:
        param = json.loads(request.body)
        animal = Animal.objects.get(rfid_uid=param.get("rfid"))
        Location.objects.filter(animal=animal).delete()
        animal.status = "removed"
        animal.save()
        return Response({"Locations deleted successfully"}, status=200)
    except Animal.DoesNotExist:
            return JsonResponse({"error": "Animal not found"}, status=status.HTTP_404_NOT_FOUND)
    except Location.DoesNotExist:
            return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def get_all_animals_data(request):
    if request.method == "GET":
        animals = Animal.objects.all()
        data = []

        for animal in animals:
            locations = Location.objects.filter(animal=animal).order_by("timestamp")

            moves = [[loc.latitude, loc.longitude] for loc in locations] if locations.exists() else []

            last_location = locations.last()
            lat = last_location.latitude if last_location else None
            lng = last_location.longitude if last_location else None
            status_last_modified = last_location.timestamp if last_location else None

            credentials = BlockchainCredentials.objects.filter(animal=animal)
            file_ids = [cred.file_id for cred in credentials] if credentials.exists() else []
            transaction_ids = [cred.transaction_id for cred in credentials] if credentials.exists() else []

            animal_data = {
                "userName": animal.user.name,
                "rfid": animal.rfid_uid,
                "behaviour": animal.behaviour,
                "lat": lat,
                "lng": lng,
                "healthStatus": animal.status,
                "statusLastModified": status_last_modified,
                "dateAdded": animal.date_added,
                "moves": moves,
                "fileIds": file_ids,
                "transactionIds": transaction_ids,
            }

            data.append(animal_data)

        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_user_animals_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=data.get("userId"))

            animals = Animal.objects.filter(user=user)
            data = []

            for animal in animals:
                locations = Location.objects.filter(animal=animal).order_by("timestamp")
                credentials =  BlockchainCredentials.objects.filter(animal=animal)

                if credentials.exists():
                    fileIds = [ [cred.file_id] for cred in credentials]
                    transactionIds = [ [cred.transaction_id] for cred in credentials]

                if BlockchainCredentials.DoesNotExist:
                    fileIds = []
                    transactionIds = []

                if locations.exists():
                    moves = [[loc.latitude, loc.longitude] for loc in locations]

                    animal_data = {
                        "rfid": animal.rfid_uid,
                        "behaviour": animal.behaviour,
                        "lat": locations.last().latitude,
                        "lng": locations.last().longitude,
                        "healthStatus": animal.status,
                        "statusLastModified": locations.last().timestamp,
                        "moves": moves,
                        "fileIds": fileIds,
                        "transactionIds": transactionIds
                    }
                    data.append(animal_data)
            return JsonResponse(data, safe=False)
        except:
            if User.DoesNotExist:
                return JsonResponse({"error": "User does not exist"}, status=400)
            if Animal.DoesNotExist:
                return JsonResponse({"error": "Animal does not exist"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@api_view(['POST'])
def save_blockchain_credentials(request):
    try:
        rfid = request.data.get("rfid")
        file_id = request.data.get("fileId")
        transaction_id = request.data.get("transactionId")
        
        animal = Animal.objects.get(rfid_uid=rfid)
      
        BlockchainCredentials.objects.create(animal=animal, file_id=str(file_id), transaction_id=str(transaction_id))
        
        return JsonResponse({"message": "Crendentials saved successfully"}, status=status.HTTP_201_CREATED)
    except Animal.DoesNotExist:
        return JsonResponse({"error": "Animal not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    