from django.urls import path
from .views import UserLoginView, UserLogoutView, ChangePasswordView, PasswordResetView, PasswordResetConfirmView
from rest_framework.routers import DefaultRouter
from .views import (
    UserLoginView, UserLogoutView, ChangePasswordView,
    PasswordResetView, PasswordResetConfirmView,
    AdministratorViewSet
)

router = DefaultRouter()
router.register(r'api/administrators',AdministratorViewSet, basename='administrators')



urlpatterns = [
    path('api/login/', UserLoginView.as_view(), name='user-login'),    
    path('api/logout/', UserLogoutView.as_view(), name='logout_user'),

    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    
]

urlpatterns += router.urls
