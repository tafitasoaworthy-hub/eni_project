from django.urls import path
from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.schedule_list, name="list"),
    path("mon-emploi-du-temps/", views.my_schedule, name="mine"),
    path("nouvelle/", views.schedule_create, name="create"),
    path("<int:pk>/", views.schedule_detail, name="detail"),
    path("<int:pk>/modifier/", views.schedule_edit, name="edit"),
    path("<int:pk>/supprimer/", views.schedule_delete, name="delete"),
]
