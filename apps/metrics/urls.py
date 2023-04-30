from django.urls import path
from .views import *

urlpatterns = [
    path("node/<str:name>/", MetricsNodeView.as_view()),
    path("pod/<str:namespace>/<str:name>/", MetricsPodView.as_view())
]
