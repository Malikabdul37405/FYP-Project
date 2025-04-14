import os
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, ImageUploadForm
from .models import UploadedImage, ContactInfo, Blog
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
    image_id = request.session.get('latest_image_id')  # Retrieve image ID from session
    if not image_id:
        messages.error(request, "No image to display. Please upload an image.")
        return redirect('home')

    try:
        latest_image = UploadedImage.objects.get(id=image_id)
    except UploadedImage.DoesNotExist:
        messages.error(request, "Image not found.")
        return redirect('home')

    if model is None:
        messages.error(request, "AI model is missing! Please contact support.")
        return redirect('home')

    # Load and preprocess the uploaded image
    img_path = latest_image.image.path
    img = image.load_img(img_path, target_size=(224, 224))  # Resize to model's input size
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Convert to batch format
    img_array /= 255.0  # Normalize the image

    # Make a prediction
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)  # Get the index of the highest probability
    predicted_label = CLASS_LABELS[predicted_class]  # Map index to class label

    return render(request, 'result.html', {'latest_image': latest_image, 'prediction': predicted_label})


# User Registration
def register(request):
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
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'register.html')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        login(request, user)
        messages.success(request, "Registration successful! Welcome!")
        return redirect('login')

    return render(request, 'register.html')


# User Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')

        messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html', {'form': AuthenticationForm()})


# User Logout
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# Blog Pages
def blog(request):
    return render(request, 'blog.html', {'blogs': Blog.objects.all()})


def blog_detail(request, blog_id):
    return render(request, 'blog_detail.html', {'blog': get_object_or_404(Blog, id=blog_id)})


# Contact Page
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactInfo.objects.create(address=name, phone=message, email=email)

        messages.success(request, "Thank you for reaching out! We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'contact.html')


# Contact Info Display
def contact_view(request):
    contact_info = ContactInfo.objects.first()
    if not contact_info:
        contact_info = ContactInfo.objects.create(
            address="2nd Flr, Chaudhary Plaza, Rawalpindi",
            phone="+92-331-6262-363",
            email="default@example.com"
        )
    return render(request, 'contact.html', {'contact_info': contact_info})
