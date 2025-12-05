from django.contrib import admin
from .models import Categoria, Anuncio, PerfilUsuario, Comentario, Reporte

# Configuración básica para que el slug se rellene solo al escribir el nombre
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Anuncio)
admin.site.register(PerfilUsuario)
# admin.site.register(Comentario) # Opcional
# admin.site.register(Reporte)    # Opcional