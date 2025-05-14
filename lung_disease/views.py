import os
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

from .forms import UserRegisterForm, ImageUploadForm, DoctorRegisterForm, DoctorAssistanceRequestForm, PatientProfileUpdateForm, DoctorProfileUpdateForm
from .models import PatientProfile, PatientReport, ContactInfo, Blog, DoctorProfile, ContactMessage

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.activations import swish
import tensorflow as tf

@tf.keras.utils.register_keras_serializable()
def custom_swish(x):
    return swish(x)

MODEL_PATH = os.path.join(settings.BASE_DIR, 'lung_disease', 'TZH_MCNN_Model.h5')

if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH, custom_objects={"swish": custom_swish})
else:
    model = None
    print("⚠️ Model file not found! Please check the path.")

CLASS_LABELS = ["Benign", "Malignant", "Normal", "Pneumonia", "Not_pridicted"]

# ---------------- SIGNUP ----------------
def sign_up(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')

        if user_type == 'doctor':
            form = DoctorRegisterForm(request.POST, request.FILES)
        else:
            form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            # Create PatientProfile if user is patient
            if user_type != 'doctor':
                PatientProfile.objects.create(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    gender=form.cleaned_data['gender'],
                    age=form.cleaned_data['age']
                )

            messages.success(request, "Registration successful! Welcome!")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'sign_up.html', {'form': form})

# ---------------- LOGIN ----------------
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')

            if hasattr(user, 'doctorprofile'):
                return redirect('doctor_portal')

            return redirect(next_url if next_url else 'home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

# ---------------- HOME / UPLOAD IMAGE ----------------
@login_required
def home(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            patient_profile = get_object_or_404(PatientProfile, user=request.user)
            new_report = PatientReport(
                patient=patient_profile,
                image=form.cleaned_data['image'],
                description=form.cleaned_data['description']
            )
            new_report.save()

            request.session['latest_report_id'] = new_report.id
            messages.success(request, "Image uploaded successfully!")
            return redirect('result')
    else:
        form = ImageUploadForm()

    return render(request, 'home.html', {'form': form})

# ---------------- RESULT ----------------
@login_required
def result(request):
    report_id = request.session.get('latest_report_id')
    if not report_id:
        messages.error(request, "No image to display. Please upload an image.")
        return redirect('home')

    try:
        report = PatientReport.objects.get(id=report_id)
    except PatientReport.DoesNotExist:
        messages.error(request, "Image not found.")
        return redirect('home')

    if model is None:
        messages.error(request, "AI model is missing! Please contact support.")
        return redirect('home')

    img_path = report.image.path
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    predicted_label = CLASS_LABELS[predicted_class]

    report.prediction = predicted_label
    report.save()

    return render(request, 'patient/result.html', {
        'latest_image': report,
        'prediction': predicted_label
    })

# ---------------- profile ----------------
@login_required
def profile(request):
    patient_profile = get_object_or_404(PatientProfile, user=request.user)
    reports = PatientReport.objects.filter(patient=patient_profile)
    password_form = PasswordChangeForm(user=request.user)
    profile_form = PatientProfileUpdateForm(instance=patient_profile, user=request.user)

    return render(request, 'patient/profile.html', {
        'patient_profile': patient_profile,
        'patient_records': reports,
        'form': password_form,
        'profile_form': profile_form,
    })

@login_required
def update_profile(request):
    patient_profile = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = PatientProfileUpdateForm(request.POST, instance=patient_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Please try again.")
    return redirect('profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Password miss matches. Try Again")
    return redirect('profile')

@login_required
def delete_record(request, record_id):
    patient_profile = get_object_or_404(PatientProfile, user=request.user)
    record = get_object_or_404(PatientReport, id=record_id, patient=patient_profile)

    if request.method == 'POST':
        record.delete()
    return redirect('profile')

# ---------------- DOCTOR PORTAL ----------------
@login_required
def doctor_portal(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    if not doctor.verified:
        return render(request, 'doctor/unverified.html', {'doctor': doctor})

    # Use select_related to follow ForeignKey and OneToOneField efficiently
    pending_reports = PatientReport.objects.filter(
        needs_doctor_assistance=True,
        reviewed_by=None
    ).select_related('patient', 'patient__user')

    reviewed_reports = PatientReport.objects.filter(
        reviewed_by=request.user
    ).select_related('patient', 'patient__user')

    return render(request, 'doctor/doctor_portal.html', {
        'doctor': doctor,
        'pending_reports': pending_reports,
        'reviewed_reports': reviewed_reports,
    })


@login_required
def give_assistance(request, report_id):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    report = get_object_or_404(PatientReport, id=report_id, needs_doctor_assistance=True, reviewed_by=None)

    if request.method == 'POST':
        comment = request.POST.get('doctor_comment', '').strip()
        if comment:
            report.doctor_comment = comment
            report.reviewed_by = request.user
            report.doctor = doctor
            report.doctor_name = doctor.full_name
            report.save()
            messages.success(request, "Advice submitted successfully!")
        else:
            messages.error(request, "Advice cannot be empty.")

    return redirect('doctor_portal')

@login_required
def request_doctor_assistance(request):
    if request.method == 'POST':
        form = DoctorAssistanceRequestForm(request.user, request.POST)
        if form.is_valid():
            report = form.cleaned_data['report']
            report.needs_doctor_assistance = True
            report.save()
            messages.success(request, "Doctor assistance requested successfully.")
            return redirect('home')
    else:
        form = DoctorAssistanceRequestForm(request.user)

    return render(request, 'patient/request_assistance.html', {'form': form})

@login_required
def view_doctor_responses(request):
    patient_profile = get_object_or_404(PatientProfile, user=request.user)
    reports = PatientReport.objects.filter(patient=patient_profile, needs_doctor_assistance=True)
    return render(request, 'patient/view_responses.html', {'reports': reports})

@login_required
def doctor_profile(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    profile_form = DoctorProfileUpdateForm(instance=doctor, user=request.user)
    form = PasswordChangeForm(user=request.user)
    return render(request, 'doctor/doctor_profile.html', {
        'doctor': doctor,
        'form': form,
        'profile_form':profile_form,
        })

@login_required
def update_doctor_profile(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        form = DoctorProfileUpdateForm(request.POST, instance=doctor_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Please try again.")
    return redirect('doctor_profile')

@login_required
def doctor_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully!")
            return redirect('doctor_profile')
        else:
            messages.error(request, "Password miss matches. Try Again")
    return redirect('doctor_profile')

# ---------------- BLOG & CONTACT ----------------
def blog(request):
    return render(request, 'patient/blog.html', {'blogs': Blog.objects.all()})

def blog_detail(request, blog_id):
    return render(request, 'patient/blog_detail.html', {'blog': get_object_or_404(Blog, id=blog_id)})

def contact(request):
    contact_info = ContactInfo.objects.first() or ContactInfo.objects.create(
        address="2nd Flr, Chaudhary Plaza, Rawalpindi",
        phone="+92-331-6262-363",
        email="default@example.com"
    )

    if request.method == "POST":
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contact_message = ContactMessage(full_name=name, email=email, message=message)
        if request.user.is_authenticated:
            contact_message.user = request.user
        contact_message.save()
        messages.success(request, "Thank you for reaching out!")
        return redirect('contact')

    return render(request, 'patient/contact.html', {'contact_info': contact_info})

def doctor_contact(request):
    contact_info = ContactInfo.objects.first()

    if request.method == "POST":
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contact_message = ContactMessage(full_name=name, email=email, message=message)
        if request.user.is_authenticated:
            contact_message.user = request.user
        contact_message.save()
        messages.success(request, "Thank you for reaching out!")
        return redirect('doctor_contact')

    return render(request, 'doctor/doctor_contact.html', {'contact_info': contact_info})

def doctor_blog(request):
    return render(request, 'doctor/doctor_blog.html', {'blogs': Blog.objects.all()})

def doctor_blog_detail(request, blog_id):
    return render(request, 'doctor/doctor_blog_detail.html', {'blog': get_object_or_404(Blog, id=blog_id)})
