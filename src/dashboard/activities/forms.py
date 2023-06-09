from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from process_manager.models import Phase, Project, Activity
from no_sql_client import NoSQLClient


class ActivityForm(forms.Form):
    error_messages = {
        "duplicated_activity": _("An Activity with this name is already registered."),
    }
    # choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()
    # project = forms.ChoiceField(choices = [])
    # phase = forms.ChoiceField(choices = [])
    # total_tasks = forms.IntegerField()
    # order = forms.IntegerField()
    couch_id = forms.CharField(required=False)

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Activity.objects.filter(name=name).exists():
            self.add_error("name", self.error_messages["duplicated_activity"])
        return name

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['project'].choices = [(x.id, x.name) for x in Project.objects.all()]
        # self.fields['phase'].choices = [(p.id, p.name) for p in Phase.objects.all()]


class UpdateActivityForm(forms.ModelForm):
    # choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()
    # couch_id = forms.CharField(required=False, disabled=True)
    # phase = forms.ModelChoiceField(queryset=Phase.objects.distinct())
    # total_tasks = forms.IntegerField()
    # order = forms.IntegerField()

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['project'].queryset = [(x, x.name) for x in Project.objects.list()]

    class Meta:
        model = Activity
        fields = ["name", "description"]  # specify the fields to be displayed
