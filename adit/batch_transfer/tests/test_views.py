from io import BytesIO
from unittest.mock import patch

import pandas as pd
import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from adit.accounts.factories import InstituteFactory, UserFactory
from adit.core.factories import DicomNodeInstituteAccessFactory, DicomServerFactory
from adit.core.models import DicomServer

from ..models import BatchTransferJob


# Somehow the form data must be always generated from scratch (maybe cause of the
# SimpleUploadedFile) otherwise tests fail.
@pytest.fixture
def form_data(db):
    buffer = BytesIO()
    data = pd.DataFrame(
        [
            ["1001", "1.2.840.113845.11.1000000001951524609.20200705182951.2689481", "WSOHMP4N"],
            ["1002", "1.2.840.113845.11.1000000001951524609.20200705170836.2689469", "C2XJQ2AR"],
            ["1003", "1.2.840.113845.11.1000000001951524609.20200705172608.2689471", "KRS8CZ3S"],
        ],
        columns=["PatientID", "StudyInstanceUID", "Pseudonym"],
    )
    data.to_excel(buffer, index=False)

    return {
        "source": DicomServerFactory.create().id,
        "destination": DicomServerFactory.create().id,
        "project_name": "Apollo project",
        "project_description": "Fly to the moon",
        "ethics_application_id": "12345",
        "batch_file": SimpleUploadedFile(
            name="sample_sheet.xlsx",
            content=buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }


@pytest.mark.django_db
def test_user_must_be_logged_in_to_access_view(client):
    response = client.get(reverse("batch_transfer_job_create"))
    assert response.status_code == 302
    response = client.post(reverse("batch_transfer_job_create"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_must_have_permission_to_access_view(client):
    user = UserFactory.create()
    client.force_login(user)
    response = client.get(reverse("batch_transfer_job_create"))
    assert response.status_code == 403
    response = client.post(reverse("batch_transfer_job_create"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_with_permission_can_access_form(client):
    user = UserFactory.create()
    batch_transfer_group = Group.objects.get(name="batch_transfer_group")
    user.groups.add(batch_transfer_group)
    client.force_login(user)
    response = client.get(reverse("batch_transfer_job_create"))
    assert response.status_code == 200
    assertTemplateUsed(response, "batch_transfer/batch_transfer_job_form.html")


@patch("celery.current_app.send_task")
def test_batch_job_created_and_enqueued_with_auto_verify(
    send_task_mock, client, settings, form_data
):
    settings.BATCH_TRANSFER_UNVERIFIED = True
    user = UserFactory.create()
    batch_transfer_group = Group.objects.get(name="batch_transfer_group")
    user.groups.add(batch_transfer_group)
    client.force_login(user)
    institute = InstituteFactory.create()
    institute.users.add(user)
    source_server = DicomServer.objects.get(pk=form_data["source"])
    DicomNodeInstituteAccessFactory.create(
        dicom_node=source_server, institute=institute, source=True
    )
    destination_server = DicomServer.objects.get(pk=form_data["destination"])
    DicomNodeInstituteAccessFactory.create(
        dicom_node=destination_server, institute=institute, destination=True
    )
    client.post(reverse("batch_transfer_job_create"), form_data)
    job = BatchTransferJob.objects.first()
    assert job and job.tasks.count() == 3
    send_task_mock.assert_called_once_with(
        "adit.batch_transfer.tasks.ProcessBatchTransferJob", (1,)
    )


@patch("celery.current_app.send_task")
def test_batch_job_created_and_not_enqueued_without_auto_verify(
    send_task_mock, client, settings, form_data
):
    settings.BATCH_TRANSFER_UNVERIFIED = False
    user = UserFactory.create()
    batch_transfer_group = Group.objects.get(name="batch_transfer_group")
    user.groups.add(batch_transfer_group)
    client.force_login(user)
    institute = InstituteFactory.create()
    institute.users.add(user)
    source_server = DicomServer.objects.get(pk=form_data["source"])
    DicomNodeInstituteAccessFactory.create(
        dicom_node=source_server, institute=institute, source=True
    )
    destination_server = DicomServer.objects.get(pk=form_data["destination"])
    DicomNodeInstituteAccessFactory.create(
        dicom_node=destination_server, institute=institute, destination=True
    )
    client.post(reverse("batch_transfer_job_create"), form_data)
    job = BatchTransferJob.objects.first()
    assert job and job.tasks.count() == 3
    send_task_mock.assert_not_called()


def test_job_cant_be_created_with_missing_fields(client, form_data):
    user = UserFactory.create()
    batch_transfer_group = Group.objects.get(name="batch_transfer_group")
    user.groups.add(batch_transfer_group)
    client.force_login(user)
    for key_to_exclude in form_data:
        invalid_form_data = form_data.copy()
        del invalid_form_data[key_to_exclude]
        response = client.post(reverse("batch_transfer_job_create"), invalid_form_data)
        assert len(response.context["form"].errors) > 0
        assert BatchTransferJob.objects.first() is None
