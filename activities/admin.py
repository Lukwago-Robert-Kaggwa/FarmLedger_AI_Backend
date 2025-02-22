from django.contrib import admin
from .models import ActivityDurations, AnimalActivity, ActivityAnomaly

# Register your models here.
admin.site.register(AnimalActivity)
admin.site.register(ActivityDurations)
admin.site.register(ActivityAnomaly)
