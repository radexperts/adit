from django.urls import path

from adit.core.views import HtmxTemplateView

from .views import (
    BatchTransferJobCancelView,
    BatchTransferJobCreateView,
    BatchTransferJobDeleteView,
    BatchTransferJobDetailView,
    BatchTransferJobListView,
    BatchTransferJobRestartView,
    BatchTransferJobResumeView,
    BatchTransferJobRetryView,
    BatchTransferJobVerifyView,
    BatchTransferTaskDetailView,
    BatchTransferUpdatePreferencesView,
)

urlpatterns = [
    path(
        "update-preferences/",
        BatchTransferUpdatePreferencesView.as_view(),
    ),
    path(
        "help/",
        HtmxTemplateView.as_view(template_name="batch_transfer/_batch_transfer_help.html"),
        name="batch_transfer_help",
    ),
    path(
        "jobs/",
        BatchTransferJobListView.as_view(),
        name="batch_transfer_job_list",
    ),
    path(
        "jobs/new/",
        BatchTransferJobCreateView.as_view(),
        name="batch_transfer_job_create",
    ),
    path(
        "jobs/<int:pk>/",
        BatchTransferJobDetailView.as_view(),
        name="batch_transfer_job_detail",
    ),
    path(
        "jobs/<int:pk>/delete/",
        BatchTransferJobDeleteView.as_view(),
        name="batch_transfer_job_delete",
    ),
    path(
        "jobs/<int:pk>/verify/",
        BatchTransferJobVerifyView.as_view(),
        name="batch_transfer_job_verify",
    ),
    path(
        "jobs/<int:pk>/cancel/",
        BatchTransferJobCancelView.as_view(),
        name="batch_transfer_job_cancel",
    ),
    path(
        "jobs/<int:pk>/resume/",
        BatchTransferJobResumeView.as_view(),
        name="batch_transfer_job_resume",
    ),
    path(
        "jobs/<int:pk>/retry/",
        BatchTransferJobRetryView.as_view(),
        name="batch_transfer_job_retry",
    ),
    path(
        "jobs/<int:pk>/restart/",
        BatchTransferJobRestartView.as_view(),
        name="batch_transfer_job_restart",
    ),
    path(
        "jobs/<int:pk>/verify/",
        BatchTransferJobVerifyView.as_view(),
        name="batch_transfer_job_verify",
    ),
    path(
        "jobs/<int:job_id>/tasks/<int:task_id>/",
        BatchTransferTaskDetailView.as_view(),
        name="batch_transfer_task_detail",
    ),
]
