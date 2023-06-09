from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from process_manager.models import Project
from no_sql_client import NoSQLClient


class ProjectForm(forms.Form):
    error_messages = {
        "duplicated_project": _("A project with this name is already registered."),
    }
    name = forms.CharField()
    description = forms.CharField()
    couch_id = forms.CharField(required=False)

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Project.objects.filter(name=name).exists():
            self.add_error("name", self.error_messages["duplicated_project"])
        return name

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateProjectForm(forms.ModelForm):
    name = forms.CharField()
    description = forms.CharField()
    couch_id = forms.CharField(required=False)

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = []  # specify the fields to be displayed
