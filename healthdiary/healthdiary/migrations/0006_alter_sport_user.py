# Generated by Django 4.1.13 on 2024-04-11 08:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("healthdiary", "0005_remove_sport_users_liked_sport_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sport",
            name="user",
            field=models.ManyToManyField(
                related_name="sport_user", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
