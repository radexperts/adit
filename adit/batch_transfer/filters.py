import django_filters
from .models import BatchTransferRequest


class BatchTransferRequestFilter(django_filters.FilterSet):
    class Meta:
        model = BatchTransferRequest
        fields = ("status",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["status"].label = "Filter by Status"
