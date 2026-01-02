from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(
        url=staticfiles_storage.url("images/favicon.ico"),
        permanent=True
    )),

    path("admin/", admin.site.urls),
    path("", include("app_fsMD.urls")), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "app_fsMD.views.error_404"