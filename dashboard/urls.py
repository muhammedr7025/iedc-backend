from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserRegisterAPI.as_view()),
    path('forgot-password/', views.ForgotPasswordAPI.as_view())
]
