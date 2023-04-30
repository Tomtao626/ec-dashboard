from django.urls import path
from .views import *

urlpatterns = [
    path("devicemodel/", DeviceModelView.as_view()),
    path("devicemodel/<str:namespace>/", DeviceModelView.as_view()),
    path("devicemodel/<str:namespace>/<str:name>/", DeviceModelView.as_view()),

    path("device/", DeviceView.as_view()),
    path("device/<str:namespace>/", DeviceView.as_view()),
    path("device/<str:namespace>/<str:name>/", DeviceView.as_view()),
]
