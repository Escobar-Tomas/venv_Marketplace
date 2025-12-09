from django import forms
from .models import Anuncio, PerfilUsuario

class ContactForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    email = forms.EmailField(label='Correo Electrónico')
    message = forms.CharField(label='Mensaje', widget=forms.Textarea)
    
class RegisterForm(forms.Form):
    username = forms.CharField(label='Nombre de Usuario', max_length=100)
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir Contraseña', widget=forms.PasswordInput)

# --- NUEVO FORMULARIO: AnuncioForm ---
class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        # Excluir campos que se llenan automáticamente en la vista
        exclude = ('usuario', 'fecha_publicacion', 'activo',)
        widgets = {
            # Usar Textarea para la descripción
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            # Opcional: Agregar clases Tailwind CSS para estilos si lo deseas
        }
        labels = {
            'titulo': 'Título del Anuncio',
            'descripcion': 'Descripción detallada',
            'precio': 'Precio ($)',
            'ubicacion': 'Ubicación (Ej: Yerba Buena, Tucumán)',
            'estado': 'Condición del producto',
            'categoria': 'Categoría',
            'imagen_principal': 'Foto principal',
        }

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        # Agregamos 'imagen' a la lista de campos
        fields = ['telefono_contacto', 'ubicacion_contacto', 'imagen'] 
        labels = {
            'telefono_contacto': 'Teléfono / WhatsApp',
            'ubicacion_contacto': 'Ciudad / Localidad',
            'imagen': 'Foto de Perfil'
        }
        widgets = {
            'telefono_contacto': forms.TextInput(attrs={'placeholder': 'Ej: 381-1234567'}),
            'ubicacion_contacto': forms.TextInput(attrs={'placeholder': 'Ej: Yerba Buena, San Miguel de Tucumán'}),
        }