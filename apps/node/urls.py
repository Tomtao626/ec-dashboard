from django.urls import path
from .views import *

urlpatterns = [
    path("node/", NodeView.as_view()),
    path("join/", NodeJoinView.as_view()),
    path("label/", NodeLabelView.as_view()),
    path("node/<str:name>/", NodeView.as_view()),
]
