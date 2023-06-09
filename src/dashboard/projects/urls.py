from django.urls import path

from dashboard.projects import views

app_name = "projects"
urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("projects-list/", views.ProjectListTableView.as_view(), name="projects_list"),
    path("create/", views.CreateProjectFormView.as_view(), name="create"),
    path("<int:pk>/update/", views.UpdateProjectView.as_view(), name="update"),
    # path('update/<int:id>', views.update, name='update'),
    # path('update/updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    # path('<slug:id>/', views.ProjectDetailView.as_view(), name='detail'),
    path("delete/<int:id>", views.delete, name="delete"),
]
