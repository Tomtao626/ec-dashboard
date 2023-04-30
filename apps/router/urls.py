from django.urls import path
from .views import *

urlpatterns = [
    path("ruleendpoint/", RuleEndPointView.as_view()),
    path("ruleendpoint/<str:namespace>/", RuleEndPointView.as_view()),
    path("ruleendpoint/<str:namespace>/<str:name>/", RuleEndPointView.as_view()),

    path("rule/", RuleView.as_view()),
    path("rule/<str:namespace>/", RuleView.as_view()),
    path("rule/<str:namespace>/<str:name>/", RuleView.as_view()),
]
