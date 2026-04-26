from django.urls import path

from . import views
from .views import PropertiesView
app_name = "estateAgency"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("properties/", PropertiesView.as_view(), name="properties"),
]
