from django.urls import path

from dashboard.form_builder import views

# from dashboard.activities import views as activityView

app_name = "form_builder"
urlpatterns = [
    path("", views.FormTypeListView.as_view(), name="list"),
    path("form-list/", views.FormTypeListTableView.as_view(), name="form_list"),
    path("create-form/", views.CreateFormTypeView.as_view(), name="create_form"),
    path(
        "update-form/<int:pk>", views.UpdateFormTypeView.as_view(), name="update_form"
    ),
    path(
        "delete-form/<int:pk>", views.UpdateFormTypeView.as_view(), name="delete_form"
    ),
    path(
        "form-fields/<int:id>",
        views.CreateFormTypeView.as_view(),
        name="list_form_fields",
    ),
    path(
        "delete-form-field/<int:pk>", views.delete_formfield, name="delete_form_field"
    ),
    # path('delete/<int:id>', views.delete, name='delete'),
    # path('MoveUp/<int:id>', views.changeOrderUp, name='MoveUp'),
    # path('MoveDown/<int:id>', views.changeOrderDown, name='MoveDown'),
    # path('Detail/<int:id>', views.task_detail_view, name='task_detail'),
    # path('Detail/<int:id>', activityView.activity_detail_view, name='activity_Detail'),
]
