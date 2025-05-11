# lung_disease/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientProfile,PatientReport, DoctorProfile
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        required=True
    )
    age = forms.IntegerField(min_value=0, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'gender', 'age', 'email', 'password1', 'password2']

class PatientProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = PatientProfile
        fields = ['first_name', 'last_name', 'age']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data['email']
                self.user.save()
        return profile
    
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = PatientReport
        fields = ['description', 'image']

class DoctorRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
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
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            doctor_profile = DoctorProfile(
                user=user,
                full_name=self.cleaned_data['full_name'],
                specialization=self.cleaned_data['specialization'],
                license_number=self.cleaned_data['license_number'],
                documents=self.cleaned_data.get('documents')
            )
            doctor_profile.save()
        return user

class DoctorProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = DoctorProfile
        fields = ['full_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data['email']
                self.user.save()
        return profile

"""
class DoctorProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = DoctorProfile
        fields = ['full_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        # Additional strict format check (optional)
        import re
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            raise ValidationError("Please enter a valid email address.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data['email']
                self.user.save()
        return profile

class DoctorProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = DoctorProfile
        fields = ['full_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Custom validation: only allow a-z, A-Z, 0-9, ".", "@", must end with .com
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
        if not re.match(pattern, email):
            raise ValidationError("Enter a valid email address that ends with '.com' and uses only allowed characters.")

        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data['email']
                self.user.save()
        return profile"""
class DoctorAssistanceRequestForm(forms.Form):
    report = forms.ModelChoiceField(
        queryset=PatientReport.objects.none(),  # fix here
        label="Select a report to request assistance",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['report'].queryset = PatientReport.objects.filter(
            patient__user=user,
            needs_doctor_assistance=False
        )