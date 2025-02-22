from django.urls import path
from .views import store_location, get_locations, get_latest_location, update_location

urlpatterns = [
    path('store/', store_location, name='store_location'),
    path('get-locations/', get_locations, name='get_locations'),
    path('latest-location/', get_latest_location, name='get_latest_location'),
    path('update-location/', update_location, name='update_location'),
]
