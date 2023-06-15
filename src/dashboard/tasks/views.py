from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import generic
from datetime import datetime

from process_manager.models import Phase, Activity, Project, Task
from dashboard.tasks.forms import TaskForm, UpdateTaskForm
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class TaskListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Task
    queryset = Task.objects.all()
    template_name = "tasks/list.html"
    context_object_name = "tasks"
    title = gettext_lazy("Tâches")
    active_level1 = "tasks"
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return super().get_queryset()


class TaskListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_results(self):
        tasks = []
        tasks = list(Task.objects.all())
        return tasks

    def get_queryset(self):
        return self.get_results()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class CreateTaskFormView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "tasks/create.html"
    title = gettext_lazy("Create Task")
    active_level1 = "tasks"
    form_class = TaskForm
    success_url = reverse_lazy("dashboard:tasks:list")
    breadcrumb = [
        {"url": reverse_lazy("dashboard:tasks:list"), "title": gettext_lazy("Tasks")},
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        # project = Project.objects.get(id = data['project'])
        # phase = Phase.objects.get(id = data['phase'])
        activity = Activity.objects.get(id=data["activity"])
        form = []
        if data["form"]:
            form = data["form"]
        task = Task(
            name=data["name"],
            description=data["description"],
            project=activity.phase.project,
            phase=activity.phase,
            activity=activity,
            order=data["order"],
            form=form,
        )
        task.save()
        return super().form_valid(form)


def delete(request, id):
    task = Task.objects.get(id=id)
    activity_id = task.activity.id
    if request.method == "POST":
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result({"_id": task.couch_id})[0]
        if new_document:
            activity = Activity.objects.get(id=task.activity_id)
            docu = {"total_tasks": activity.total_tasks}
            query_result = nsc_database.get_query_result(
                {"_id": task.activity.couch_id}
            )[:]
            doc = nsc_database[query_result[0]["_id"]]
            nsc.update_doc(nsc_database, doc["_id"], docu)
            nsc.delete_document(nsc_database, task.couch_id)
            task.delete()
            activity.total_tasks = (
                Task.objects.filter(activity_id=activity.id).all().count()
            )
            activity.save()
            tasks = list(Task.objects.filter(activity_id=activity_id))
            return render(
                request,
                "activities/activity_detail.html",
                context={"activity": activity, "tasks": tasks},
            )

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


class UpdateTaskView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = Task
    template_name = "tasks/update.html"
    title = gettext_lazy("Edit Task")
    active_level1 = "tasks"
    form_class = UpdateTaskForm
    # success_url = reverse_lazy('dashboard:projects:list')
    breadcrumb = [
        {"url": reverse_lazy("dashboard:tasks:list"), "title": gettext_lazy("Tasks")},
        {"url": "", "title": title},
    ]

    task_db = None
    task = None
    doc = None
    task_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.task = self.get_object()
            self.task_db_name = "process_design"
            self.task_db = nsc.get_db(self.task_db_name)
            query_result = self.task_db.get_query_result({"type": "task"})[:]
            self.doc = self.task_db[query_result[0]["_id"]]
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateTaskView, self).get_context_data(**kwargs)
        form = ctx.get("form")
        ctx.setdefault("task_doc", self.doc)
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
        if not self.task_db_name:
            raise Http404("We don't find the database name for the Task.")

        form = UpdateTaskForm(request.POST, instance=self.task)
        if form.is_valid():
            return self.form_valid(form)
        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        task = form.save(commit=False)
        task.name = data["name"]
        task.description = data["description"]
        task.save()
        doc = {
            "name": data["name"],
            "description": data["description"],
            "sql_id": task.id,
        }
        nsc = NoSQLClient()
        query_result = self.task_db.get_query_result({"_id": task.couch_id})[:]
        self.doc = self.task_db[query_result[0]["_id"]]
        nsc.update_doc(self.task_db, self.doc["_id"], doc)

        activity = Activity.objects.get(id=task.activity_id)
        tasks = list(
            Task.objects.filter(activity_id=task.activity_id).order_by("order")
        )
        # return redirect('dashboard:tasks:list')
        return render(
            self.request,
            "activities/activity_detail.html",
            context={"activity": activity, "tasks": tasks},
        )


class CreateTaskForm(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "tasks/create_task.html"
    title = gettext_lazy("Create Task")
    active_level1 = "tasks"
    form_class = TaskForm
    success_url = reverse_lazy("dashboard:tasks:list")
    breadcrumb = [
        {"url": reverse_lazy("dashboard:tasks:list"), "title": gettext_lazy("Tasks")},
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        # project = Project.objects.get(id = data['project'])
        pk = self.kwargs["id"]
        activity = Activity.objects.get(id=pk)
        form = []
        # if data['form']:
        # form = data['form']
        task = Task(
            name=data["name"],
            description=data["description"],
            project=activity.phase.project,
            phase=activity.phase,
            activity=activity,
            form=form,
        )
        task_count = 0
        task_count = Task.objects.filter(activity_id=activity.id).all().count()
        orderNew = task_count + 1
        task.order = orderNew
        task.save()

        activity = Activity.objects.get(id=task.activity_id)
        tasks = list(
            Task.objects.filter(activity_id=task.activity_id).order_by("order")
        )
        return render(
            self.request,
            "activities/activity_detail.html",
            context={"activity": activity, "tasks": tasks},
        )
        # return super().form_valid(form)


def task_detail_view(request, id):
    try:
        task = Task.objects.get(id=id)
        # tasks = list(Task.objects.filter(activity_id = activity.id))
    except Activity.DoesNotExist:
        raise Http404("Activity does not exist")

    return render(request, "tasks/task_detail.html", context={"task": task})


def changeOrderUp(request, id):
    task = Task.objects.get(id=id)
    if task:
        taskPrev = Task.objects.filter(order__lt=task.order).order_by("order").last()
        if taskPrev:
            if task.order > 0:
                if task.order == 1:
                    exit
                else:
                    if taskPrev.order == task.order:
                        task.order = task.order - 1
                        taskPrev.order = taskPrev.order
                    else:
                        task.order = task.order - 1
                        taskPrev.order = taskPrev.order + 1
            taskPrev.save()
            task.save()
            doc = {"order": task.order}
            docPrev = {"order": taskPrev.order}
            nsc = NoSQLClient()
            task_db = nsc.get_db("process_design")
            query_result = task_db.get_query_result({"_id": task.couch_id})[:]
            query_result_prev = task_db.get_query_result({"_id": taskPrev.couch_id})[:]
            docu = task_db[query_result[0]["_id"]]
            docPrevU = task_db[query_result_prev[0]["_id"]]
            nsc.update_doc(task_db, docu["_id"], doc)
            nsc.update_doc(task_db, docPrevU["_id"], docPrev)
        else:
            if task.order > 0:
                if task.order == 1:
                    exit
                else:
                    task.order = task.order - 1
                    task.save()
                    doc = {"order": task.order}
                    nsc = NoSQLClient()
                    task_db = nsc.get_db("process_design")
                    query_result = task_db.get_query_result({"_id": task.couch_id})[:]
                    docu = task_db[query_result[0]["_id"]]
                    nsc.update_doc(task_db, docu["_id"], doc)

    activity = Activity.objects.get(id=task.activity.id)
    tasks = list(Task.objects.filter(activity_id=activity.id).order_by("order"))

    return render(
        request,
        "activities/activity_detail.html",
        context={"activity": activity, "tasks": tasks},
    )


def changeOrderDown(request, id):
    task = Task.objects.get(id=id)
    task_count = Task.objects.filter(activity_id=task.activity_id).all().count()
    if task:
        taskNext = Task.objects.filter(order__gt=task.order).order_by("order").first()
        if taskNext:
            if taskNext.order > 0:
                if taskNext.order == 1:
                    task.order = task.order + 1
                else:
                    if task.order < task_count:
                        task.order = task.order + 1
                    taskNext.order = taskNext.order - 1
            taskNext.save()
            task.save()
            doc = {"order": task.order}
            docNext = {"order": taskNext.order}
            nsc = NoSQLClient()
            task_db = nsc.get_db("process_design")
            query_result = task_db.get_query_result({"_id": task.couch_id})[:]
            query_result_next = task_db.get_query_result({"_id": taskNext.couch_id})[:]
            docu = task_db[query_result[0]["_id"]]
            docNextU = task_db[query_result_next[0]["_id"]]
            nsc.update_doc(task_db, docu["_id"], doc)
            nsc.update_doc(task_db, docNextU["_id"], docNext)
        else:
            if task.order < task_count:
                task.order = task.order + 1
                task.save()
                doc = {"order": task.order}
                nsc = NoSQLClient()
                task_db = nsc.get_db("process_design")
                query_result = task_db.get_query_result({"_id": task.couch_id})[:]
                docu = task_db[query_result[0]["_id"]]
                nsc.update_doc(task_db, docu["_id"], doc)

    activity = Activity.objects.get(id=task.activity.id)
    tasks = list(Task.objects.filter(activity_id=activity.id).order_by("order"))

    return render(
        request,
        "activities/activity_detail.html",
        context={"activity": activity, "tasks": tasks},
    )
