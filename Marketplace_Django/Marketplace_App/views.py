from django.shortcuts import render, HttpResponse, redirect
from Marketplace_App.forms import ContactForm, RegisterForm, LoginForm
from Marketplace_App.models import User
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'Marketplace_App/home.html', {})

def registro(request):
    
    formulario_registro = RegisterForm()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            # Aquí puedes agregar la lógica para crear el usuario en la base de datos
            usuario = User(username=username, email=email, password=password)
            usuario.save()
            
            messages.success(request, f'Cuenta creada para {username}!')
            
            return redirect(request, 'Marketplace_App/mensaje_modal.html', {})
            #return HttpResponse(f"Registro exitoso para el usuario: {str(username)}")
        else:
            return HttpResponse("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")
    
    return render(request, 'Marketplace_App/registro.html', {'formulario_registro': formulario_registro})


""" def inicio_sesion(request):
    
    formulario_login = LoginForm()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Aquí puedes agregar la lógica para autenticar al usuario
        return redirect('home')  # Redirige a la página de inicio después de iniciar sesión
    
    return render(request, 'Marketplace_App/inicio_sesion.html', {})
"""

""" def contacto(request):
    
    formulario_contacto = ContactForm()
        
    if request.method == 'POST':
        formulario_contacto = ContactForm(data=request.POST)
        if formulario_contacto.is_valid():
            nombre = request.POST.get('name', '')
            email = request.POST.get('email', '')
            mensaje = request.POST.get('message', '')
            return HttpResponse("Gracias por contactarnos, {}. Hemos recibido tu mensaje.".format(nombre))
    else:
        formulario_contacto = ContactForm()
    
    return render(request, 'Marketplace_App/contacto.html', {'formulario_contacto': formulario_contacto})
"""