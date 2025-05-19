from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from process_manager.models import Phase, Project
from no_sql_client import NoSQLClient


class PhaseForm(forms.Form):
    error_messages = {
        "duplicated_phase": _("A phase with this name is already registered."),
    }
    # choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Phase.objects.filter(name=name).exists():
            self.add_error("name", self.error_messages["duplicated_phase"])
        return name

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['project'].choices = [(x.id, x.name) for x in Project.objects.all()]


class UpdatePhaseForm(forms.ModelForm):
    # choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['project'].queryset = [(x, x.name) for x in Project.objects.list()]

    class Meta:
        model = Phase
        fields = ["name", "description"]  # specify the fields to be displayed
