from django.shortcuts import redirect
from django.urls import reverse

class VerificacionDosPasosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de rutas permitidas sin verificación (Login, Logout, Admin, y la propia verificación)
        rutas_excluidas = [
            reverse('login'),
            reverse('logout'),
            reverse('registro'),
            reverse('verificacion_2fa'),
        ]
        
        # También excluimos rutas estáticas o de admin si es necesario
        if request.path.startswith('/static/') or request.path.startswith('/media/') or request.path.startswith('/admin/'):
            return self.get_response(request)

        # LÓGICA DEL GUARDIA:
        # Si el usuario está autenticado...
        if request.user.is_authenticated:
            # ...y NO tiene la marca de verificado en su sesión...
            if not request.session.get('2fa_verificado'):
                # ...y no está intentando ir a una ruta permitida...
                if request.path not in rutas_excluidas:
                    # ...¡LO MANDAMOS A VERIFICAR!
                    return redirect('verificacion_2fa')

        response = self.get_response(request)
        return response