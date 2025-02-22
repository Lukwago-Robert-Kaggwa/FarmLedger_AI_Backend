from django.urls import path
from .views import UserSignUpView, UserLoginView, UpdateUserView

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('update-user/', UpdateUserView.as_view(), name='update-user'),
]
