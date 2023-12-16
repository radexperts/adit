# Generated by Django 4.2.7 on 2023-12-10 22:20

from django.apps import AppConfig
from django.db import migrations


def convert_institute_to_group_accesses(apps: AppConfig, schema_editor):
    DicomNodeInstituteAccess = apps.get_model("core.DicomNodeInstituteAccess")
    DicomNodeGroupAccess = apps.get_model("core.DicomNodeGroupAccess")
    Group = apps.get_model("auth.Group")

    for access in DicomNodeInstituteAccess.objects.all():
        DicomNodeGroupAccess.objects.create(
            dicom_node=access.dicom_node,
            group=Group.objects.get(name=access.institute.name),
            source=access.source,
            destination=access.destination,
        )


def convert_group_to_institute_accesses(apps, schema_editor):
    DicomNodeInstituteAccess = apps.get_model("core.DicomNodeInstituteAccess")
    DicomNodeGroupAccess = apps.get_model("core.DicomNodeGroupAccess")

    for access in DicomNodeGroupAccess.objects.all():
        DicomNodeInstituteAccess.objects.create(
            dicom_node=access.dicom_node,
            institute=Institute.objects.get(name=access.group.name),
            source=access.source,
            destination=access.destination,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_convert_institutes_to_groups"),
        ("core", "0010_dicomnodegroupaccess"),
    ]

    operations = [
        migrations.RunPython(
            convert_institute_to_group_accesses, convert_group_to_institute_accesses
        )
    ]
