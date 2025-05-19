from django.urls import path

from dashboard.phases import views

app_name = "phases"
urlpatterns = [
    path("", views.PhaseListView.as_view(), name="list"),
    path("phases-list/", views.PhaseListTableView.as_view(), name="phases_list"),
    path("create/", views.CreatePhaseFormView.as_view(), name="create"),
    path("<int:pk>/update/", views.UpdatePhaseView.as_view(), name="update"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("MoveUp/<int:id>", views.changeOrderUp, name="MoveUp"),
    path("MoveDown/<int:id>", views.changeOrderDown, name="MoveDown"),
    path("Detail/<int:id>", views.phase_detail_view, name="phase_Detail"),
    # path('MoveUpActivity/<int:id>', views.changeOrderActivityUp, name='MoveUpActivity'),
]
