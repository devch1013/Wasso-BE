# Generated by Django 5.1.4 on 2025-01-24 11:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("club", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="club",
            name="current_generation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="current_club",
                to="club.generation",
            ),
        ),
    ]
