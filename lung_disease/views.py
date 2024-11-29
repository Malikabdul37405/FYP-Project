from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, ImageUploadForm
from .models import UploadedImage

# Home Page
#@login_required
def home(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()

            # Save the image ID in the session
            request.session['latest_image_id'] = image.id

            messages.success(request, "Image uploaded successfully!")
            return redirect('result')  # Redirect to the result page
    else:
        form = ImageUploadForm()

    return render(request, 'home.html', {'form': form})

def result(request):
    image_id = request.session.get('latest_image_id')  # Retrieve the image ID from the session
    if not image_id:
        messages.error(request, "No image to display. Please upload an image.")
        return redirect('home')  # Redirect back to home if no image ID is found

    # Fetch the image from the database
    try:
        latest_image = UploadedImage.objects.get(id=image_id)
    except UploadedImage.DoesNotExist:
        messages.error(request, "Image not found.")
        return redirect('home')  # Redirect back to home if the image is not found

    return render(request, 'result.html', {'latest_image': latest_image})


# User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# User Logout
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# Blog Page
def blog(request):
    # Static content for now, can be expanded to fetch posts from a database
    return render(request, 'blog.html')

# Contact Us Page
def contact(request):
    if request.method == "POST":
        # Process contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Here you can save to a database or send an email
        messages.success(request, "Thank you for reaching out! We'll get back to you soon.")
        return redirect('contact')
    return render(request, 'contact.html')
