# Generated by Django 4.1.13 on 2024-04-07 03:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("healthdiary", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BodyPart",
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
                ("name", models.CharField(max_length=200)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
