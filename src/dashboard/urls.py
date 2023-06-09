from django.conf.urls import include
from django.urls import path

app_name = "dashboard"
urlpatterns = [
    path("", include("dashboard.authentication.urls")),
    path("facilitators/", include("dashboard.facilitators.urls")),
    path("administrative-levels/", include("dashboard.administrative_levels.urls")),
    path("diagnostics/", include("dashboard.diagnostics.urls")),
    path("projects/", include("dashboard.projects.urls")),
    path("phases/", include("dashboard.phases.urls")),
    path("activities/", include("dashboard.activities.urls")),
    path("tasks/", include("dashboard.tasks.urls")),
    path("builder/", include("dashboard.form_builder.urls")),
]
