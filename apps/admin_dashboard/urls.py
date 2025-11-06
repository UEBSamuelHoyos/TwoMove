# apps/admin_dashboard/urls.py
from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [
    # Login y Logout
    path("login/", views.admin_login_view, name="admin_login"),
    path("logout/", views.admin_logout_view, name="admin_logout"),

    # Dashboard principal
    path("", views.dashboard_home, name="dashboard_home"),

    # Panel de reportes
    path("reportes/", views.reportes_panel, name="reportes_panel"),

    # ✅ Nueva ruta para descargar reportes (falta en tu proyecto)
    path("reportes/descargar/", views.descargar_reporte, name="descargar_reporte"),
    
    path("sanciones/", views.sanciones_panel, name="sanciones_panel"),
    path("sanciones/levantar/<int:sancion_id>/", views.levantar_sancion, name="levantar_sancion"),
    path("usuarios/", views.usuarios_panel, name="usuarios_panel"),
    path("usuarios/editar/", views.usuarios_editar, name="usuarios_editar"),
    path("usuarios/toggle/<int:usuario_id>/", views.usuarios_toggle, name="usuarios_toggle"),
    path("usuarios/eliminar/<int:usuario_id>/", views.usuarios_eliminar, name="usuarios_eliminar"),


]
