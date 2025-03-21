# Generated by Django 5.1.4 on 2025-03-13 14:44

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_club_deleted_club_deleted_at_generation_deleted_and_more'),
        ('event', '0004_alter_attendance_latitude_alter_attendance_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_attendances', to='club.genmember'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='generation_mapping',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='club.genmember'),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
