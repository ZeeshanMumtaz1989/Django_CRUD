

from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

# class CreateUserForm(UserCreationForm):
#     class Meta():
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']



# class ChangeUserPassword(PasswordChangeForm):
#     class Meta():
#         model = User
#         fields = ['old_password', 'new_password1', 'new_password2']




class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)






