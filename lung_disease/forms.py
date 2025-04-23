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

class DoctorRegisterForm(UserCreationForm):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=255)
    specialization = forms.CharField(max_length=255)
    license_number = forms.CharField(max_length=100)
    documents = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        doctor_profile = DoctorProfile(
            user=user,
            full_name=self.cleaned_data['full_name'],
            specialization=self.cleaned_data['specialization'],
            license_number=self.cleaned_data['license_number'],
            documents=self.cleaned_data.get('documents')
        )
        if commit:
            doctor_profile.save()
        return user