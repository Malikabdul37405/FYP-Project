from django.contrib import admin
from .models import UploadedImage, Blog, ContactInfo

class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'uploaded_at')  # Fields to display in the admin panel
    search_fields = ('user__username',)             # Search functionality by username
    list_filter = ('uploaded_at',)                  # Filter by upload date

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author')  # Allow search by author
    list_filter = ('created_at', 'author')  # Filter blogs by author

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('address', 'phone', 'email')





admin.site.register(UploadedImage, UploadedImageAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
