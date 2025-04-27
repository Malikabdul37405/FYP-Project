from django.contrib import admin
from .models import PatientProfile, Blog, ContactInfo, DoctorProfile, ContactMessage

admin.site.site_header = "Lung Disease Admin Site"  # Title for the admin panel header
admin.site.site_title = "Lung Disease App"         # Title for the browser tab
admin.site.index_title = "Welcome to the Lung Disease App Admin Panel"  # Subtitle on the admin index page

class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'uploaded_at', 'prediction')  # Fields to display in the admin panel
    search_fields = ('user__username',)             # Search functionality by username
    list_filter = ('uploaded_at',)                  # Filter by upload date

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author')  # Allow search by author
    list_filter = ('created_at', 'author')  # Filter blogs by author

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('address', 'phone', 'email')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user','full_name', 'email', 'message', 'created_at')

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'verified']
    list_filter = ['verified']
    actions = ['verify_doctors']

    def verify_doctors(self, request, queryset):
        queryset.update(verified=True)



admin.site.register(PatientProfile, PatientProfileAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(DoctorProfile, DoctorAdmin)
