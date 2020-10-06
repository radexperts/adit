from django.apps import AppConfig
from django.db.models.signals import post_migrate
from adit.main.site import register_main_menu_item, register_transfer_job


class BatchTransferConfig(AppConfig):
    name = "adit.batch_transfer"

    def ready(self):
        register_app()

        # Put calls to db stuff in this signal handler
        post_migrate.connect(init_db, sender=self)


def register_app():
    register_main_menu_item(
        url_name="batch_transfer_job_create", label="Batch Transfer"
    )

    # pylint: disable=import-outside-toplevel
    from .models import BatchTransferJob
    from .views import BatchTransferJobDetailView
    from .tasks import batch_transfer

    def delay(job_id):
        batch_transfer.delay(job_id)

    register_transfer_job(
        type_key=BatchTransferJob.JOB_TYPE,
        type_name="Batch Transfer",
        detail_view=BatchTransferJobDetailView,
        delay_func=delay,
    )


def init_db(**kwargs):  # pylint: disable=unused-argument
    create_group()
    create_app_settings()


def create_group():
    # pylint: disable=import-outside-toplevel
    from adit.accounts.utils import create_group_with_permissions

    create_group_with_permissions(
        "batch_transferrers",
        (
            "batch_transfer.add_batchtransferjob",
            "batch_transfer.view_batchtransferjob",
            "batch_transfer.cancel_batchtransferjob",
        ),
    )


def create_app_settings():
    # pylint: disable=import-outside-toplevel
    from .models import AppSettings

    app_settings = AppSettings.objects.first()
    if not app_settings:
        AppSettings.objects.create()
