from django.urls import path, include  # ← include agregado
from django.views.generic import RedirectView  # ← RedirectView agregado

urlpatterns = [
    path("admin/", admin.site.urls),
    path("productos/", include("productos.urls")),  # ← NUEVO
    path("", RedirectView.as_view(url="/productos/", permanent=False)),  # ← NUEVO
]
