# Generated by Django 5.1.2 on 2024-10-12 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('animals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimalActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(choices=[('sitting', 'Sitting'), ('standing', 'Standing'), ('walking', 'Walking'), ('grazing', 'Grazing'), ('ruminating', 'Ruminating')], max_length=50)),
                ('duration', models.IntegerField(default=0)),
                ('animal_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='animals.animal')),
            ],
        ),
    ]
