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
from dashboard.activities.forms import ActivityForm, UpdateActivityForm
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class ActivityListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Activity
    queryset = Activity.objects.all()
    template_name = "activities/list.html"
    context_object_name = "activities"
    title = gettext_lazy("Activities")
    active_level1 = "activities"
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return super().get_queryset()


class ActivityListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "activities/activity_list.html"
    context_object_name = "activities"

    def get_results(self):
        activities = []
        activities = list(Activity.objects.all())
        return activities

    def get_queryset(self):
        return self.get_results()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class CreateActivityFormView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "activities/create.html"
    title = gettext_lazy("Create Activity")
    active_level1 = "activities"
    form_class = ActivityForm
    success_url = reverse_lazy("dashboard:activities:list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:activities:list"),
            "title": gettext_lazy("Phases"),
        },
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        # project = Project.objects.get(id = data['project'])
        phase = Phase.objects.get(id=data["phase"])
        activity = Activity(
            name=data["name"],
            description=data["description"],
            project=phase.project,
            phase=phase,
            total_tasks=data["total_tasks"],
            order=data["order"],
        )
        activity.save()
        return super().form_valid(form)


class CreateActivityForm(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "activities/create_activity.html"
    title = gettext_lazy("Create Activity")
    active_level1 = "activities"
    form_class = ActivityForm
    success_url = reverse_lazy("dashboard:activities:list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:activities:list"),
            "title": gettext_lazy("Phases"),
        },
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        # project = Project.objects.get(id = data['project'])
        pk = self.kwargs["id"]
        phase = Phase.objects.get(id=pk)
        activity = Activity(
            name=data["name"],
            description=data["description"],
            project=phase.project,
            phase=phase,
            total_tasks=0,
        )
        activity_count = 0
        activity_count = Activity.objects.filter(phase_id=phase.id).all().count()
        orderNew = activity_count + 1
        activity.order = orderNew
        activity.save()
        # return super().form_valid(form)
        phase = Phase.objects.get(id=activity.phase_id)
        activities = list(Activity.objects.filter(phase_id=phase.id).order_by("order"))

        return render(
            self.request,
            "phases/phase_detail.html",
            context={"phase": phase, "activities": activities},
        )


def delete(request, id):
    activity = Activity.objects.get(id=id)
    all_task = Task.objects.filter(activity_id=activity.id).all()
    phase_id = activity.phase.id
    if request.method == "POST":
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        for task in all_task:
            task_document = nsc_database.get_query_result({"_id": task.couch_id})[0]
            if task_document:
                nsc.delete_document(nsc_database, task.couch_id)

        new_document = nsc_database.get_query_result({"_id": activity.couch_id})[0]
        if new_document:
            nsc.delete_document(nsc_database, activity.couch_id)
            activity.delete()
            activities = list(
                Activity.objects.filter(phase_id=phase_id).order_by("order")
            )
            phase = Phase.objects.get(id=phase_id)

            return render(
                request,
                "phases/phase_detail.html",
                context={"phase": phase, "activities": activities},
            )

    return render(
        request, "activities/activity_confirm_delete.html", {"activity": activity}
    )


class UpdateActivityView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = Activity
    template_name = "activities/update.html"
    title = gettext_lazy("Edit Activity")
    active_level1 = "activities"
    form_class = UpdateActivityForm
    # success_url = reverse_lazy('dashboard:projects:list')
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:activities:list"),
            "title": gettext_lazy("Activities"),
        },
        {"url": "", "title": title},
    ]

    activity_db = None
    activity = None
    doc = None
    activity_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.activity = self.get_object()
            self.activity_db_name = "process_design"
            self.activity_db = nsc.get_db(self.activity_db_name)
            query_result = self.activity_db.get_query_result({"type": "activity"})[:]
            self.doc = self.activity_db[query_result[0]["_id"]]
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateActivityView, self).get_context_data(**kwargs)
        form = ctx.get("form")
        ctx.setdefault("activity_doc", self.doc)
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
        if not self.activity_db_name:
            raise Http404("We don't find the database name for the Activity.")

        form = UpdateActivityForm(request.POST, instance=self.activity)
        if form.is_valid():
            return self.form_valid(form)
        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        activity = form.save(commit=False)
        activity.name = data["name"]
        activity.description = data["description"]
        # activity.phase = data['phase']
        # activity.project = activity.phase.project
        # activity.total_tasks = data['total_tasks']
        # activity.order = data['order']
        activity.save()
        doc = {
            "name": data["name"],
            "description": data["description"],
            "sql_id": activity.id,
        }
        nsc = NoSQLClient()
        query_result = self.activity_db.get_query_result({"_id": activity.couch_id})[:]
        self.doc = self.activity_db[query_result[0]["_id"]]
        nsc.update_doc(self.activity_db, self.doc["_id"], doc)
        phase = Phase.objects.get(id=activity.phase_id)
        activities = list(
            Activity.objects.filter(phase_id=activity.phase_id).order_by("order")
        )
        # return redirect('dashboard:activities:list')
        return render(
            self.request,
            "phases/phase_detail.html",
            context={"phase": phase, "activities": activities},
        )
        # return redirect('dashboard:phases:phase_detail', activity.phase.id)


def activity_detail_view(request, id):
    try:
        activity = Activity.objects.get(id=id)
        tasks = list(Task.objects.filter(activity_id=activity.id).order_by("order"))
    except Activity.DoesNotExist:
        raise Http404("Activity does not exist")

    return render(
        request,
        "activities/activity_detail.html",
        context={"activity": activity, "tasks": tasks},
    )


def changeOrderUp(request, id):
    activity = Activity.objects.get(id=id)
    if activity:
        activityPrev = (
            Activity.objects.filter(order__lt=activity.order).order_by("order").last()
        )
        if activityPrev:
            if activity.order > 0:
                if activity.order == 1:
                    exit
                else:
                    if activityPrev.order == activity.order:
                        activity.order = activity.order - 1
                        activityPrev.order = activityPrev.order
                    else:
                        activity.order = activity.order - 1
                        activityPrev.order = activityPrev.order + 1
            activityPrev.save()
            activity.save()
            doc = {"order": activity.order}
            docPrev = {"order": activityPrev.order}
            nsc = NoSQLClient()
            activity_db = nsc.get_db("process_design")
            query_result = activity_db.get_query_result({"_id": activity.couch_id})[:]
            query_result_prev = activity_db.get_query_result(
                {"_id": activityPrev.couch_id}
            )[:]
            docu = activity_db[query_result[0]["_id"]]
            docPrevU = activity_db[query_result_prev[0]["_id"]]
            nsc.update_doc(activity_db, docu["_id"], doc)
            nsc.update_doc(activity_db, docPrevU["_id"], docPrev)
        else:
            if activity.order > 0:
                if activity.order == 1:
                    exit
                else:
                    activity.order = activity.order - 1
                    activity.save()
                    doc = {"order": activity.order}
                    nsc = NoSQLClient()
                    activity_db = nsc.get_db("process_design")
                    query_result = activity_db.get_query_result(
                        {"_id": activity.couch_id}
                    )[:]
                    docu = activity_db[query_result[0]["_id"]]
                    nsc.update_doc(activity_db, docu["_id"], doc)

    phase = Phase.objects.get(id=activity.phase.id)
    activities = list(Activity.objects.filter(phase_id=phase.id).order_by("order"))
    return render(
        request,
        "phases/phase_detail.html",
        context={"phase": phase, "activities": activities},
    )


def changeOrderDown(request, id):
    activity = Activity.objects.get(id=id)
    activity_count = Activity.objects.filter(phase_id=activity.phase_id).all().count()
    if activity:
        activityNext = (
            Activity.objects.filter(order__gt=activity.order).order_by("order").first()
        )
        if activityNext:
            if activityNext.order > 0:
                if activityNext.order == 1:
                    activity.order = activity.order + 1
                else:
                    if activity.order < activity_count:
                        activity.order = activity.order + 1
                    activityNext.order = activityNext.order - 1
            activityNext.save()
            activity.save()
            doc = {"order": activity.order}
            docNext = {"order": activityNext.order}
            nsc = NoSQLClient()
            activity_db = nsc.get_db("process_design")
            query_result = activity_db.get_query_result({"_id": activity.couch_id})[:]
            query_result_next = activity_db.get_query_result(
                {"_id": activityNext.couch_id}
            )[:]
            docu = activity_db[query_result[0]["_id"]]
            docNextU = activity_db[query_result_next[0]["_id"]]
            nsc.update_doc(activity_db, docu["_id"], doc)
            nsc.update_doc(activity_db, docNextU["_id"], docNext)
        else:
            if activity.order < activity_count:
                activity.order = activity.order + 1
                activity.save()
                doc = {"order": activity.order}
                nsc = NoSQLClient()
                activity_db = nsc.get_db("process_design")
                query_result = activity_db.get_query_result({"_id": activity.couch_id})[
                    :
                ]
                docu = activity_db[query_result[0]["_id"]]
                nsc.update_doc(activity_db, docu["_id"], doc)

    phase = Phase.objects.get(id=activity.phase.id)
    activities = list(Activity.objects.filter(phase_id=phase.id).order_by("order"))

    return render(
        request,
        "phases/phase_detail.html",
        context={"phase": phase, "activities": activities},
    )
