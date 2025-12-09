from django.urls import path
from Marketplace_App import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('categoria/<slug:categoria_slug>/', views.home, name='home_por_categoria'),
    
    # Rutas de Usuario
    path('registro', views.registro, name='registro'),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Rutas de Perfil y Anuncios
    path('crear-anuncio', views.crear_anuncio, name='crear_anuncio'),
    path('anuncio/<int:pk>/', views.detalle_anuncio, name='detalle_anuncio'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('anuncio/editar/<int:pk>/', views.editar_anuncio, name='editar_anuncio'),
    path('anuncio/eliminar/<int:pk>/', views.eliminar_anuncio, name='eliminar_anuncio'),

    # --- RUTAS DE VERIFICACIÓN DE TELÉFONO (LAS NUEVAS) ---
    path('verificar-telefono/', views.verificar_telefono, name='verificar_telefono'),
    path('validar-sms/', views.validar_codigo_telefono, name='validar_codigo_telefono'),
    
    # BORRA ESTA LÍNEA SI LA TIENES, ES LA QUE DA ERROR:
    # path('verificar-registro/', views.verificar_registro, name='verificar_registro'),
]