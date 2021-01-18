from django import forms
from django.forms.models import BaseInlineFormSet
from crispy_forms.helper import FormHelper
from adit.core.forms import DicomNodeChoiceField
from adit.core.models import DicomNode
from .models import ContinuousTransferJob, DataElementFilter


class DateInput(forms.DateInput):
    input_type = "date"


class ContinuousTransferJobForm(forms.ModelForm):
    source = DicomNodeChoiceField(True, DicomNode.NodeType.SERVER)
    destination = DicomNodeChoiceField(False, DicomNode.NodeType.SERVER)

    class Meta:
        model = ContinuousTransferJob
        fields = (
            "source",
            "destination",
            "urgent",
            "project_name",
            "project_description",
            "trial_protocol_id",
            "trial_protocol_name",
            "start_date",
            "end_date",
        )
        labels = {
            "urgent": "Start transfer urgently",
        }
        help_texts = {
            "urgent": (
                "Start transfer directly (without scheduling) and prioritize it."
            ),
        }
        widgets = {"start_date": DateInput(), "end_date": DateInput()}

    def __init__(self, *args, **kwargs):
        can_process_urgently = kwargs.pop("can_process_urgently")

        # Not needed for continuous transfer, but we have to remove it before
        # calling the super __init__ method
        kwargs.pop("can_transfer_unpseudonymized")

        super().__init__(*args, **kwargs)

        self.fields["source"].widget.attrs["class"] = "custom-select"
        self.fields["destination"].widget.attrs["class"] = "custom-select"

        if not can_process_urgently:
            del self.fields["urgent"]

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class DataElementFilterForm(forms.ModelForm):
    class Meta:
        model = DataElementFilter
        fields = ("dicom_tag", "filter_type", "filter_value", "case_sensitive")


class BaseDataElementFilterFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[forms.formsets.ORDERING_FIELD_NAME].initial = index + 1


DataElementFilterFormSet = forms.inlineformset_factory(
    ContinuousTransferJob,
    DataElementFilter,
    formset=BaseDataElementFilterFormSet,
    form=DataElementFilterForm,
    extra=1,
    can_order=True,
)


class DataElementFilterFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "continuous_transfer/data_element_filter_formset.html"
