# Generated by Django 4.1.13 on 2024-05-07 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('healthdiary', '0009_alter_sporthistory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mainmenu',
            options={'ordering': ['id']},
        ),
    ]
