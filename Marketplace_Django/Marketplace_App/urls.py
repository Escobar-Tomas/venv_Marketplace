# Marketplace_App/urls.py
from django.urls import path
from Marketplace_App import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    
    # NUEVA RUTA: Filtrado por categoría
    # Ejemplo de uso: /categoria/vehiculos/
    path('categoria/<slug:categoria_slug>/', views.home, name='home_por_categoria'),

    path('registro', views.registro, name='registro'),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('crear-anuncio', views.crear_anuncio, name='crear_anuncio'),
    path('anuncio/<int:pk>/', views.detalle_anuncio, name='detalle_anuncio'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # NUEVA RUTA: Dashboard del Perfil (Ver info + Anuncios)
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    
    # Mantenemos la ruta de edición (puedes dejarla como 'perfil/editar/')
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # NUEVA RUTA para editar anuncio específico
    path('anuncio/editar/<int:pk>/', views.editar_anuncio, name='editar_anuncio'),
    
    path('anuncio/eliminar/<int:pk>/', views.eliminar_anuncio, name='eliminar_anuncio'),
]