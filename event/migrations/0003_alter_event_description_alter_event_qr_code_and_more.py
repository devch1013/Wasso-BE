# Generated by Django 5.1.4 on 2025-01-24 11:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="description",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="qr_code",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="qr_code_url",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
