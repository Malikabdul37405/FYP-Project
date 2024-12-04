
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),               # Home page
    path('register/', views.register, name='register'),  # Registration page
    path('login/', views.user_login, name='login'),      # Login page
    path('logout/', views.user_logout, name='logout'),   # Logout functionality
    path('blog/', views.blog, name='blog'),              # Blog page
    path('contact/', views.contact_view, name='contact'),     # Contact us page
    path('contact/submit/', views.contact, name='contact_submit'), 
    path('result/', views.result, name='result'),

]
