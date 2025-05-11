# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import DoctorProfile

@receiver(post_save, sender=DoctorProfile)
def send_admin_notification_on_new_doctor(sender, instance, created, **kwargs):
    if created and not instance.verified:
        subject = 'New Doctor Registration Pending Verification'
        message = (
            f"A new doctor has registered and needs verification:\n\n"
            f"Name: {instance.full_name}\n"
            f"Specialization: {instance.specialization}\n"
            f"License No: {instance.license_number}\n"
            f"Email: {instance.user.email}\n\n"
            f"Please log into the admin panel to verify the doctor."
        )
        admin_emails = [email for _, email in settings.ADMINS]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
