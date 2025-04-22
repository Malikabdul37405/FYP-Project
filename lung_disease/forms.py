# lung_disease/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UploadedImage, DoctorProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['first_name', 'last_name', 'gender', 'age', 'description', 'image']

class DoctorRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = DoctorProfile
        fields = ['full_name', 'specialization', 'license_number', 'documents']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor