from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserRegisterAPI.as_view()),
    path('login/', views.UserLoginAPI.as_view()),
    path('profile/', views.UserProfileAPI.as_view()),
    path('forgot-password/', views.ForgotPasswordAPI.as_view()),
    path('create-groups/', views.CreateBulkGroupsAPI.as_view()),
    path('assign-groups/', views.UserGroupLinkBulkCreateAPI.as_view()),
    path('qr-code-scanner/', views.QrCodeScannerAPI.as_view())
]
