from django.db import models
from no_sql_client import NoSQLClient
from django.utils.translation import gettext_lazy as _
from process_manager.enums import FieldTypeEnum
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from rest_framework import serializers


# Create your models here.
# The project object on couch looks like this
# {
#     "_id": "219e50bc41c65648039b08eb10e7b925",
#     "_rev": "1-2851220dbb9d42ee9a7d1f2889cf4f83",
#     "type": "project",
#     "name": "COSO",
#     "description": "Lorem ipsum"
# }
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    couch_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "projet"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = {
            "name": self.name,
            "type": "project",
            "description": self.description,
            "sql_id": self.id,
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": self.couch_id})[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document["_id"]
            self.save()
        return self

    def simple_save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


# The Phase object on couch looks like this
# {
#     "_id": "abc123",
#     "_rev": "2-ae3f90c1f84c91ff97a4bffd5686a9b7",
#     "type": "phase",
#     "project_id": "219e50bc41c65648039b08eb10e7b925",
#     "administrative_level_id": "adml123", NO
#     "name": "Community Mobilization",
#     "order": 1,
#     "description": "Lorem ipsum",
#     "capacity_attachments": [
#         {
#             "name": "tutorial.pdf",
#             "url": "/attachments/1253a3516c4e88550768d719be04e43d/report.pdf",
#             "bd_id": "1253a3516c4e88550768d719be04e43d"
#         }
#     ]
# }
class Phase(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    couch_id = models.CharField(max_length=255, blank=True)
    order = models.IntegerField()

    class Meta:
        verbose_name = "phase"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = {
            "name": self.name,
            "type": "phase",
            "description": self.description,
            "order": self.order,
            "capacity_attachments": [],
            "project_id": self.project.couch_id,
            "sql_id": self.id,
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": self.couch_id})[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document["_id"]
            self.save()
        return self

    def simple_save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


# The activity object on couch looks like this
# {
#     "_id": "219e50bc41c65648039b08eb10032af1",
#     "_rev": "357-8cacccf0cbd94ecbaf2f45242a946eb0",
#     "type": "activity",
#     "project_id": "219e50bc41c65648039b08eb10e7b925",
#     "phase_id": "abc123",
#     "administrative_level_id": "adml123",
#     "name": "Réunion cantonale",
#     "order": 1,
#     "description": "Participer à la réunion cantonale conduite par l’AADB",
#     "capacity_attachments": [
#         {
#             "name": "tutorial.pdf",
#             "url": "/attachments/1253a3516c4e88550768d719be04e43d/report.pdf",
#             "bd_id": "1253a3516c4e88550768d719be04e43d"
#         }
#     ],
#     "total_tasks": 4,
#     "completed_tasks": 0
# }
class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    phase = models.ForeignKey("Phase", on_delete=models.CASCADE)
    total_tasks = models.IntegerField()
    order = models.IntegerField()
    couch_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "étape"
        verbose_name_plural = "étapes"

    def __str__(self):
        return self.phase.name + "-" + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = {
            "name": self.name,
            "type": "activity",
            "description": self.description,
            "order": self.order,
            "capacity_attachments": [],
            "project_id": self.phase.project.couch_id,
            "phase_id": self.phase.couch_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": 0,
            "sql_id": self.id,
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": self.couch_id})[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document["_id"]
            self.save()
        return self


# The task object on couch looks like this
# {
#   "_id": "d50db81ec709d67e3b1b299ba60f2666",
#   "_rev": "28-837510813494bd487a329b9d66e693f6",
#   "type": "task",
#   "project_id": "219e50bc41c65648039b08eb10e7b925",
#   "phase_id": "abc123",
#   "phase_name": "VISITES PREALABLES",
#   "activity_id": "219e50bc41c65648039b08eb10032af1",
#   "activity_name": "Réunion cantonale",
#   "administrative_level_id": "adml123",
#   "administrative_level_name": "Sanloaga",
#   "name": "Tarea 2",
#   "order": 2,
#   "description": "Lorem ipsum https://ee.kobotoolbox.org/x/HY43dHN4",
#   "completed": false,
#   "completed_date": "15-08-2022",
#   "capacity_attachments": [
#     {
#       "name": "Présentation du projet COSO.pdf",
#       "url": "https://drive.google.com/file/................."
#     },
#   ],
#   "support_attachments": true,
#   "attachments": [
#     {
#       "attachment": null,
#       "name": "Télécharger le PV de la séance",
#       "type": "image/jpeg",
#       "order": 0
#     },
#     {
#       "attachment": null,
#       "name": "Télécharger le programme des réunions d'arrondissement",
#       "type": "image/jpeg",
#       "order": 1
#     },
#     {
#       "attachment": null,
#       "name": "Photo de la réunion",
#       "type": "image/jpeg",
#       "order": 2
#     }
#   ],
#   "form": []
#   ...
# }
#
# "support_attachments" is not set by default and will
# be added manually before synching
#
# "attachments" by default is empty and need to be fill
# following the above example according to the given specifications
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    phase = models.ForeignKey("Phase", on_delete=models.CASCADE)
    activity = models.ForeignKey("Activity", on_delete=models.CASCADE)
    order = models.IntegerField()
    form = models.JSONField(null=True, blank=True)
    couch_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "tâche"

    def __str__(self):
        return self.phase.name + "-" + self.activity.name + "-" + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        form = []
        if self.form:
            form = self.form
        data = {
            "type": "task",
            "project_id": self.activity.phase.project.couch_id,
            "phase_id": self.activity.phase.couch_id,
            "phase_name": self.activity.phase.name,
            "activity_id": self.activity.couch_id,
            "activity_name": self.activity.name,
            "name": self.name,
            "order": self.order,
            "description": self.description,
            "completed": False,
            "completed_date": "",
            "capacity_attachments": [],
            "attachments": [],
            "form": form,
            "form_response": [],
            "sql_id": self.id,
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": self.couch_id})[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document["_id"]
            activity = Activity.objects.get(id=self.activity_id)
            activity.total_tasks = (
                Task.objects.filter(activity_id=activity.id).all().count()
            )
            activity.save()
            docu = {"total_tasks": activity.total_tasks}
            query_result = nsc_database.get_query_result(
                {"_id": self.activity.couch_id}
            )[:]
            doc = nsc_database[query_result[0]["_id"]]
            nsc.update_doc(nsc_database, doc["_id"], docu)
            self.save()

        return self


User = get_user_model()


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_creator",
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updater",
    )
    # is_deleted = models.Boolean(default=False)
    # deleted_on = models.DateTimeField(null=True)
    # deleted_by = models.ForeignKey(get_user_model(), null=True)

    class Meta:
        abstract = True

    def to_dict(self):
        """Return Dict representation of the model"""
        import pdb

        pdb.set_trace()
        # from process_manager.serializers import FormFieldSerializer
        # return FormFieldSerializer(self).data
        # from process_manager.serializers import BaseModelSerializer
        return BaseModelSerializer(self).data


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = "__all__"
        # exclude = ["created_on", ""]


# Create your models here.
class FormType(BaseModel):
    """
    Model representing a Form
    """

    name = models.CharField(
        blank=False,
        null=False,
        max_length=140,
        help_text=_("Unique name for the Model"),
    )
    description = models.TextField(
        blank=True, null=True, help_text=_("Description of the form")
    )
    couch_id = models.CharField(
        blank=True, null=True, max_length=140, help_text=_("Related Couchdb id")
    )

    def __str__(self):
        return "{0}".format(self.name)

    def _get_json_data(self):
        """https://stackoverflow.com/questions/3535977/can-model-properties-be-displayed-in-a-template"""
        # get FormFields
        fields = FormField.objects.filter(form=self)
        dct = []
        delete_keys = ["created_by", "updated_by"]
        for fld in fields:
            import pdb

            pdb.set_trace()
            dct.append(model_to_dict(fld, exclude=delete_keys))
        return str(dct)

    json_data = property(_get_json_data)


class FormField(BaseModel):
    """
    Model representing a column/field in a FormType
    """

    FIELD_TYPES = []
    for itm in FieldTypeEnum:
        FIELD_TYPES.append((itm.value, itm.value))

    form = models.ForeignKey(FormType, on_delete=models.CASCADE)
    name = models.CharField(
        blank=False,
        null=False,
        max_length=140,
        help_text=_("Unique identifier for the field"),
    )
    label = models.CharField(
        blank=False, null=False, max_length=140, help_text=_("Field Label")
    )
    field_type = models.CharField(
        blank=False,
        null=False,
        max_length=140,
        choices=FIELD_TYPES,
        help_text=_("Type of field"),
    )

    def to_dict2(self):
        """Return Dict representation of the model"""
        import pdb

        pdb.set_trace()
        # from process_manager.serializers import FormFieldSerializer
        # return FormFieldSerializer(self).data
        from process_manager.serializers import BaseModelSerializer

        return BaseModelSerializer(self).data

    # options = models.TextField(help_text=_("For Select, enter list of Options, each on a new line."))
    # default = models.TextField(help_text=_("Default value for the field"))
    # description = models.TextField(help_text=_("Text to be displayed as help"))
    # mandatory = models.BooleanField(help_text=_("Is the field mandatory"))
    # hidden = models.BooleanField(help_text=_("Is the field hidden?"))
    # read_only = models.BooleanField(help_text=_("Is the field read-only?"))
