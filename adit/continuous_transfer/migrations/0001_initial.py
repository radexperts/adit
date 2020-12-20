# Generated by Django 3.1.3 on 2020-12-20 10:19

import adit.core.validators
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContinuousTransferJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('UV', 'Unverified'), ('PE', 'Pending'), ('IP', 'In Progress'), ('CI', 'Canceling'), ('CA', 'Canceled'), ('SU', 'Success'), ('WA', 'Warning'), ('FA', 'Failure')], default='UV', max_length=2)),
                ('urgent', models.BooleanField(default=False)),
                ('message', models.TextField(blank=True, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('trial_protocol_id', models.CharField(blank=True, max_length=64, validators=[django.core.validators.RegexValidator(inverse_match=True, message='Contains invalid backslash character', regex='\\\\')])),
                ('trial_protocol_name', models.CharField(blank=True, max_length=64, validators=[django.core.validators.RegexValidator(inverse_match=True, message='Contains invalid backslash character', regex='\\\\')])),
                ('archive_password', models.CharField(blank=True, max_length=50)),
                ('project_name', models.CharField(max_length=150)),
                ('project_description', models.TextField(max_length=2000)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.dicomnode')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_transfer_jobs', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.dicomnode')),
            ],
            options={
                'permissions': [('can_process_urgently', 'Can process urgently (prioritized and without scheduling).')],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContinuousTransferSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locked', models.BooleanField(default=False)),
                ('suspended', models.BooleanField(default=False)),
                ('slot_begin_time', models.TimeField(default=datetime.time(22, 0), help_text='Must be set in UTC time zone.')),
                ('slot_end_time', models.TimeField(default=datetime.time(8, 0), help_text='Must be set in UTC time zone.')),
                ('transfer_timeout', models.IntegerField(default=3)),
            ],
            options={
                'verbose_name_plural': 'Continuous transfer settings',
            },
        ),
        migrations.CreateModel(
            name='DataElementFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dicom_tag', models.CharField(max_length=100)),
                ('filter_type', models.CharField(choices=[('EQ', 'equals'), ('EN', 'equals not'), ('CO', 'contains'), ('CN', 'contains not'), ('RE', 'regex'), ('RN', 'regex not')], default='EQ', max_length=2)),
                ('filter_value', models.CharField(max_length=200)),
                ('case_sensitive', models.BooleanField(default=False)),
                ('order', models.SmallIntegerField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='continuous_transfer.continuoustransferjob')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='ContinuousTransferTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PE', 'Pending'), ('IP', 'In Progress'), ('CA', 'Canceled'), ('SU', 'Success'), ('WA', 'Warning'), ('FA', 'Failure')], default='PE', max_length=2)),
                ('message', models.TextField(blank=True, default='')),
                ('log', models.TextField(blank=True, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('patient_id', models.CharField(max_length=64)),
                ('study_uid', models.CharField(max_length=64)),
                ('series_uids', models.JSONField(blank=True, null=True, validators=[adit.core.validators.validate_uids])),
                ('pseudonym', models.CharField(blank=True, max_length=64, validators=[django.core.validators.RegexValidator(inverse_match=True, message='Contains invalid backslash character', regex='\\\\'), django.core.validators.RegexValidator(inverse_match=True, message='Contains invalid control characters.', regex='[\\f\\n\\r]')])),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='continuous_transfer.continuoustransferjob')),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='continuoustransferjob',
            index=models.Index(fields=['owner', 'status'], name='continuous__owner_i_250893_idx'),
        ),
    ]
