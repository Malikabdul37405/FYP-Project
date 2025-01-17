from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, ImageUploadForm
from .models import UploadedImage, ContactInfo, Blog
from django.shortcuts import render, redirect



# Home Page
#@login_required
def home(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Redirect to the login page with a "next" parameter
        return redirect(f'/login/?next={request.path}')

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user  # Associate the image with the authenticated user
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
        # Get form data
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

        # Create the user with first name and last name
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Automatically log the user in after registration
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

            # Redirect to the page the user was trying to access, or home
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
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
    blogs = Blog.objects.all()  # Fetch all blog posts
    return render(request, 'blog.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})

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


"""def contact(request):
    if request.method == "POST":
        # Process contact form submission
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the submitted form data (optional)
        ContactInfo.objects.create(address=name, phone=message, email=email)

        # Show a success message to the user
        messages.success(request, "Thank you for reaching out! We'll get back to you soon.")

        # Redirect to prevent resubmission
        return redirect('contact')

    return render(request, 'contact.html')"""


def contact_view(request):
    # Retrieve the latest ContactInfo object, or create a default one if none exists
    contact_info = ContactInfo.objects.first()
    if not contact_info:
        contact_info = ContactInfo.objects.create(
            address="2nd Flr, Chaudhary Plaza, Rawalpindi",
            phone="+92-331-6262-363",
            email="default@example.com"
        )

    # Render the page with contact info (but no form handling)
    return render(request, 'contact.html', {'contact_info': contact_info})