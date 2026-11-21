from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.profile_view, name="profile"),
    path("profil/mot-de-passe/", views.password_change_view, name="password_change"),

    # User management (admin)
    path("utilisateurs/", views.user_list, name="user_list"),
    path("utilisateurs/nouveau/", views.user_create, name="user_create"),
    path("utilisateurs/<int:pk>/modifier/", views.user_edit, name="user_edit"),
    path("utilisateurs/<int:pk>/activer/", views.user_toggle_active, name="user_toggle_active"),
    path("utilisateurs/<int:pk>/mot-de-passe/", views.user_reset_password, name="user_reset_password"),

    # Audit log
    path("journal/", views.audit_log, name="audit_log"),

    # Password reset flow
    path("reinitialisation/", views.AppPasswordResetView.as_view(), name="password_reset"),
    path("reinitialisation/envoye/", views.AppPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reinitialisation/<uidb64>/<token>/", views.AppPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reinitialisation/termine/", views.AppPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
