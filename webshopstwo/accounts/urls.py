from django.urls import path
from .views import LoginView, RegisterView, SendCodeView, VerifyCodeView, LogoutView , UserProfileView

urlpatterns = [
    path("send-code/", SendCodeView.as_view(), name="send-code"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name='profile'),
]