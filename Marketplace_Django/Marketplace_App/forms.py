from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    email = forms.EmailField(label='Correo Electrónico')
    message = forms.CharField(label='Mensaje', widget=forms.Textarea)
    
class RegisterForm(forms.Form):
    username = forms.CharField(label='Nombre de Usuario', max_length=100)
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir Contraseña', widget=forms.PasswordInput)
    
class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de Usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)