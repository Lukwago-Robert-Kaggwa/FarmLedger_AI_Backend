from django.db import models
from authuser.models import User  # Import the User model

class Animal(models.Model):
    rfid_uid = models.CharField(max_length=100, unique=True)  # Unique RFID UID
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with a user
    status = models.CharField(max_length=200, default='healthy')
    behaviour = models.CharField(max_length=200, default='none')
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Animal {self.rfid_uid} owned by {self.user.name}"

class BlockchainCredentials(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=False)
    file_id = models.CharField(max_length=20, blank=False, null=False)
    transaction_id = models.CharField(max_length=100, blank=False, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Enforce unique combination of animal and file_id
        unique_together = ('animal', 'file_id')

    def __str__(self) -> str:
        return f"{self.animal.rfid_uid} - {self.file_id}"
