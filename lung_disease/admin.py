from django.contrib import admin
from .models import UploadedImage

class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'uploaded_at')  # Fields to display in the admin panel
    search_fields = ('user__username',)             # Search functionality by username
    list_filter = ('uploaded_at',)                  # Filter by upload date

admin.site.register(UploadedImage, UploadedImageAdmin)