from django.views.generic import FormView, View as GenericView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageMixin, AJAXRequestMixin, JSONResponseMixin
from django.utils.translation import gettext_lazy
from django.conf import settings
from dashboard.diagnostics.forms import DiagnosticsForm
from dashboard.utils import (
    # get_child_administrative_levels,
    # get_parent_administrative_level,
    # get_documents_by_type,
    # get_administrative_levels_by_type,
    # get_region_of_village_by_sql_id,
    get_departement_of_administrative_level_by_sql_id,
    get_all_docs_administrative_levels_by_type_and_administrative_id,
    get_all_docs_administrative_levels_by_type_and_parent_id,
    get_all_docs_administrative_levels_by_type,
    sort_months_dict,
)
from cdd.constants import ADMINISTRATIVE_LEVEL_TYPE, AGENT_ROLE
from no_sql_client import NoSQLClient
from authentication.models import Facilitator
from collections import defaultdict, OrderedDict


class DashboardDiagnosticsCDDView(PageMixin, LoginRequiredMixin, FormView):
    template_name = "diagnostics/diagnostics.html"
    context_object_name = "Diagnostics"
    title = gettext_lazy("diagnostics")
    active_level1 = "diagnostics"
    form_class = DiagnosticsForm
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["access_token"] = settings.MAPBOX_ACCESS_TOKEN
        context["lat"] = settings.DIAGNOSTIC_MAP_LATITUDE
        context["lng"] = settings.DIAGNOSTIC_MAP_LONGITUDE
        context["zoom"] = settings.DIAGNOSTIC_MAP_ZOOM
        context["ws_bound"] = settings.DIAGNOSTIC_MAP_WS_BOUND
        context["en_bound"] = settings.DIAGNOSTIC_MAP_EN_BOUND
        context["country_iso_code"] = settings.DIAGNOSTIC_MAP_ISO_CODE

        context["list_fields"] = [
            "phase",
            "activity",
            "task",
            "departement",
            "commune",
            "arrondissement",
            "village",
        ]
        # exclude test account
        facilitators = Facilitator.objects.all().exclude(username__icontains="test")
        # exclude undeployed agents
        facilitators = facilitators.exclude(username__icontains="FC_")
        context["total_fc"] = facilitators.filter(role=AGENT_ROLE.FC).count()
        context["total_sc"] = facilitators.filter(role=AGENT_ROLE.SC).count()

        active_facilitators_monthly = defaultdict(int)
        percent_le_30 = percent_in_30_50 = percent_in_50_80 = percent_gt_80 = (
            percent_at_100
        ) = 0
        for facilitator in facilitators:
            facilitator.completion_percentage = facilitator.get_tasks_completion()
            if facilitator.completion_percentage <= 30:
                percent_le_30 += 1
            if 30 < facilitator.completion_percentage <= 50:
                percent_in_30_50 += 1
            if 50 < facilitator.completion_percentage <= 80:
                percent_in_50_80 += 1
            if facilitator.completion_percentage > 80:
                percent_gt_80 += 1
            if facilitator.completion_percentage == 100:
                percent_at_100 += 1

            monthly_activity = facilitator.get_monthly_activity()
            for month, task_count in monthly_activity.items():
                if task_count > 0:
                    active_facilitators_monthly[month] += 1

        context["percent_le_30"] = percent_le_30
        context["percent_in_30_50"] = percent_in_30_50
        context["percent_in_50_80"] = percent_in_50_80
        context["percent_gt_80"] = percent_gt_80
        context["percent_at_100"] = percent_at_100
        context["active_facilitators_monthly"] = sort_months_dict(
            active_facilitators_monthly, self.request
        )
        # mapbox coordinate conf for departement

        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault("content_type", self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )


class GetTasksDiagnosticsView(
    AJAXRequestMixin, LoginRequiredMixin, JSONResponseMixin, GenericView
):
    def get(self, request, *args, **kwargs):
        _type = request.GET.get("type")
        if _type == "departement":
            _type = "département"

        type_header = _type
        print("type : ", _type)
        sql_id = request.GET.get("sql_id")
        if not sql_id:
            raise Exception("The value of the element must not be null!!!")
        nsc = NoSQLClient()
        administrative_levels_db = nsc.get_db("administrative_levels")
        administrative_levels = administrative_levels_db.all_docs(include_docs=True)[
            "rows"
        ]
        liste_villages = []
        nbr_tasks = 0
        nbr_tasks_completed = 0
        percentage_tasks_completed = 0
        nbr_facilitators = 0
        nbr_villages = nbr_not_village = nbr_all_adm_lvl = 0
        search_by_locality = False
        already_count_facilitator = False
        _departement = None
        regions = {
            "SAVANES": {
                "nbr_tasks": 0,
                "nbr_tasks_completed": 0,
                "percentage_tasks_completed": 0,
            },
            "KARA": {
                "nbr_tasks": 0,
                "nbr_tasks_completed": 0,
                "percentage_tasks_completed": 0,
            },
            "CENTRALE": {
                "nbr_tasks": 0,
                "nbr_tasks_completed": 0,
                "percentage_tasks_completed": 0,
            },
        }
        list_departements = get_all_docs_administrative_levels_by_type(
            administrative_levels, ADMINISTRATIVE_LEVEL_TYPE.DÉPARTEMENT
        )
        departements = {
            elt["name"]: {
                "nbr_tasks": 0,
                "nbr_tasks_completed": 0,
                "percentage_tasks_completed": 0,
            }
            for elt in list_departements
        }
        # _type in ["département", "commune", "arrondissement", "village"]
        # ["region", "prefecture", "commune", "canton", "village"]
        if _type in ADMINISTRATIVE_LEVEL_TYPE.values.keys():
            search_by_locality = True
            liste_prefectures = []  ##
            liste_communes = []
            liste_cantons = []  ##
            liste_arrondissements = []

            # if _type == "region":
            if _type == ADMINISTRATIVE_LEVEL_TYPE.DÉPARTEMENT:
                departement = (
                    get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type, sql_id
                    )
                )
                departement = departement[:][0]
                _type = ADMINISTRATIVE_LEVEL_TYPE.COMMUNE
                liste_communes = (
                    get_all_docs_administrative_levels_by_type_and_parent_id(
                        administrative_levels,
                        _type,
                        departement["administrative_id"],
                    )[:]
                )

            # "prefecture"
            if _type == ADMINISTRATIVE_LEVEL_TYPE.COMMUNE:
                if not liste_communes:
                    liste_communes = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type, sql_id
                    )[
                        :
                    ]
                _type = ADMINISTRATIVE_LEVEL_TYPE.ARRONDISSEMENT
                for commune in liste_communes:
                    [
                        liste_arrondissements.append(elt)
                        for elt in get_all_docs_administrative_levels_by_type_and_parent_id(
                            administrative_levels,
                            _type,
                            commune["administrative_id"],
                        )[
                            :
                        ]
                    ]

            if _type == ADMINISTRATIVE_LEVEL_TYPE.ARRONDISSEMENT:
                if not liste_arrondissements:
                    liste_arrondissements = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type, sql_id
                    )[
                        :
                    ]
                _type = ADMINISTRATIVE_LEVEL_TYPE.VILLAGE
                for arrondissement in liste_arrondissements:
                    [
                        liste_villages.append(elt)
                        for elt in get_all_docs_administrative_levels_by_type_and_parent_id(
                            administrative_levels,
                            _type,
                            arrondissement["administrative_id"],
                        )[
                            :
                        ]
                    ]
            nbr_not_village = len(liste_arrondissements)
            print("nbr_not_village : ", nbr_not_village)
            if _type == ADMINISTRATIVE_LEVEL_TYPE.VILLAGE:
                if not liste_villages:
                    liste_villages = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type, sql_id
                    )[
                        :
                    ]

            for f in Facilitator.objects.filter(
                develop_mode=False, training_mode=False
            ):
                already_count_facilitator = False
                facilitator_db = nsc.get_db(f.no_sql_db_name)
                query_result = facilitator_db.get_query_result(
                    {
                        "type": "facilitator"  # , "develop_mode": False, "training_mode": False
                    }
                )[:]
                if query_result:
                    doc = query_result[0]
                    for _village in doc["administrative_levels"]:
                        if str(
                            _village["id"]
                        ).isdigit():  # Verify if id contain only digit
                            for village in liste_villages:
                                if str(_village["id"]) == str(
                                    village["administrative_id"]
                                ):  # _village['name'] == village['name'] and
                                    nbr_villages += 1
                                    if not already_count_facilitator:
                                        nbr_facilitators += 1
                                        already_count_facilitator = True

                                    for _task in facilitator_db.all_docs(
                                        include_docs=True
                                    )["rows"]:
                                        _task = _task.get("doc")
                                        if _task.get("type") == "task" and str(
                                            _task.get("administrative_level_id")
                                        ) == str(_village["id"]):
                                            if _task["completed"]:
                                                nbr_tasks_completed += 1
                                            nbr_tasks += 1

            nbr_all_adm_lvl = len(liste_villages)
            print("nbr_all_adm_lvl : ", nbr_all_adm_lvl)
            nbr_villages = nbr_all_adm_lvl - nbr_not_village
            if nbr_villages > 0:
                _departement = get_departement_of_administrative_level_by_sql_id(
                    administrative_levels_db, liste_villages[0]["administrative_id"]
                )

            percentage_tasks_completed = (
                ((nbr_tasks_completed / nbr_tasks) * 100) if nbr_tasks else 0
            )

        elif _type in ["phase", "activity", "task"]:
            if _type in ("phase", "activity"):
                for f in Facilitator.objects.filter(
                    develop_mode=False, training_mode=False
                ):
                    already_count_facilitator = False
                    facilitator_db = nsc.get_db(f.no_sql_db_name)
                    query_result = facilitator_db.get_query_result(
                        {"type": _type, "sql_id": int(sql_id)}
                    )[:]
                    if query_result:
                        for _task in facilitator_db.all_docs(include_docs=True)["rows"]:
                            _task = _task.get("doc")
                            if (
                                _task.get("type") == "task"
                                and _task.get((str(type_header) + "_id"))
                                == query_result[0]["_id"]
                            ):
                                if str(_task["administrative_level_id"]).isdigit():
                                    if not already_count_facilitator:
                                        nbr_facilitators += 1
                                        already_count_facilitator = True

                                    _departement = get_departement_of_administrative_level_by_sql_id(
                                        administrative_levels_db,
                                        _task["administrative_level_id"],
                                    )
                                    if _departement:
                                        _departement_name = _departement["name"]
                                        # if regions.get(_region_name):
                                        if _task["completed"]:
                                            departements[_departement_name][
                                                "nbr_tasks_completed"
                                            ] += 1
                                        departements[_departement_name][
                                            "nbr_tasks"
                                        ] += 1

            elif _type == "task":
                for f in Facilitator.objects.filter(
                    develop_mode=False, training_mode=False
                ):
                    already_count_facilitator = False
                    facilitator_db = nsc.get_db(f.no_sql_db_name)
                    _tasks = facilitator_db.get_query_result(
                        {"type": "task", "sql_id": int(sql_id)}
                    )[:]
                    for _task in _tasks:
                        if str(_task["administrative_level_id"]).isdigit():
                            if not already_count_facilitator:
                                nbr_facilitators += 1
                                already_count_facilitator = True

                            _departement = (
                                get_departement_of_administrative_level_by_sql_id(
                                    administrative_levels_db,
                                    _task["administrative_level_id"],
                                )
                            )
                            if _departement:
                                _departement_name = _departement["name"]
                                if _task["completed"]:
                                    departements[_departement_name][
                                        "nbr_tasks_completed"
                                    ] += 1
                                departements[_departement_name]["nbr_tasks"] += 1

            for departement, values in departements.items():
                departements[departement]["percentage_tasks_completed"] = (
                    (
                        (
                            departements[departement]["nbr_tasks_completed"]
                            / departements[departement]["nbr_tasks"]
                        )
                        * 100
                    )
                    if departements[departement]["nbr_tasks"]
                    else 0
                )

        if search_by_locality:
            return self.render_to_json_response(
                {
                    "type": type_header,
                    "nbr_tasks": nbr_tasks,
                    "nbr_tasks_completed": nbr_tasks_completed,
                    "percentage_tasks_completed": percentage_tasks_completed,
                    "departement": _departement["name"] if _departement else None,
                    "search_by_locality": search_by_locality,
                    "nbr_facilitators": nbr_facilitators,
                    "nbr_villages": nbr_villages,
                },
                safe=False,
            )

        return self.render_to_json_response(
            {
                "type": type_header,
                "departements": departements,
                "search_by_locality": search_by_locality,
                "nbr_facilitators": nbr_facilitators,
            },
            safe=False,
        )
