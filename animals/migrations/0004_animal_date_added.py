# Generated by Django 5.1.5 on 2025-01-25 12:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0003_blockchaincredentials'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
