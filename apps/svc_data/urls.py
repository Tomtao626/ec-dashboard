from django.urls import path
from .views import *

urlpatterns = [
    path("svc_data/", SvcDataView.as_view()),
]
