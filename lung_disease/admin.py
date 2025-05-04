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

"""from django.contrib import admin
from .models import PatientProfile, Blog, ContactInfo, DoctorProfile, ContactMessage

admin.site.site_header = "Lung Disease Admin Site"
admin.site.site_title = "Lung Disease App"
admin.site.index_title = "Welcome to the Lung Disease App Admin Panel"

# ✅ PatientProfile: can add, but not edit/delete
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'uploaded_at', 'prediction')
    search_fields = ('user__username',)
    list_filter = ('uploaded_at',)

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing existing records

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing: all fields read-only
            return [field.name for field in self.model._meta.fields]
        else:  # Adding: some fields read-only
            allowed_fields = ['user', 'first_name', 'last_name', 'gender', 'age', 'description', 'image']
            return [field.name for field in self.model._meta.fields if field.name not in allowed_fields]

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'verified']
    list_filter = ['verified']
    actions = ['verify_doctors']

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing: all fields read-only
            return [field.name for field in self.model._meta.fields]
        else:  # Adding: only some fields editable
            allowed_fields = ['user', 'full_name', 'specialization', 'license_number', 'documents']
            return [field.name for field in self.model._meta.fields if field.name not in allowed_fields]

    def verify_doctors(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f"{updated} doctor(s) successfully verified.")

    verify_doctors.short_description = "Verify selected doctors"

# Other models: normal admin
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author')
    list_filter = ('created_at', 'author')

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('address', 'phone', 'email')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user','full_name', 'email', 'message', 'created_at')

# Register all models
admin.site.register(PatientProfile, PatientProfileAdmin)
admin.site.register(DoctorProfile, DoctorAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)"""

