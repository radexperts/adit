# Generated by Django 5.0.4 on 2024-07-09 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0010_uploadpermissionsupport_delete_uploadpermission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='uploadpermissionsupport',
            options={'default_permissions': (), 'managed': False, 'permissions': [('upload_data_rights', 'Can upload data'), ('upload_data_view', 'Can view upload')]},
        ),
    ]
