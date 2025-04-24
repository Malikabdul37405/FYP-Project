
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),               # Home page
    path('register/', views.register, name='register'),  # Registration page
    path('login/', views.user_login, name='login'),      # Login page
    path('logout/', views.user_logout, name='logout'),   # Logout functionality
    path('blog/', views.blog, name='blog'),              # Blog page
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact_view, name='contact'),     # Contact us page
    path('contact/submit/', views.contact, name='contact_submit'), 
    path('result/', views.result, name='result'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-record/<int:record_id>/', views.delete_record, name='delete_record'),
    #path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
]
