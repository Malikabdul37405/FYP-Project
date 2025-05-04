
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),               # Home page
    path('sign_up/', views.sign_up, name='sign_up'),  # Registration page
    path('login/', views.user_login, name='login'),      # Login page
    path('logout/', views.user_logout, name='logout'),   # Logout functionality
    path('assistance/', views.request_doctor_assistance, name='assistance'),    # doctor assistance
    path('patient/blog/', views.blog, name='blog'),              # Blog page
    path('patient/blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('patient/contact/', views.contact, name='contact'),   # Contact us page
    path('patient/result/', views.result, name='result'),
    path('patient/dashboard/', views.dashboard, name='dashboard'),
    path('patient/change-password/', views.change_password, name='change_password'),
    path('delete-record/<int:record_id>/', views.delete_record, name='delete_record'),
    path('doctor/portal/', views.doctor_portal, name='doctor_portal'),
    path('doctor/give-assistance/<int:report_id>/', views.give_assistance, name='give_assistance'),
    path('responses/', views.view_doctor_responses, name='view_responses'),
    path('doctor_blog/', views.doctor_blog, name='doctor_blog'),         # Doctor Blog page
    path('doctor_blog/<int:blog_id>/', views.doctor_blog_detail, name='doctor_blog_detail'),
    path('doctor_contact/', views.doctor_contact, name='doctor_contact'),     # Doctor Contact us page
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_change-password/', views.doctor_change_password, name='doctor_change_password'),
]
