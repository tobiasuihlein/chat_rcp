from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from . import views

app_name = "recipe_app"

urlpatterns = [
    path('api/', include("api.urls")),
    path('recipes/', include("recipes.urls")),
    path('', views.home, name="home"),
    path('generator/', include("generator.urls")),
    path('admin/', admin.site.urls),
    path('chefs/', include("chefs.urls")),
    path('chefs/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
