# Generated by Django 5.1.5 on 2025-02-03 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_rename_animal_id_animalactivity_animal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalactivity',
            name='counter',
            field=models.IntegerField(default=0),
        ),
    ]
