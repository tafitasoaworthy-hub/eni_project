from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView

admin.site.site_header = "Administration — Gestion Universitaire"
admin.site.site_title = "Gestion Universitaire"
admin.site.index_title = "Tableau d'administration"

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", RedirectView.as_view(pattern_name="dashboard:home")),
    path("tableau-de-bord/", include("dashboard.urls")),
    path("comptes/", include("accounts.urls")),
    path("gestion/", include("core.urls")),
    path("inscriptions/", include("enrollments.urls")),
    path("emplois-du-temps/", include("schedules.urls")),
    path("documents/", include("documents.urls")),
    path("ia/", include("aiassistant.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
