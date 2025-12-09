from django.db import models

from django.db import models
from django.contrib.auth import get_user_model

# Obtenemos el modelo de usuario de Django, que ya está normalizado (idUsuario, nombreUsuario, contraseña, etc.)
User = get_user_model()

# --- NUEVA ENTIDAD: PerfilUsuario (Extensión del User de Django, 3FN) ---
# Clave Primaria: id (automático)
# Clave Foránea: usuario (Relación Uno-a-Uno con User)
class PerfilUsuario(models.Model):
    """
    Extiende el modelo de usuario de Django para incluir información personal adicional
    como teléfono, ubicación de contacto y si el perfil está verificado.
    Relación Uno-a-Uno con User, asegurando 3FN.
    """
    # Relación uno a uno con el modelo User
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')

    # Campos adicionales de información personal
    imagen = models.ImageField(upload_to='perfil_imagenes/', blank=True, null=True, verbose_name="Foto de Perfil")
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de Contacto")
    ubicacion_contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación/Ciudad")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Campo 'verificado' del DER original, movido aquí
    verificado = models.BooleanField(default=False) 
    
    telefono_verificado = models.BooleanField(default=False)
    
    # Campo 'rol' (Si se necesitan roles complejos, se usaría un modelo de Grupos de Django. 
    # Aquí se maneja como un campo simple para propósitos del DER)
    ROL_CHOICES = [
        ('VENDEDOR', 'Vendedor'),
        ('COMPRADOR', 'Comprador'),
        ('ADMIN', 'Administrador'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='COMPRADOR')

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f'Perfil de {self.usuario.username}'

# --- ENTIDAD: Categoría (1FN, 2FN, 3FN) ---
# Clave Primaria: id (automático)
# No hay dependencias parciales ni transitivas.
class Categoria(models.Model):
    """
    Define las categorías para los anuncios (ej: Vehículos, Inmuebles, Servicios).
    Relación 1:N con Anuncio.
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True) # URL amigable

    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# --- ENTIDAD: Anuncio (1FN, 2FN, 3FN) ---
# Clave Primaria: id (automático)
# Dependencias: categoría (FK) y usuario (FK). No hay dependencias parciales ni transitivas.
class Anuncio(models.Model):
    """
    Representa un anuncio publicado en el marketplace.
    Relación 1:N con Comentario. Relación 1:N con Reporte (a través de TipoEntidad).
    """
    ESTADOS = [
        ('NUEVO', 'Nuevo'),
        ('USADO', 'Usado'),
        ('REACONDICIONADO', 'Reacondicionado'),
    ]

    # Relaciones (Foreign Keys)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anuncios_publicados') # Relación 1:N con Usuario
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='anuncios_categoria') # Relación N:1 con Categoría

    # Campos principales
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=9, decimal_places=2) 

    # Ubicación y estado
    ubicacion = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='USADO')

    # Fechas y control
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True) 

    # Gestión de archivos
    imagen_principal = models.ImageField(upload_to='anuncios_imagenes/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ['-fecha_publicacion'] 

    def __str__(self):
        return self.titulo


# --- ENTIDAD: Comentario (1FN, 2FN, 3FN) ---
# Clave Primaria: id (automático)
# Dependencias: anuncio (FK) y usuario (FK). No hay dependencias parciales ni transitivas.
class Comentario(models.Model):
    """
    Comentario realizado por un usuario sobre un anuncio.
    Relación N:1 con Anuncio y N:1 con Usuario.
    """
    # Relaciones (Foreign Keys)
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='comentarios') # Relación N:1 con Anuncio
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comentarios_realizados') # Relación N:1 con Usuario (SET_NULL para preservar el comentario si el usuario se elimina)

    # Campos principales
    contenido = models.TextField(max_length = 255)
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['fecha_comentario']

    def __str__(self):
        return f'Comentario de {self.usuario.username} en {self.anuncio.titulo}'


# --- ENTIDAD: Reporte (1FN, 2FN, 3FN) ---
# Este modelo es un ejemplo de estructura polimórfica simple para respetar el DER.
# Clave Primaria: id (automático)
# Dependencias: usuario_reportador (FK). No hay dependencias parciales ni transitivas.
class Reporte(models.Model):
    """
    Permite a un usuario reportar otro usuario o un anuncio (estructura de reporte polimórfico).
    Relación 1:N con Usuario.
    """
    TIPOS_ENTIDAD = [
        ('ANUNCIO', 'Anuncio'),
        ('USUARIO', 'Usuario'),
    ]

    # Relaciones (Foreign Keys)
    usuario_reportador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reportes_hechos') # Usuario que realiza el reporte (Relación 1:N)
    
    # Campos del reporte
    motivo = models.CharField(max_length=255)
    descripcion_reporte = models.TextField(blank=True, null=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    # Campos para la entidad reportada (Siguiendo el DER con tipoEntidad e idEntidadReportada)
    tipo_entidad_reportada = models.CharField(max_length=10, choices=TIPOS_ENTIDAD)
    identificador_entidad_reportada = models.IntegerField() # El ID de Anuncio o el ID de Usuario

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-fecha_reporte']

    def __str__(self):
        return f'Reporte de {self.tipo_entidad_reportada} ID {self.identificador_entidad_reportada}'