# Marketplace_App/views.py
from django.shortcuts import get_object_or_404, render, redirect

# Importamos el nuevo formulario y el modelo Anuncio
from Marketplace_App.forms import ContactForm, PerfilUsuarioForm, RegisterForm, LoginForm, AnuncioForm 
from Marketplace_App.models import Categoria, PerfilUsuario, User, Anuncio 
from django.contrib import messages
from django.contrib.auth.decorators import login_required # ¡Fundamental!

# Create your views here.
# Marketplace_App/views.py

# 1. Agrega esta importación al principio del archivo
from django.db.models import Q 

# ... (otras importaciones) ...

def home(request, categoria_slug=None):
    # ... (código existente para categorías y productos base) ...
    categorias = Categoria.objects.all()
    productos = Anuncio.objects.filter(activo=True).order_by('-fecha_publicacion')
    
    # ... (código existente de ubicaciones) ...
    ubicaciones = Anuncio.objects.filter(activo=True).values_list('ubicacion', flat=True).distinct().order_by('ubicacion')
    
    categoria_actual = None
    
    # 1. Filtro de Categoría (Existente)
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    # 2. Filtro de Ubicación (Existente)
    ubicacion_actual = request.GET.get('ubicacion')
    if ubicacion_actual:
        productos = productos.filter(ubicacion=ubicacion_actual)
        
    # --- NUEVO: Lógica del Buscador ---
    busqueda = request.GET.get('q') # 'q' es el nombre estándar para queries de búsqueda
    
    if busqueda:
        # Usamos Q para decir: (titulo CONTIENE busqueda) O (descripcion CONTIENE busqueda)
        productos = productos.filter(
            Q(titulo__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'ubicaciones': ubicaciones,
        'ubicacion_actual': ubicacion_actual,
        'busqueda': busqueda, # Pasamos esto para mantener el texto en la cajita
    }
    return render(request, 'Marketplace_App/home.html', context)

def registro(request):
    
    formulario_registro = RegisterForm()
    
    if request.method == 'POST':
        # Rellenamos el formulario con los datos
        formulario_registro = RegisterForm(request.POST)
        if formulario_registro.is_valid(): # Usar la validación del form
            username = formulario_registro.cleaned_data['username']
            email = formulario_registro.cleaned_data['email']
            password = formulario_registro.cleaned_data['password']
            password2 = formulario_registro.cleaned_data['password2']
            
            if password == password2:
                # CORRECCIÓN CRÍTICA: Usar create_user para encriptar la contraseña (hashing)
                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, f'Cuenta creada para {username}!')
                    return redirect('login') 
                except Exception as e:
                    messages.error(request, f"Error al crear usuario: {e}")
            else:
                messages.error(request, "Las contraseñas no coinciden.")
    
    return render(request, 'Marketplace_App/registro.html', {'formulario_registro': formulario_registro})


# --- NUEVA VISTA: Crear Anuncio ---
@login_required # Solo usuarios logueados pueden acceder
def crear_anuncio(request):
    if request.method == 'POST':
        # **IMPORTANTE**: Usar request.FILES para manejar la subida de imágenes
        form = AnuncioForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. No guardar la instancia todavía (commit=False)
            anuncio = form.save(commit=False)
            
            # 2. Asignar el usuario logueado
            anuncio.usuario = request.user
            
            # 3. Ahora sí, guardar la instancia final en la base de datos
            anuncio.save()
            
            messages.success(request, '¡Tu anuncio ha sido publicado con éxito!')
            return redirect('home') # Redirige a la home
    else:
        form = AnuncioForm()
        
    context = {
        'form': form
    }
    return render(request, 'Marketplace_App/crear_anuncio.html', context)

# --- NUEVA VISTA: Detalle de Anuncio ---
def detalle_anuncio(request, pk):
    """
    Muestra los detalles de un anuncio específico.
    Utiliza 'pk' (Primary Key) pasado en la URL para buscar el anuncio.
    """
    # Si el anuncio no existe o no está activo, Django lanzará un error 404
    anuncio = get_object_or_404(Anuncio, pk=pk, activo=True)
    
    context = {
        'anuncio': anuncio
    }
    return render(request, 'Marketplace_App/detalle_anuncio.html', context)

@login_required
def editar_anuncio(request, pk):
    """Procesa el POST del modal de anuncio"""
    # Nos aseguramos que el anuncio pertenezca al usuario actual (seguridad)
    anuncio = get_object_or_404(Anuncio, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Importante: request.FILES para las imágenes
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el anuncio.')
            
    return redirect('mi_perfil')

# Marketplace_App/views.py

@login_required
def eliminar_anuncio(request, pk):
    # Obtenemos el anuncio asegurándonos que pertenezca al usuario actual
    anuncio = get_object_or_404(Anuncio, pk=pk)
    
    if anuncio.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar este anuncio.")
        return redirect('mi_perfil')
    
    if request.method == 'POST':
        anuncio.delete()
        messages.success(request, "El anuncio ha sido eliminado correctamente.")
        return redirect('mi_perfil')
        
    # Si intentan acceder por GET, los devolvemos al perfil
    return redirect('mi_perfil')

@login_required
def mi_perfil(request):
    # 1. Obtener o crear perfil
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    # 2. Formulario para editar Perfil (Lo pasamos al contexto para el modal)
    form_perfil = PerfilUsuarioForm(instance=perfil)

    # 3. Obtener anuncios y crear una lista de tuplas (anuncio, formulario)
    # Esto es necesario para que cada anuncio en el bucle tenga su PROPIO formulario con sus datos
    mis_anuncios_qs = Anuncio.objects.filter(usuario=request.user).order_by('-fecha_publicacion')
    anuncios_con_forms = []
    
    for anuncio in mis_anuncios_qs:
        form = AnuncioForm(instance=anuncio)
        anuncios_con_forms.append((anuncio, form))

    context = {
        'perfil': perfil,
        'form_perfil': form_perfil,       # Form para el modal de perfil
        'anuncios_con_forms': anuncios_con_forms # Lista [(anuncio, form), ...]
    }
    return render(request, 'Marketplace_App/mi_perfil.html', context)

@login_required
def editar_perfil(request):
    """Procesa el POST del modal de perfil"""
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        # AGREGAR request.FILES AQUÍ
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el perfil.')
            
    return redirect('mi_perfil')