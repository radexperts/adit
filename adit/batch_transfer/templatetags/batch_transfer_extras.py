from django.template import Library
from ..models import TransferTask

register = Library()


@register.inclusion_tag("core/_job_control_panel.html")
def job_control_panel():
    return {
        "delete_url": "batch_transfer_job_delete",
        "cancel_url": "batch_transfer_job_cancel",
        "verify_url": "batch_transfer_job_verify",
    }


@register.filter
def task_status_badge_class(status):
    css_class = ""
    if status == TransferTask.Status.PENDING:
        css_class = "badge-secondary"
    elif status == TransferTask.Status.IN_PROGRESS:
        css_class = "badge-info"
    elif status == TransferTask.Status.CANCELED:
        css_class = "badge-dark"
    elif status == TransferTask.Status.SUCCESS:
        css_class = "badge-success"
    elif status == TransferTask.Status.FAILURE:
        css_class = "badge-danger"
    return css_class
