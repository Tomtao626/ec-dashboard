from django.urls import path
from .views import TestView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("test/", TestView.as_view()),
    path("api/token/", TokenObtainPairView.as_view()),
]
