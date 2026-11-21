from django.urls import path
from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollment_list, name="list"),
    path("nouvelle/", views.enrollment_create, name="create"),
    path("<int:pk>/", views.enrollment_detail, name="detail"),
    path("<int:pk>/modifier/", views.enrollment_edit, name="edit"),
    path("<int:pk>/statut/<str:statut>/", views.enrollment_set_status, name="set_status"),
]
