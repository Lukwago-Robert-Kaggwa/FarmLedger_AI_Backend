from django.urls import path
from .views import create_animal, delete_animal_activities, delete_animal_locations, get_healthy_animals, get_sick_animals, get_all_animals_data, get_user_animals_data, save_blockchain_credentials

urlpatterns = [
    path('create-animal/', create_animal, name='create_animal'),  # Add this line
    path('delete-animal-activities/', delete_animal_activities, name='delete_animal_activities'),
    path('delete-animal-locations/', delete_animal_locations, name='get_sick_locations'),
    path('get-sick-animals/', get_sick_animals, name='get_sick_animals'),
    path('get-healthy-animals/', get_healthy_animals, name='get_healthy_animals'),
    path('get-all-animals-data/', get_all_animals_data, name='get_all_animals_data'),
    path('get-user-animals-data/', get_user_animals_data, name='get_user_animals_data'),
    path('save-blockchain-credentials/', save_blockchain_credentials, name='save_blockchain_credentials'),
]
