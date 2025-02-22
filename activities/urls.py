from django.urls import path
from .views import get_anomalies_for_animal, predict_animal_behavior, update_activity

urlpatterns = [
    path('update_activity/', update_activity, name='update_activity'),
    path('predict/', predict_animal_behavior, name='predict_animal_behavior'),
    path("get-anomalies/", get_anomalies_for_animal, name="get_anomalies_for_animal"),
]
