from django.urls import path
from .views import UserLoginView, UserLogoutView, ChangePasswordView, PasswordResetView, PasswordResetConfirmView


urlpatterns = [
    path('api/login/', UserLoginView.as_view(), name='user-login'),    
    path('api/logout/', UserLogoutView.as_view(), name='logout_user'),

    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    
]
