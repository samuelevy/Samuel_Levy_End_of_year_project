from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import AppUser

class CreateUserForm(UserCreationForm):
    name=forms.CharField(max_length=255,required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Name'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
            'class': 'form-input'
        })
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'class': 'form-input'
        })
    )
    
    class Meta:
        model = AppUser
        fields = ['name', 'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if AppUser.objects.filter(name=name).exists():
            raise forms.ValidationError("Username taken. Please choose another.")
        return name