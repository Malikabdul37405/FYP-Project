from django.db import models
from django.contrib.auth.models import User

class UploadedImage(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField('First Name',max_length=100) 
    last_name = models.CharField('Last Name',max_length=100)
    gender = models.CharField('Gender',max_length=10, choices=GENDER_CHOICES) 
    age = models.PositiveIntegerField('Age')            
    description = models.TextField('Description',blank=True)     
    image = models.ImageField('Image',upload_to='uploads/') 
    uploaded_at = models.DateTimeField('Uploaded At',auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"

class ContactInfo(models.Model):
    address = models.CharField('Address', max_length=255, default="2nd Flr, Chaudhary Plaza, Rawalpindi")
    phone = models.CharField('Phone', max_length=16, default="+92-331-6262-363")
    email = models.EmailField('Email', default="admin@info.com")
    
    def __str__(self):
        return "Contact Information"