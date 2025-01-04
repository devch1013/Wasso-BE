# Generated by Django 5.1.4 on 2025-01-04 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AbsentApply",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "대기"),
                            ("APPROVED", "승인"),
                            ("REJECTED", "반려"),
                        ],
                        default="PENDING",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "absent_applies",
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PRESENT", "Present"),
                            ("LATE", "Late"),
                            ("ABSENT", "Absent"),
                            ("FAILED", "Failed"),
                        ],
                        default="PRESENT",
                        max_length=10,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("is_modified", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "attendances",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.CharField(max_length=255)),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                ("attendance_start_datetime", models.DateTimeField()),
                ("attendance_end_datetime", models.DateTimeField()),
                ("begin_minutes", models.IntegerField()),
                ("late_tolerance_minutes", models.IntegerField()),
                ("location", models.CharField(max_length=255)),
                ("latitude", models.DecimalField(decimal_places=8, max_digits=10)),
                ("longitude", models.DecimalField(decimal_places=8, max_digits=11)),
                ("qr_code_url", models.CharField(max_length=255)),
                ("qr_code", models.CharField(max_length=15)),
                (
                    "attendance_type",
                    models.CharField(
                        choices=[
                            ("QR", "QR"),
                            ("LOCATION", "Location"),
                            ("BOTH", "Both"),
                        ],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "events",
            },
        ),
        migrations.CreateModel(
            name="Notice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "notices",
            },
        ),
    ]
