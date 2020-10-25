from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, DetailView
from django.conf import settings
from django_tables2 import SingleTableMixin
from adit.main.mixins import OwnerRequiredMixin
from adit.main.forms import FilterFormHelper
from .models import BatchTransferSettings, BatchTransferJob
from .forms import BatchTransferJobForm
from .tables import BatchTransferRequestTable
from .filters import BatchTransferRequestFilter


class BatchTransferJobCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateView
):
    model = BatchTransferJob
    form_class = BatchTransferJobForm
    template_name = "batch_transfer/batch_transfer_job_form.html"
    permission_required = "batch_transfer.add_batchtransferjob"

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        response = super().form_valid(form)

        # Do it after an ongoing transaction (even if it is currently
        # unnecessary as ATOMIC_REQUESTS is False), see also
        # https://spapas.github.io/2019/02/25/django-fix-async-db/
        # Currently I am not using it because it is hard to test, but there
        # it is already fixed in an upcoming release, see
        # https://code.djangoproject.com/ticket/30457
        # TODO transaction.on_commit(lambda: enqueue_batch_job(self.object.id))
        job = self.object
        if user.is_staff or settings.BATCH_TRANSFER_UNVERIFIED:
            job.status = BatchTransferJob.Status.PENDING
            job.save()
            job.delay()

        return response

    def dispatch(self, request, *args, **kwargs):
        batch_transfer_settings = BatchTransferSettings.get()
        if batch_transfer_settings.locked and not request.user.is_staff:
            return TemplateView.as_view(
                template_name="batch_transfer/batch_transfer_locked.html"
            )(request)
        return super().dispatch(request, *args, **kwargs)


class BatchTransferJobDetailView(
    LoginRequiredMixin, OwnerRequiredMixin, SingleTableMixin, DetailView
):
    owner_accessor = "owner"
    table_class = BatchTransferRequestTable
    model = BatchTransferJob
    context_object_name = "job"
    template_name = "batch_transfer/batch_transfer_job_detail.html"

    def get_table_data(self):
        job = self.get_object()

        # pylint: disable=attribute-defined-outside-init
        per_page = int(self.request.GET.get("per_page", 50))
        if per_page > 1000:
            per_page = 1000
        self.paginate_by = per_page  # Used by django_tables2

        # pylint: disable=attribute-defined-outside-init
        self.filterset = BatchTransferRequestFilter(
            data=self.request.GET or None, request=self.request, queryset=job.requests
        )
        self.object_list = self.filterset.qs

        return self.object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["filter"] = self.filterset
        data["filter"].form.helper = FilterFormHelper("status")
        data["object_list"] = self.object_list
        return data
