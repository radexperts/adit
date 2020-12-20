from django.template import Library

register = Library()


@register.inclusion_tag("core/_job_control_panel.html", takes_context=True)
def job_control_panel(context):
    return {
        "delete_url": "continuous_transfer_job_delete",
        "cancel_url": "continuous_transfer_job_cancel",
        "verify_url": "continuous_transfer_job_verify",
        "user": context["user"],
        "job": context["job"],
    }
