from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator # Importante para la paginación
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importamos los modelos desde el paquete superior
from Marketplace_App.models import Anuncio, Categoria
from Marketplace_App.forms import AnuncioForm

def home(request, categoria_slug=None):
    # ... (lógica inicial de categorías, productos base y ubicaciones) ...
    categorias = Categoria.objects.all()
    productos = Anuncio.objects.filter(activo=True).order_by('-fecha_publicacion')
    ubicaciones = Anuncio.objects.filter(activo=True).values_list('ubicacion', flat=True).distinct().order_by('ubicacion')
    
    # ... (filtros de categoría, ubicación y búsqueda existentes) ...
    categoria_actual = None
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    ubicacion_actual = request.GET.get('ubicacion')
    if ubicacion_actual:
        productos = productos.filter(ubicacion=ubicacion_actual)
        
    busqueda = request.GET.get('q')
    if busqueda:
        productos = productos.filter(
            Q(titulo__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )

    # 1. ORDENAMIENTO (Mantener si ya lo tenías)
    orden = request.GET.get('orden')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
        
    # --- 2. NUEVO FILTRO: TIEMPO DE PUBLICACIÓN ---
    tiempo = request.GET.get('tiempo')
    
    if tiempo:
        hoy = timezone.now()
        fecha_limite = None
        
        if tiempo == '24h':
            fecha_limite = hoy - timedelta(days=1)
        elif tiempo == '7d':
            fecha_limite = hoy - timedelta(days=7)
        elif tiempo == '30d':
            fecha_limite = hoy - timedelta(days=30)
            
        if fecha_limite:
            # Filtramos los que sean MAYORES o IGUALES a la fecha límite
            productos = productos.filter(fecha_publicacion__gte=fecha_limite)

    # --- Paginación ---
    paginator = Paginator(productos, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'productos': page_obj, 
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'ubicaciones': ubicaciones,
        'ubicacion_actual': ubicacion_actual,
        'busqueda': busqueda,
        'orden': orden,
        'tiempo_actual': tiempo, # <--- Enviamos esto para marcar el select
    }
    return render(request, 'Marketplace_App/home.html', context)

@login_required
def crear_anuncio(request):
    # --- CANDADO DE SEGURIDAD MEJORADO ---
    try:
        perfil = request.user.perfil
        # 1. Chequeamos el tilde de verificado
        # 2. Y ADEMÁS chequeamos que realmente tenga un número escrito (que no esté vacío)
        if not perfil.telefono_verificado or not perfil.telefono_contacto:
            messages.warning(request, "⚠️ Para publicar anuncios, primero debes verificar tu número de celular.")
            return redirect('verificar_telefono')
    except Exception:
        return redirect('verificar_telefono')
    
    # --- BLOQUE DE SEGURIDAD (Nuevo) ---
    try:
        # Verificamos si tiene perfil y si está verificado
        if not hasattr(request.user, 'perfil') or not request.user.perfil.telefono_verificado:
            messages.warning(request, "⚠️ Para publicar anuncios, primero debes verificar tu número de celular.")
            return redirect('verificar_telefono')
    except Exception:
        # Si ocurre cualquier error extraño, lo mandamos a verificar por seguridad
        return redirect('verificar_telefono')
    
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.usuario = request.user
            anuncio.save()
            messages.success(request, '¡Tu anuncio ha sido publicado con éxito!')
            return redirect('home')
    else:
        form = AnuncioForm()
        
    context = {'form': form}
    # NOTA: Actualizamos la ruta al template
    return render(request, 'Marketplace_App/anuncios/crear_anuncio.html', context)

def detalle_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk, activo=True)
    context = {'anuncio': anuncio}
    # NOTA: Actualizamos la ruta al template
    return render(request, 'Marketplace_App/anuncios/detalle_anuncio.html', context)

@login_required
def editar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el anuncio.')
            
    return redirect('mi_perfil')

@login_required
def eliminar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    
    if anuncio.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar este anuncio.")
        return redirect('mi_perfil')
    
    if request.method == 'POST':
        anuncio.delete()
        messages.success(request, "El anuncio ha sido eliminado correctamente.")
        return redirect('mi_perfil')
        
    return redirect('mi_perfil')