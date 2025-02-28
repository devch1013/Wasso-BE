# Generated by Django 5.1.4 on 2025-02-27 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_rename_done_generation_activated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='club',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='generation',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generation',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
