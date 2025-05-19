from django.urls import path

from dashboard.tasks import views
from dashboard.activities import views as activityView

app_name = "tasks"
urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("tasks-list/", views.TaskListTableView.as_view(), name="tasks_list"),
    path("create/", views.CreateTaskFormView.as_view(), name="create"),
    path("create/<int:id>", views.CreateTaskForm.as_view(), name="create_task"),
    path("<int:pk>/update/", views.UpdateTaskView.as_view(), name="update"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("MoveUp/<int:id>", views.changeOrderUp, name="MoveUp"),
    path("MoveDown/<int:id>", views.changeOrderDown, name="MoveDown"),
    path("Detail/<int:id>", views.task_detail_view, name="task_detail"),
    # path("Detail/<int:id>", activityView.activity_detail_view, name="activity_Detail"),
]
