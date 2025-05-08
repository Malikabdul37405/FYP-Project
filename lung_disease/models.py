from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    documents = models.FileField(upload_to='doctor_documents/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.full_name} ({'Verified' if self.verified else 'Pending'})"
    

class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    gender = models.CharField('Gender', max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField('Age')

    def __str__(self):
        return f"{self.user.username} - {self.first_name} {self.last_name}"


class PatientReport(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reports')
    image = models.ImageField('Image', upload_to='uploads/')
    uploaded_at = models.DateTimeField('Uploaded At', auto_now_add=True)
    description = models.TextField('Description', blank=True)
    prediction = models.CharField('Prediction Result', max_length=100, blank=True, null=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_patients')
    doctor_name = models.CharField('Doctor Name', max_length=255, blank=True, null=True)
    doctor_comment = models.TextField(blank=True, null=True)
    needs_doctor_assistance = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for {self.patient.user.username} - {self.image.name}"

class Blog(models.Model):
    title = models.CharField('Title', max_length=255)
    content = RichTextField('Content')
    image = models.ImageField('Image', upload_to='blog_images/', blank=True, null=True)
    author = models.CharField('Author', max_length=200)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']  # Order by the latest first

class ContactInfo(models.Model):
    address = models.CharField('Address', max_length=255, default="2nd Flr, Chaudhary Plaza, Rawalpindi")
    phone = models.CharField('Phone', max_length=16, default="+92-331-6262-363")
    email = models.EmailField('Email', default="admin@info.com")
    
    def __str__(self):
        return "Contact Information"

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.full_name}"
