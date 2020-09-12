from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):


    class Meta:
        model = User
        fields = ('first_name','last_name','username', 'email', 'password1', 'password2', )

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}),max_length=254)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
