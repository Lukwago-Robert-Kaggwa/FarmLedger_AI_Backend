from django.contrib import admin
from .models import Animal, BlockchainCredentials

# Register your models here.
admin.site.register(Animal)
admin.site.register(BlockchainCredentials)
