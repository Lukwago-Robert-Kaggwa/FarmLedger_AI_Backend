from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('authuser.urls')),
    path('api/v1/locations/', include('location.urls')),
    path('api/v1/activities/', include('activities.urls')),
    path('api/v1/animals/', include('animals.urls')), 
]
