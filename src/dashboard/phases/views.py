from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import generic
from datetime import datetime

from process_manager.models import Phase, Project, Activity, Task
from dashboard.phases.forms import PhaseForm, UpdatePhaseForm
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class PhaseListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Phase
    queryset = Phase.objects.all()
    template_name = "phases/list.html"
    context_object_name = "phases"
    title = gettext_lazy("Phases")
    active_level1 = "phases"
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return super().get_queryset()


class PhaseListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "phases/phase_list.html"
    context_object_name = "phases"

    def get_results(self):
        phases = []
        phases = list(Phase.objects.all().order_by("order"))
        self.maxOrder = len(phases)
        return phases

    def get_queryset(self):
        return self.get_results()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maxOrder"] = self.maxOrder
        return context


class CreatePhaseFormView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "phases/create.html"
    title = gettext_lazy("Create Phase")
    active_level1 = "phases"
    form_class = PhaseForm
    success_url = reverse_lazy("dashboard:phases:list")
    breadcrumb = [
        {"url": reverse_lazy("dashboard:phases:list"), "title": gettext_lazy("Phases")},
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        project = Project.objects.first()
        phase_count = 0
        phase_count = Phase.objects.all().count()
        orderNew = phase_count + 1
        phase = Phase(
            name=data["name"],
            description=data["description"],
            project=project,
            order=orderNew,
        )
        phase.save()
        return super().form_valid(form)


def delete(request, id):
    phase = Phase.objects.get(id=id)
    all_activity = Activity.objects.filter(phase_id=phase.id).all()
    if request.method == "POST":
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        for act in all_activity:
            all_task = Task.objects.filter(activity_id=act.id).all()
            for tas in all_task:
                task_document = nsc_database.get_query_result({"_id": tas.couch_id})[0]
                if task_document:
                    nsc.delete_document(nsc_database, tas.couch_id)
            actvity_document = nsc_database.get_query_result({"_id": act.couch_id})[0]
            if actvity_document:
                nsc.delete_document(nsc_database, act.couch_id)
        del_document = nsc_database.get_query_result({"_id": phase.couch_id})[0]
        if del_document:
            nsc.delete_document(nsc_database, phase.couch_id)
            phase.delete()

            return redirect("dashboard:phases:list")

    return render(request, "phases/phase_confirm_delete.html", {"phase": phase})


def changeOrderUp(request, id):
    phase = Phase.objects.get(id=id)
    if phase:
        phasePrev = Phase.objects.filter(order__lt=phase.order).order_by("order").last()
        if phasePrev:
            if phase.order > 0:
                if phase.order == 1:
                    exit
                else:
                    if phasePrev.order == phase.order:
                        phase.order = phase.order - 1
                        phasePrev.order = phasePrev.order
                    else:
                        phase.order = phase.order - 1
                        phasePrev.order = phasePrev.order + 1
            phasePrev.save()
            phase.save()
            doc = {"order": phase.order}
            docPrev = {"order": phasePrev.order}
            nsc = NoSQLClient()
            phase_db = nsc.get_db("process_design")
            query_result = phase_db.get_query_result({"_id": phase.couch_id})[:]
            query_result_prev = phase_db.get_query_result({"_id": phasePrev.couch_id})[
                :
            ]
            docu = phase_db[query_result[0]["_id"]]
            docPrevU = phase_db[query_result_prev[0]["_id"]]
            nsc.update_doc(phase_db, docu["_id"], doc)
            nsc.update_doc(phase_db, docPrevU["_id"], docPrev)
        else:
            if phase.order > 0:
                if phase.order == 1:
                    exit
                else:
                    phase.order = phase.order - 1
                    phase.save()
                    doc = {"order": phase.order}
                    nsc = NoSQLClient()
                    phase_db = nsc.get_db("process_design")
                    query_result = phase_db.get_query_result({"_id": phase.couch_id})[:]
                    docu = phase_db[query_result[0]["_id"]]
                    nsc.update_doc(phase_db, docu["_id"], doc)
    return redirect("dashboard:phases:list")


def changeOrderDown(request, id):
    phase = Phase.objects.get(id=id)
    phase_count = Phase.objects.all().count()
    if phase:
        phaseNext = (
            Phase.objects.filter(order__gt=phase.order).order_by("order").first()
        )
        if phaseNext:
            if phaseNext.order > 0:
                if phaseNext.order == 1:
                    phase.order = phase.order + 1
                else:
                    if phase.order < phase_count:
                        phase.order = phase.order + 1
                    phaseNext.order = phaseNext.order - 1
            phaseNext.save()
            phase.save()
            doc = {"order": phase.order}
            docNext = {"order": phaseNext.order}
            nsc = NoSQLClient()
            phase_db = nsc.get_db("process_design")
            query_result = phase_db.get_query_result({"_id": phase.couch_id})[:]
            query_result_next = phase_db.get_query_result({"_id": phaseNext.couch_id})[
                :
            ]
            docu = phase_db[query_result[0]["_id"]]
            docNextU = phase_db[query_result_next[0]["_id"]]
            nsc.update_doc(phase_db, docu["_id"], doc)
            nsc.update_doc(phase_db, docNextU["_id"], docNext)
        else:
            if phase.order < phase_count:
                phase.order = phase.order + 1
                phase.save()
                doc = {"order": phase.order}
                nsc = NoSQLClient()
                phase_db = nsc.get_db("process_design")
                query_result = phase_db.get_query_result({"_id": phase.couch_id})[:]
                docu = phase_db[query_result[0]["_id"]]
                nsc.update_doc(phase_db, docu["_id"], doc)
    return redirect("dashboard:phases:list")


class UpdatePhaseView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = Phase
    template_name = "phases/update.html"
    title = gettext_lazy("Edit Phase")
    active_level1 = "phases"
    form_class = UpdatePhaseForm
    # success_url = reverse_lazy('dashboard:projects:list')
    breadcrumb = [
        {"url": reverse_lazy("dashboard:phases:list"), "title": gettext_lazy("Phases")},
        {"url": "", "title": title},
    ]

    phase_db = None
    phase = None
    doc = None
    phase_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.phase = self.get_object()
            self.phase_db_name = "process_design"
            self.phase_db = nsc.get_db(self.phase_db_name)
            query_result = self.phase_db.get_query_result({"type": "phase"})[:]
            self.doc = self.phase_db[query_result[0]["_id"]]
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePhaseView, self).get_context_data(**kwargs)
        form = ctx.get("form")
        ctx.setdefault("phase_doc", self.doc)
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
        if not self.phase_db_name:
            raise Http404("We don't find the database name for the phase.")

        form = UpdatePhaseForm(request.POST, instance=self.phase)
        if form.is_valid():
            return self.form_valid(form)
        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        phase = form.save(commit=False)
        phase.name = data["name"]
        phase.description = data["description"]
        phase.save()
        doc = {"name": data["name"], "description": data["description"]}
        nsc = NoSQLClient()
        query_result = self.phase_db.get_query_result({"_id": phase.couch_id})[:]
        self.doc = self.phase_db[query_result[0]["_id"]]
        nsc.update_doc(self.phase_db, self.doc["_id"], doc)
        return redirect("dashboard:phases:list")


class PhaseDetailView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.DetailView
):
    template_name = "phases/phase_detail.html"
    context_object_name = "phase_doc"
    title = gettext_lazy("Phase Detail")
    active_level1 = "phases"
    model = Phase
    breadcrumb = [
        {"url": reverse_lazy("dashboard:phases:list"), "title": gettext_lazy("Phases")},
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["phase"] = self.obj
        # facilitator_docs = self.facilitator_db.all_docs(include_docs=True)['rows']
        return context

    def get_object(self, queryset=None):
        return self.phase


def phase_detail_view(request, id):
    try:
        phase = Phase.objects.get(id=id)
        activities = list(Activity.objects.filter(phase_id=phase.id).order_by("order"))
        nbr_activities = len(activities)
    except Phase.DoesNotExist:
        raise Http404("Phase does not exist")

    return render(
        request,
        "phases/phase_detail.html",
        context={
            "phase": phase,
            "activities": activities,
            "nbr_activities": nbr_activities,
        },
    )
