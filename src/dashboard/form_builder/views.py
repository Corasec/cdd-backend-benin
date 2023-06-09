from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy
from django.shortcuts import redirect, get_list_or_404
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient
from process_manager.models import FormType, FormField
from dashboard.form_builder.forms import (
    FormTypeForm,
    UpdateFormTypeForm,
    FormFieldFormSet,
)
from django.forms.models import inlineformset_factory
from django.contrib import messages

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class FormTypeListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = FormType
    queryset = FormType.objects.all()
    template_name = "form_builder/form/list.html"
    context_object_name = "forms"
    title = gettext_lazy("Forms")
    breadcrumb = [{"url": "", "title": title}]

    def get_queryset(self):
        return super().get_queryset()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['form'] = FormTypeForm()
    #     return context


class FormTypeListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "form_builder/form/form_list.html"
    context_object_name = "forms"

    def get_results(self):
        return list(FormType.objects.all())

    def get_queryset(self):
        return self.get_results()


# class FormTypeListView_OLD(PageMixin, LoginRequiredMixin, generic.ListView):
#     model = FormType
#     queryset = FormType.objects.all()
#     template_name = 'form_builder/form_type/list.html'
#     context_object_name = 'forms'
#     title = gettext_lazy('Forms')
#     breadcrumb = [{
#             'url': '',
#             'title': title
#         }]

#     def get_queryset(self):
#         return super().get_queryset()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = FormTypeForm()
#         return context


class FormFieldListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = FormType
    queryset = FormType.objects.all()
    template_name = "form_builder/form_field/list.html"
    context_object_name = "forms"
    title = gettext_lazy("Form Types")
    breadcrumb = [{"url": "", "title": title}]

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FormTypeForm()
        return context


class FormTypeInline:
    """
    See https://www.letscodemore.com/blog/django-inline-formset-factory-with-examples/
    """

    form_class = FormTypeForm
    model = FormType
    template_name = "form_builder/form/create.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function. If not found, just save
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, "formset_{0}_valid".format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect("dashboard:form_builder:list")

    def formset_form_fields_valid(self, formset):
        """
        Hook for custom formset saving. It is useful if you have multiple formsets
        So in case you have another formset, just declare another formset_{FORMSET}_valid method
        """
        form_fields = formset.save(commit=False)
        # add this 2 lines, if you have can_delete=True parameter
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for form_field in form_fields:
            # assign parent
            form_field.form = self.object
            form_field.save()


class CreateFormTypeView(
    FormTypeInline,
    PageMixin,
    LoginRequiredMixin,
    AdminPermissionRequiredMixin,
    generic.FormView,
):
    """
    See https://swapps.com/blog/working-with-nested-forms-with-django/
    https://www.imagescape.com/blog/multipage-forms-django/
    https://www.letscodemore.com/blog/django-inline-formset-factory-with-examples/
    """

    template_name = "form_builder/form/create.html"
    title = gettext_lazy("Create Form Type")
    active_level1 = "forms"
    form_class = FormTypeForm
    success_url = reverse_lazy("dashboard:form_builder:list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:form_builder:list"),
            "title": gettext_lazy("Form Types"),
        },
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        ctx = super(CreateFormTypeView, self).get_context_data(**kwargs)
        ctx["named_formsets"] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        """
        If there are multiple formsets, you would extend the dictionary
        """
        if self.request.method == "GET":
            return {"form_fields": FormFieldFormSet(prefix="form_fields")}
        else:
            return {
                "form_fields": FormFieldFormSet(
                    self.request.POST or None, prefix="form_fields"
                )
            }
        # if self.request.POST:
        #     data['fields'] = FormFieldSet(self.request.POST)
        # else:
        #     data['fields'] = FormFieldSet()
        # return data # super().get_context_data(**kwargs)

    # def form_valid(self, form):
    #     context = self.get_context_data()
    #     children = context["fields"]
    #     self.object = form.save()
    #     if children.is_valid():
    #         children.instance = self.object
    #         children.save()
    #     return super().form_valid(form)

    # def form_valid_old(self, form):
    #     data = form.cleaned_data
    #     form_fields = []
    #     if data['fields']:
    #         form_fields = data['fields']
    #     my_form = FormType(
    #         name=data['name'],
    #         is_generic=data['is_generic'],
    #         content_type=data['content_type'],
    #         content_object=data['content_object']
    #     )
    #     my_form.save()
    #     return super().form_valid(my_form)


class CreateFormTypeView_OLD(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    """
    See https://swapps.com/blog/working-with-nested-forms-with-django/
    https://www.imagescape.com/blog/multipage-forms-django/
    https://www.letscodemore.com/blog/django-inline-formset-factory-with-examples/
    """

    template_name = "form_builder/form/create.html"
    title = gettext_lazy("Create Form")
    active_level1 = "forms"
    form_class = FormTypeForm
    success_url = reverse_lazy("dashboard:form_builder:form_list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:form_builder:form_list"),
            "title": gettext_lazy("Forms"),
        },
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        FormFieldSet = inlineformset_factory(
            FormType,
            FormField,
            fields=[
                "name",
            ],
        )
        if self.request.POST:
            data["fields"] = FormFieldSet(self.request.POST)
        else:
            data["fields"] = FormFieldSet()
        return data  # super().get_context_data(**kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        children = context["fields"]
        self.object = form.save()
        if children.is_valid():
            children.instance = self.object
            children.save()
        return super().form_valid(form)

    def form_valid_old(self, form):
        data = form.cleaned_data
        form_fields = []
        if data["fields"]:
            form_fields = data["fields"]
        form_type = FormType(
            name=data["name"],
            is_generic=data["is_generic"],
            content_type=data["content_type"],
            content_object=data["content_object"],
        )
        form_type.save()
        return super().form_valid(form)


class UpdateFormTypeView(
    FormTypeInline,
    PageMixin,
    LoginRequiredMixin,
    AdminPermissionRequiredMixin,
    generic.UpdateView,
):
    model = FormType
    template_name = "form_builder/form/update.html"
    title = gettext_lazy("Edit Form")
    active_level1 = "forms"
    form_class = UpdateFormTypeForm
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:form_builder:list"),
            "title": gettext_lazy("Forms"),
        },
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        ctx = super(UpdateFormTypeView, self).get_context_data(**kwargs)
        ctx["named_formsets"] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        """
        If there are multiple formsets, you would extend the dictionary
        """
        return {
            "form_fields": FormFieldFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="form_fields",
            )
        }


class UpdateFormTypeView_OLD(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = FormType
    template_name = "form_builder/form/update.html"
    title = gettext_lazy("Edit Form Type")
    active_level1 = "forms"
    form_class = UpdateFormTypeForm
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:form_builder:list_form"),
            "title": gettext_lazy("Forms"),
        },
        {"url": "", "title": title},
    ]


# class FormTypeMixin:
#     doc = None
#     obj = None
#     db = None
#     db_name = None
#     content_type = None #Type of data that we should pull

#     def dispatch(self, *args, **kwargs):
#         nsc = NoSQLClient()
#         try:
#             self.db_name = kwargs["id"]
#             self.content_type = kwargs["ctype"]
#             self.db = nsc.get_db(self.db_name)
#             query_result = self.db.get_query_result({"type": self.content_type})
#         except Exception:
#             raise Http404


def delete_formfield(request, pk):
    """This functions is for custom added delete button functionality. If you don't want to use custom delete buttons than don't add this"""
    try:
        form_field = FormField.objects.get(id=pk)
    except FormField.DoesNotExist:
        messages.success(request, gettext_lazy("Object does not exist"))
        return redirect(
            "dashboard:form_builder:update_form_type", pk=form_field.form_type.id
        )

    form_field.delete()
    messages.success(request, gettext_lazy("Form deleted successfully"))
    return redirect(
        "dashboard:form_builder:update_form_type", pk=form_field.form_type.id
    )
