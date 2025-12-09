import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from Marketplace_App.forms import RegisterForm, PerfilUsuarioForm, AnuncioForm
from Marketplace_App.models import PerfilUsuario, Anuncio
from django.contrib.auth.decorators import login_required

# --- 1. LOGIN PERSONALIZADO (Con "Recordarme") ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Lógica de "Recordarme"
            if request.POST.get('remember_me'):
                # La sesión dura 30 días (en segundos)
                request.session.set_expiry(30 * 24 * 60 * 60) 
            else:
                # La sesión expira al cerrar el navegador
                request.session.set_expiry(0) 
                
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

# --- 2. REGISTRO (Paso 1: Datos + Envio de Código) ---
def registro(request):
    if request.method == 'POST':
        formulario_registro = RegisterForm(request.POST)
        if formulario_registro.is_valid():
            username = formulario_registro.cleaned_data['username']
            email = formulario_registro.cleaned_data['email']
            password = formulario_registro.cleaned_data['password']
            password2 = formulario_registro.cleaned_data['password2']
            
            if password == password2:
                try:
                    # Verificar si el email ya existe
                    if User.objects.filter(email=email).exists():
                        messages.error(request, "Este correo electrónico ya está registrado.")
                        return render(request, 'Marketplace_App/usuarios/registro.html', {'formulario_registro': formulario_registro})

                    # Creamos el usuario pero INACTIVO
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.is_active = False 
                    user.save()
                    
                    # Generamos código de verificación
                    codigo = random.randint(100000, 999999)
                    
                    # Guardamos datos en la sesión temporalmente para el siguiente paso
                    request.session['registro_user_id'] = user.id
                    request.session['registro_codigo'] = codigo
                    
                    # Enviar correo
                    send_mail(
                        'Verifica tu cuenta - Marketplace',
                        f'Tu código de activación es: {codigo}',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    
                    messages.info(request, f'Te hemos enviado un código a {email}. Ingrésalo para activar tu cuenta.')
                    return redirect('verificar_registro') # Vamos al paso 2
                    
                except Exception as e:
                    messages.error(request, f"Error en el registro: {e}")
            else:
                messages.error(request, "Las contraseñas no coinciden.")
    else:
        formulario_registro = RegisterForm()
    
    return render(request, 'Marketplace_App/usuarios/registro.html', {'formulario_registro': formulario_registro})

# --- 3. VERIFICACIÓN DE REGISTRO (Paso 2: Ingresar Código) ---
def verificar_registro(request):
    # Si no hay un proceso de registro en curso, mandar al home
    if 'registro_user_id' not in request.session:
        return redirect('home')
        
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_generado = request.session.get('registro_codigo')
        user_id = request.session.get('registro_user_id')
        
        if str(codigo_ingresado) == str(codigo_generado):
            try:
                # Activar el usuario
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                # Crear perfil si no existe (buena práctica)
                PerfilUsuario.objects.get_or_create(usuario=user)
                
                # Limpiar sesión temporal
                del request.session['registro_user_id']
                del request.session['registro_codigo']
                
                messages.success(request, '¡Cuenta verificada exitosamente! Ahora puedes iniciar sesión.')
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, 'Error al encontrar el usuario.')
        else:
            messages.error(request, 'Código incorrecto. Inténtalo de nuevo.')

    # Reutilizamos tu template verificacion_2fa.html
    return render(request, 'Marketplace_App/formularios/verificacion_2fa.html')

@login_required
def verificar_telefono(request):
    # Obtenemos o creamos el perfil del usuario actual
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        
        if telefono:
            # 1. Guardamos el número en el perfil (marcado como NO verificado aún)
            perfil.telefono_contacto = telefono
            perfil.telefono_verificado = False 
            perfil.save()
            
            # 2. Generamos código aleatorio de 6 dígitos
            codigo = random.randint(100000, 999999)
            
            # 3. Guardamos el código en la sesión (memoria temporal)
            request.session['sms_codigo'] = codigo
            
            # 4. SIMULACIÓN: Imprimir en la consola negra (Terminal)
            print(f"\n{'='*40}")
            print(f" >>> SIMULACIÓN SMS A {telefono} <<<")
            print(f" >>> CÓDIGO: {codigo} <<<")
            print(f"{'='*40}\n")
            
            messages.info(request, f"Te enviamos un código de verificación al {telefono}.")
            return redirect('validar_codigo_telefono')
        else:
            messages.error(request, "Por favor ingresa un número válido.")
            
    return render(request, 'Marketplace_App/formularios/verificar_telefono.html', {'perfil': perfil})

@login_required
def validar_codigo_telefono(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_real = request.session.get('sms_codigo')
        
        # --- INICIO DEPURACIÓN (Míralo en tu consola negra) ---
        print(f"--- DEBUG VERIFICACIÓN ---")
        print(f"Código en Sesión (Real): {codigo_real} (Tipo: {type(codigo_real)})")
        print(f"Código Ingresado (User): {codigo_ingresado} (Tipo: {type(codigo_ingresado)})")
        # ----------------------------------------------------

        # CORRECCIÓN: Convertir ambos a string y usar .strip() para quitar espacios
        if codigo_real and str(codigo_ingresado).strip() == str(codigo_real):
            
            # ¡ÉXITO!
            perfil = request.user.perfil
            perfil.telefono_verificado = True
            perfil.save()
            
            # Limpiamos sesión
            if 'sms_codigo' in request.session:
                del request.session['sms_codigo']
            
            messages.success(request, "¡Teléfono verificado correctamente!")
            return redirect('crear_anuncio') 
        else:
            messages.error(request, "Código incorrecto. Inténtalo de nuevo.")
            
    return render(request, 'Marketplace_App/formularios/validar_codigo_telefono.html')

# --- 4. PERFIL DE USUARIO ---
@login_required
def mi_perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    form_perfil = PerfilUsuarioForm(instance=perfil)

    mis_anuncios_qs = Anuncio.objects.filter(usuario=request.user).order_by('-fecha_publicacion')
    anuncios_con_forms = []
    
    for anuncio in mis_anuncios_qs:
        form = AnuncioForm(instance=anuncio)
        anuncios_con_forms.append((anuncio, form))

    context = {
        'perfil': perfil,
        'form_perfil': form_perfil,
        'anuncios_con_forms': anuncios_con_forms
    }
    return render(request, 'Marketplace_App/usuarios/mi_perfil.html', context)

@login_required
def editar_perfil(request):
    """Procesa el POST del modal de perfil"""
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        
        if form.is_valid():
            # --- PARCHE DE SEGURIDAD ---
            # Verificamos si el usuario tocó el campo del teléfono
            if 'telefono_contacto' in form.changed_data:
                # Si cambió el número (o lo borró), reseteamos la verificación
                instancia = form.save(commit=False)
                instancia.telefono_verificado = False
                instancia.save()
                
                # Opcional: Avisar al usuario si borró el número
                if not instancia.telefono_contacto:
                     messages.warning(request, 'Has eliminado tu teléfono. Necesitarás verificar uno nuevo para publicar.')
                else:
                     messages.info(request, 'Al cambiar tu número, deberás verificarlo nuevamente para publicar.')
            else:
                # Si no tocó el teléfono, guardamos normal
                form.save()
            # ---------------------------

            messages.success(request, 'Perfil actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el perfil.')
            
    return redirect('mi_perfil')