from django.urls import path
from . import views

app_name = "aiassistant"

urlpatterns = [
    path("chat/", views.chat_home, name="chat"),
    path("chat/nouvelle/", views.chat_new, name="chat_new"),
    path("chat/<int:pk>/", views.chat_session, name="chat_session"),
    path("chat/<int:pk>/envoyer/", views.chat_send, name="chat_send"),
    path("assistant-administratif/", views.admin_assistant, name="admin_assistant"),
    path("analyse/", views.data_analysis, name="analysis"),
    path("recherche/", views.smart_search, name="search"),
]
