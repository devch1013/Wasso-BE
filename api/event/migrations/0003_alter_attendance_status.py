# Generated by Django 5.1.4 on 2025-02-25 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.IntegerField(choices=[(0, '인증전'), (1, '출석'), (2, '지각'), (3, '결석')], default=1),
        ),
    ]
