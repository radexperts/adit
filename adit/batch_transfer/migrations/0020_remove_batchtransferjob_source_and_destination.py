# Generated by Django 4.2.4 on 2023-09-03 22:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("batch_transfer", "0019_alter_batchtransfertask_source_destination_not_null"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="batchtransferjob",
            name="destination",
        ),
        migrations.RemoveField(
            model_name="batchtransferjob",
            name="source",
        ),
    ]
