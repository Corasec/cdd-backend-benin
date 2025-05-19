from django import forms
from django.utils.translation import gettext_lazy as _
from no_sql_client import NoSQLClient
from process_manager.enums import FieldTypeEnum
from process_manager.models import FormField, FormType, Task
from django.apps import apps
from django.forms.models import inlineformset_factory


class FormTypeForm(forms.ModelForm):
    error_messages = {
        "duplicate_field": _("Another field with the same name is already defined"),
        "duplicate_form": _("Another form associated with the task is already defined"),
    }
    name = forms.CharField(max_length=140, help_text=_("Unique name for the Model"))
    description = (
        forms.Textarea()
    )  # help_text=_("Description of the form")) #help_text=_("Description of the form"))
    couch_id = forms.CharField(
        required=False, disabled=True, help_text=_("Unique name for the Model")
    )
    # model = models.CharField(blank=False, null=False, max_length=140, choices=MODELS, help_text=_("Model associated with the form"))
    # is_generic = forms.BooleanField(help_text=_("Does the form apply to all instances of an object?"))
    # task = forms.ModelChoiceField(queryset=Task.objects.all(), initial=0)
    # content_type = forms.ChoiceField()
    # object_id = forms.IntegerField(disabled=True)
    # content_object = forms.ChoiceField(
    # 	choices=(())
    # ) # GenericForeignKey("content_type", "object_id")

    # FormFieldSet = inlineformset_factory(FormType, FormField, fields=['name',])

    def __init__(self, *args, **kwargs):
        """
        @TODO. Get List of models from couch_db. For the selected model, get its instances from couch db
        For this project, just limit model to Task, but this can be applied generically to any model
        """
        super().__init__(*args, **kwargs)
        # nsc = NoSQLClient()
        # # Get Models
        # MODELS = []
        # app_models = apps.get_models()
        # for m in app_models:
        # 	if m.__name__ == "Task":
        # 		MODELS.append((m.__name__, m.__name__))

        # self.fields['content_type'].choices = MODELS
        # # Get tasks
        # tasks = Task.objects.all()
        # TASKS = []
        # for t in tasks:
        # 	TASKS.append((t.id, t.name))
        # self.fields['content_object'].choices = TASKS

    class Meta:
        model = FormType
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "couch_id": forms.TextInput(
                attrs={"class": "form-control", "readonly": "True"}
            ),
        }


class UpdateFormTypeForm(forms.ModelForm):
    name = forms.CharField(help_text=_("Name of the form"))
    description = forms.CharField(help_text=_("Description of the form"))
    # is_generic = forms.BooleanField()
    # content_type = forms.ChoiceField()
    # object_id = forms.IntegerField(disabled=True)
    # content_object = forms.ChoiceField()
    couch_id = forms.CharField(required=False)

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FormType
        fields = ["name"]  #'is_generic']


class FormFieldForm(forms.ModelForm):
    class Meta:
        FIELD_TYPES = []
        for itm in FieldTypeEnum:
            FIELD_TYPES.append((itm.value, itm.value))

        model = FormField
        fields = ["label", "field_type", "name"]
        widgets = {
            # 'form_type': forms.Select(
            # 	attrs={
            # 		'class': 'form-control'
            # 	}
            # ),
            "label": forms.TextInput(attrs={"class": "form-control"}),
            "field_type": forms.Select(
                attrs={"class": "form-control"}, choices=FIELD_TYPES
            ),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            # 'options': forms.Textarea(
            # 	attrs={
            # 		'class': 'form-control'
            # 	}
            # ),
            # 'default': forms.Textarea(
            # 	attrs={
            # 		'class': 'form-control'
            # 	}
            # ),
            # 'description': forms.Textarea(
            # 	attrs={
            # 		'class': 'form-control'
            # 	}
            # ),
            # 'required': forms.BooleanField(
            # 	# attrs={
            # 	# 	'class': 'form-control'
            # 	# }
            # ),
            # 'hidden': forms.BooleanField(
            # 	# attrs={
            # 	# 	'class': 'form-control'
            # 	# }
            # ),
            # 'read_only': forms.BooleanField(
            # 	# attrs={
            # 	# 	'class': 'form-control'
            # 	# }
            # ),
        }


FormFieldFormSet = inlineformset_factory(
    FormType,
    FormField,
    form=FormFieldForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
)
# ImageFormSet = inlineformset_factory(
#     Product, Image, form=ImageForm,
#     extra=1, can_delete=True, can_delete_extra=True
# )


class FormFieldForm_Old(forms.Form):
    error_messages = {
        "duplicate_field": _("Another field with the same name is already defined"),
        "duplicate_task_form": _(
            "Another form associated with the task is already defined"
        ),
    }
    FIELD_TYPES = []
    for itm in FieldTypeEnum:
        FIELD_TYPES.append((itm.value, itm.value))

    form_type = forms.ModelChoiceField(queryset=FormType.objects.all(), initial=0)
    # task = forms.ChoiceField(help_text=_("Task associated with this Form"))
    label = forms.CharField(help_text=_("Field Label"))
    field_type = forms.ChoiceField(choices=FIELD_TYPES, help_text=_("Type of field"))
    name = forms.CharField(help_text=_("Unique identifier for the field"))
    options = (
        forms.Textarea()
    )  # help_text=_("For Select, enter list of Options, each on a new line."))
    default = forms.Textarea()  # help_text=_("Default value for the field"))
    description = forms.Textarea()  # help_text=_("Text to be displayed as help"))
    required = forms.BooleanField()  # help_text=_("Is the field mandatory"))
    hidden = forms.BooleanField(help_text=_("Is the field hidden?"))
    read_only = forms.BooleanField(help_text=_("Is the field read-only?"))
    form = forms.JSONField(disabled=True)

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        nsc = NoSQLClient()
        # administrative_levels_db = nsc.get_db('administrative_levels')
        # label = get_administrative_levels_by_level(administrative_levels_db)[0]['administrative_level'].upper()
        # self.fields['administrative_level'].label = label

        # administrative_level_choices = get_administrative_level_choices(administrative_levels_db)
        # self.fields['administrative_level'].widget.choices = administrative_level_choices
        # self.fields['administrative_level'].choices = administrative_level_choices
        # self.fields['administrative_level'].widget.attrs['class'] = "region"
        # self.fields['administrative_levels'].widget.attrs['class'] = "hidden"

    def _post_clean(self):
        super()._post_clean()

    def clean_task(self):
        task = self.cleaned_data.get("task")
        if FormField.objects.filter(form_type="Task").exists():
            self.add_error("task", self.error_messages["duplicate_task_form"])
        return task

    def clean_name(self):
        task = self.cleaned_data.get("task")
        name = self.cleaned_data.get("name")
        if FormField.objects.filter(form_type="Task", name=name).exists():
            self.add_error("name", self.error_messages["duplicate_field"])
        return task
