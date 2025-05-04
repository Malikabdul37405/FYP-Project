import os
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from .forms import UserRegisterForm, ImageUploadForm, DoctorRegisterForm, DoctorAssistanceRequestForm
from .models import PatientProfile, ContactInfo, Blog, DoctorProfile, ContactMessage
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.activations import swish
import tensorflow as tf



# Register the swish activation function
@tf.keras.utils.register_keras_serializable()
def custom_swish(x):
    return swish(x)


# ✅ Correct model path
MODEL_PATH = os.path.join(settings.BASE_DIR, 'lung_disease', 'mcnn_trained_model.h5')

# ✅ Load the model safely
if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH, custom_objects={"swish": custom_swish})
else:
    model = None
    print("⚠️ Model file not found! Please check 'mcnn_trained_model.h5' in 'lung_disease' folder.")

# ✅ Class labels for predictions
CLASS_LABELS = ["Benign", "Malignant", "Normal", "Pneumonia"]

"""# Register the swish activation function
@tf.keras.utils.register_keras_serializable()
#def custom_swish(x):
def swish_activation(x):
    #return swish(x)
    return tf.keras.activations.swish(x)


# ✅ Correct model path
MODEL_PATH = os.path.join(settings.BASE_DIR, 'lung_disease', 'TZH_4mcnn_trained_model.h5')

# ✅ Load the model safely
if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH, custom_objects={"swish_activation": swish_activation})
else:
    model = None
    print("⚠️ Model file not found! Please check 'TZH_4mcnn_trained_model.h5' in 'lung_disease' folder.")

# ✅ Class labels for predictions
CLASS_LABELS = ["Benign", "Malignant", "Normal", "Pneumonia"]"""

# Home Page (Handles Image Upload)
def home(request):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()

            # Store the uploaded image ID in session
            request.session['latest_image_id'] = image.id

            messages.success(request, "Image uploaded successfully!")
            return redirect('result')  # Redirect to result page
    else:
        form = ImageUploadForm()

    return render(request, 'home.html', {'form': form})


# Result Page (Performs AI-based Prediction)
def result(request):
    image_id = request.session.get('latest_image_id')
    if not image_id:
        messages.error(request, "No image to display. Please upload an image.")
        return redirect('home')

    try:
        latest_image = PatientProfile.objects.get(id=image_id)
    except PatientProfile.DoesNotExist:
        messages.error(request, "Image not found.")
        return redirect('home')

    if model is None:
        messages.error(request, "AI model is missing! Please contact support.")
        return redirect('home')

    img_path = latest_image.image.path
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    predicted_label = CLASS_LABELS[predicted_class]

    # Save the prediction to the model
    latest_image.prediction = predicted_label
    latest_image.save()

    return render(request, 'patient/result.html', {
        'latest_image': latest_image,
        'prediction': predicted_label
    })

# User Registration Orignal
"""def sign_up(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate the form
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'sign_up.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'sign_up.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'sign_up.html')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        login(request, user)
        messages.success(request, "Registration successful! Welcome!")
        return redirect('login')

    return render(request, 'sign_up.html')"""

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
            messages.success(request, "Registration successful! Welcome!")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'sign_up.html', {'form': form})

# User Login Orignal
"""def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')

        messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html', {'form': AuthenticationForm()})"""

"""def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")

            try:
                # Check if user is a doctor
                doctor_profile = DoctorProfile.objects.get(user=user)
                if doctor_profile.verified:
                    return redirect('doctor_portal')
                else:
                    return render(request, 'doctor/unverified.html')
            except DoctorProfile.DoesNotExist:
                # Not a doctor, redirect to patient/home dashboard
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else 'home')

        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'form': AuthenticationForm()})"""

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.GET.get('next')
            # 🧠 Doctor check here
            if hasattr(user, 'doctorprofile'):
                return redirect('doctor_portal')

            return redirect(next_url if next_url else 'home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # 🔁 Redirect after failed POST
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# User Logout
def user_logout(request):
    logout(request)
    return redirect('home')


# Blog Pages
def blog(request):
    return render(request, 'patient/blog.html', {'blogs': Blog.objects.all()})


def blog_detail(request, blog_id):
    return render(request, 'patient/blog_detail.html', {'blog': get_object_or_404(Blog, id=blog_id)})


# Contact Page

def contact(request):
    contact_info = ContactInfo.objects.first()
    if not contact_info:
        contact_info = ContactInfo.objects.create(
            address="2nd Flr, Chaudhary Plaza, Rawalpindi",
            phone="+92-331-6262-363",
            email="default@example.com"
        )
        
    if request.method == "POST":
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Create the message
        contact_message = ContactMessage(
            full_name=name,
            email=email,
            message=message
        )
        
        if request.user.is_authenticated:
            contact_message.user = request.user 

        contact_message.save()

        messages.success(request, "Thank you for reaching out!")
        return redirect('contact')

    return render(request, 'patient/contact.html', {'contact_info': contact_info})

# Doctor Blog Pages
def doctor_blog(request):
    return render(request, 'doctor/doctor_blog.html', {'blogs': Blog.objects.all()})


def doctor_blog_detail(request, blog_id):
    return render(request, 'doctor/doctor_blog_detail.html', {'blog': get_object_or_404(Blog, id=blog_id)})

# Doctor Contact Page
def doctor_contact(request):
    contact_info = ContactInfo.objects.first()
    if not contact_info:
        contact_info = ContactInfo.objects.create(
            address="2nd Flr, Chaudhary Plaza, Rawalpindi",
            phone="+92-331-6262-363",
            email="default@example.com"
        )
        
    if request.method == "POST":
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Create the message
        contact_message = ContactMessage(
            full_name=name,
            email=email,
            message=message
        )
        
        if request.user.is_authenticated:
            contact_message.user = request.user 

        contact_message.save()

        messages.success(request, "Thank you for reaching out!")
        return redirect('doctor_contact')

    return render(request, 'doctor/doctor_contact.html', {'contact_info': contact_info})


"""@login_required
def dashboard(request):
    # Get all patient records uploaded by the currently logged-in user
    patient_records = PatientProfile.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'dashboard.html', {
        'patient_records': patient_records
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('dashboard') + '?success=1')
        else:
            error_message = "Password change failed. Please check your inputs."
            return HttpResponseRedirect(reverse('dashboard') + f'?error={error_message}')"""

@login_required
def dashboard(request):
    patient_records = PatientProfile.objects.filter(user=request.user)
    form = PasswordChangeForm(user=request.user)

    return render(request, 'patient/profile.html', {
        'patient_records': patient_records,
        'form': form,
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully!")
            return redirect('dashboard')
        else:
            patient_records = PatientProfile.objects.filter(user=request.user)
            return render(request, 'patient/dashboard.html', {
                'patient_records': patient_records,
                'form': form
            })
    return redirect('dashboard')

def delete_record(request, record_id):
    record = get_object_or_404(PatientProfile, id=record_id, user=request.user)
    if request.method == 'POST':
        record.delete()
    return redirect('dashboard') 

@login_required
def doctor_portal(request):
    """doctor = DoctorProfile.objects.get(user=request.user)  #Orignal
    if not doctor.verified:
        return render(request, 'doctor/unverified.html')
    return render(request, 'doctor/doctor_portal.html', {'doctor': doctor})"""
    doctor = DoctorProfile.objects.get(user=request.user)

    if not doctor.verified:
        return render(request, 'doctor/unverified.html', {'doctor': doctor})

    # Fetch reports
    pending_reports = PatientProfile.objects.filter(needs_doctor_assistance=True, reviewed_by=None)
    reviewed_reports = PatientProfile.objects.filter(reviewed_by=request.user)

    context = {
        'doctor': doctor,
        'pending_reports': pending_reports,
        'reviewed_reports': reviewed_reports,
    }
    return render(request, 'doctor/doctor_portal.html', context)

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
def give_assistance(request, report_id):
    doctor = DoctorProfile.objects.get(user=request.user)
    report = get_object_or_404(PatientProfile, id=report_id, needs_doctor_assistance=True, reviewed_by=None)

    if request.method == 'POST':
        doctor_comment = request.POST.get('doctor_comment', '').strip()
        if doctor_comment:
            report.doctor_comment = doctor_comment
            report.reviewed_by = request.user
            report.doctor_name = doctor.full_name
            report.save()
            messages.success(request, "Advice submitted successfully!")
        else:
            messages.error(request, "Advice cannot be empty.")

    return redirect('doctor_portal')

@login_required
def view_doctor_responses(request):
    reports = PatientProfile.objects.filter(user=request.user, needs_doctor_assistance=True)

    return render(request, 'patient/view_responses.html', {'reports': reports})

@login_required
def doctor_dashboard(request):
    form = PasswordChangeForm(user=request.user)

    return render(request, 'doctor/doctor_profile.html', {'form': form,})

@login_required
def doctor_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully!")
            return redirect('doctor_dashboard')
        else:
            return render(request, 'doctor/doctor_dashboard.html', {
                'form': form
            })
    return redirect('doctor_dashboard')

