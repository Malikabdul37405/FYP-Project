# lung_disease/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientProfile, DoctorProfile
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

"""class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']"""

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['first_name', 'last_name', 'gender', 'age', 'description', 'image']

class DoctorRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True)
    specialization = forms.CharField(max_length=255, required=True)
    license_number = forms.CharField(max_length=100, required=True)
    documents = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if not license_number.isalnum():
            raise ValidationError("License number should be alphanumeric.")
        return license_number

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

class DoctorAssistanceRequestForm(forms.Form):
    report = forms.ModelChoiceField(
        queryset=PatientProfile.objects.none(),
        label="Select a report to request assistance on",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['report'].queryset = PatientProfile.objects.filter(user=user)