from django.db import models
from animals.models import Animal  # Import the Animal model

class Location(models.Model):
    loc_id = models.IntegerField(default=0)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.rfid_uid}: ({self.latitude}, {self.longitude}) at {self.timestamp}"
