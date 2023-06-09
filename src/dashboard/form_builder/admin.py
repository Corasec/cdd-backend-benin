from django.contrib import admin
from form_builder.models import DocField, DocType


# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    """
    Base class for model admins
    """

    readonly_fields = ("created_on", "created_by", "updated_on", "updated_by")


class DocFieldInline(admin.TabularInline, BaseModelAdmin):
    """
    DocField handling for admin interface
    """

    model = DocField
    extra = 1


class DocTypeAdmin(BaseModelAdmin):
    """
    DocField handling for admin interface
    """

    fieldsets = [
        (None, {"fields": ["name"]}),
        #  ('Fields', {'fields': []})
    ]
    inlines = [DocFieldInline]
