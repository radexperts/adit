from django.db import models
from django.urls import reverse
from main.models import DicomJob

class SiteConfig(models.Model):
    batch_transfer_locked = models.BooleanField(default=False)
    

class BatchTransferJob(DicomJob):
    JOB_TYPE = 'BA'
    
    project_name = models.CharField(max_length=150)
    project_description = models.TextField(max_length=2000)
    pseudonymize = models.BooleanField(default=True)
    trial_protocol_id = models.CharField(max_length=64, blank=True)
    trial_protocol_name = models.CharField(max_length=64, blank=True)

    class Meta:
        permissions = ((
            'can_cancel_batchtransferjob',
            'Can cancel batch transfer job'
        ), (
            'can_transfer_unpseudonymized',
            'Can transfer unpseudonymized'
        ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_type = self.JOB_TYPE

    def get_absolute_url(self):
        return reverse("batch_transfer_job_detail", args=[str(self.id)])


class BatchTransferItem(models.Model):

    class Status(models.TextChoices):
        SUCCESS = 'SU', 'Success'
        WARNING = 'WA', 'Warning'
        ERROR = 'ER', 'Error'

    class Meta:
        unique_together = (('row_id', 'job'))

    job = models.ForeignKey(BatchTransferJob, on_delete=models.CASCADE,
            related_name='items')
    row_id = models.CharField(max_length=16)
    patient_id = models.CharField(null=True, max_length=64)
    patient_name = models.CharField(null=True, max_length=256)
    patient_birth_date = models.DateField()
    study_date = models.DateField()
    modality = models.CharField(max_length=16)
    pseudonym = models.CharField(null=True, max_length=256)
    status_code = models.CharField(null=True, max_length=2, choices=Status.choices)
    status_message = models.CharField(null=True, max_length=256)
