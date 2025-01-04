# Generated by Django 5.1.4 on 2025-01-04 10:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("club", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="clubapply",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="generation",
            name="club",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="club.club"
            ),
        ),
        migrations.AddField(
            model_name="clubapply",
            name="generation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="club.generation",
            ),
        ),
        migrations.AddField(
            model_name="userclub",
            name="club",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_clubs",
                to="club.club",
            ),
        ),
        migrations.AddField(
            model_name="userclub",
            name="last_generation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="club.generation"
            ),
        ),
        migrations.AddField(
            model_name="userclub",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="usergeneration",
            name="generation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="club.generation"
            ),
        ),
        migrations.AddField(
            model_name="usergeneration",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
