from django.db import models
from animals.models import Animal
from django.utils.timezone import now, timedelta


class AnimalActivity(models.Model):
    activity_choices = [
        ("sitting", "Sitting"),
        ("standing", "Standing"),
        ("walking", "Walking"),
        ("grazing", "Grazing"),
        ("ruminating", "Ruminating"),
    ]
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE
    )  # Assuming you have an Animal model
    activity = models.CharField(max_length=50, choices=activity_choices)
    duration = models.IntegerField(default=0)  # Duration in seconds
    counter = models.IntegerField(default=0)

    class Meta:
        unique_together = ("animal", "activity")

    def __str__(self):
        return f"{self.activity} for {self.duration} seconds"


class ActivityDurations(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    sitting_day_1 = models.IntegerField(default=0)
    sitting_day_2 = models.IntegerField(default=0)
    sitting_day_3 = models.IntegerField(default=0)
    standing_day_1 = models.IntegerField(default=0)
    standing_day_2 = models.IntegerField(default=0)
    standing_day_3 = models.IntegerField(default=0)
    walking_day_1 = models.IntegerField(default=0)
    walking_day_2 = models.IntegerField(default=0)
    walking_day_3 = models.IntegerField(default=0)
    grazing_day_1 = models.IntegerField(default=0)
    grazing_day_2 = models.IntegerField(default=0)
    grazing_day_3 = models.IntegerField(default=0)
    ruminating_day_1 = models.IntegerField(default=0)
    ruminating_day_2 = models.IntegerField(default=0)
    ruminating_day_3 = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.animal}"


class ActivityAnomaly(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    activity = models.CharField(max_length=50)
    day = models.IntegerField()  # 1, 2, or 3
    recorded_value = models.IntegerField()
    detected_at = models.DateTimeField(auto_now_add=True)  # Timestamp when detected

    def __str__(self):
        return f"Anomaly: {self.animal} - {self.activity} Day {self.day} ({self.recorded_value})"

    @classmethod
    def cleanup_old_anomalies(cls):
        """
        Deletes anomalies older than 3 days.
        """
        cutoff_date = now() - timedelta(days=3)
        cls.objects.filter(detected_at__lt=cutoff_date).delete()
