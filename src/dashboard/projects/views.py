from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from datetime import datetime
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from process_manager.models import Project
from dashboard.projects.forms import ProjectForm, UpdateProjectForm
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class ProjectMixin:
    doc = None
    obj = None
    project_db = None
    project_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.project_db_name = kwargs["id"]
            self.project_db = nsc.get_db(self.project_db_name)
            query_result = self.project_db.get_query_result({"type": "project"})[:]
            self.doc = self.project_db[query_result[0]["_id"]]
            self.obj = get_object_or_404(Project, no_sql_db_name=kwargs["id"])
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class ProjectListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Project
    queryset = Project.objects.all()
    template_name = "projects/list.html"
    context_object_name = "projects"
    title = gettext_lazy("Projects")
    active_level1 = "projects"
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return super().get_queryset()


class ProjectListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "projects/project_list.html"
    context_object_name = "projects"

    def get_results(self):
        projects = []
        projects = list(Project.objects.all())
        print("language : ", self.request.LANGUAGE_CODE == "fr")
        return projects

    def get_queryset(self):
        return self.get_results()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class CreateProjectFormView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "projects/create.html"
    title = gettext_lazy("Create Project")
    active_level1 = "projects"
    form_class = ProjectForm
    success_url = reverse_lazy("dashboard:projects:list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:projects:list"),
            "title": gettext_lazy("Projects"),
        },
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        project = Project(name=data["name"], description=data["description"])
        project.save()
        return super().form_valid(form)


class UpdateProjectView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = Project
    template_name = "projects/update.html"
    title = gettext_lazy("Edit Project")
    active_level1 = "projects"
    form_class = UpdateProjectForm
    # success_url = reverse_lazy('dashboard:projects:list')
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:projects:list"),
            "title": gettext_lazy("Projects"),
        },
        {"url": "", "title": title},
    ]

    project_db = None
    project = None
    doc = None
    project_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.project = self.get_object()
            self.project_db_name = "process_design"
            self.project_db = nsc.get_db(self.project_db_name)
            query_result = self.project_db.get_query_result({"type": "project"})[:]
            self.doc = self.project_db[query_result[0]["_id"]]
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateProjectView, self).get_context_data(**kwargs)
        form = ctx.get("form")
        ctx.setdefault("project_doc", self.doc)
        if self.doc:
            if form:
                for label, field in form.fields.items():
                    try:
                        form.fields[label].value = self.doc[label]
                    except Exception as exc:
                        pass

                ctx.setdefault("form", form)

        return ctx

    def post(self, request, *args, **kwargs):
        if not self.project_db_name:
            raise Http404("We don't find the database name for the project.")

        form = UpdateProjectForm(request.POST, instance=self.project)
        if form.is_valid():
            return self.form_valid(form)
        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        project = form.save(commit=False)
        project.name = data["name"]
        project.description = data["description"]
        project.couch_id = data["couch_id"]
        project.save()
        doc = {
            "name": data["name"],
            "type": "project",
            "description": data["description"],
            "sql_id": project.id,
        }
        nsc = NoSQLClient()
        query_result = self.project_db.get_query_result(
            {"type": "project", "_id": project.couch_id}
        )[:]
        self.doc = self.project_db[query_result[0]["_id"]]
        nsc.update_doc(self.project_db, self.doc["_id"], doc)
        return redirect("dashboard:projects:list")


class ProjectDetailView(
    ProjectMixin, PageMixin, LoginRequiredMixin, generic.DetailView
):
    template_name = "projects/detail.html"
    context_object_name = "project_doc"
    title = gettext_lazy("Project Detail")
    active_level1 = "projects"
    model = Project
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:projects:list"),
            "title": gettext_lazy("Projects"),
        },
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.obj

        project_docs = self.project_db.all_docs(include_docs=True)["rows"]
        for doc in project_docs:
            doc = doc.get("doc")
        return context

    def get_object(self, queryset=None):
        return self.doc


def update(request, id):
    project = Project.objects.get(id=id)
    template = loader.get_template("projects/update.html")
    context = {
        "project": project,
    }
    return HttpResponse(template.render(context, request))


def updaterecord(request, id):
    name = request.POST["name"]
    description = request.POST["description"]
    couch_id = request.POST["couch_id"]

    project = Project.objects.get(id=id)
    project.name = name
    project.description = description
    project.couch_id = couch_id
    project.save()
    doc = None
    _id = couch_id
    doc = {
        "name": project.name,
        "type": "project",
        "description": request.POST["description"],
        "sql_id": project.id,
    }
    try:
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        query_result = nsc_database.get_query_result({"type": "project"})[:]
        doc = nsc_database[query_result[0]["_id"]]
        nsc.update_doc(nsc_database, doc["_id"], doc)
    except Exception:
        raise Http404
    return redirect("dashboard:projects:list")


def delete(request, id):
    project = Project.objects.get(id=id)

    if request.method == "POST":
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": project.couch_id})[0]
        if new_document:
            nsc.delete_document(nsc_database, project.couch_id)
            project.delete()

            return redirect("dashboard:projects:list")

    return render(request, "projects/project_confirm_delete.html", {"project": project})
