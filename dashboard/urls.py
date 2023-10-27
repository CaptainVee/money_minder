from django.urls import path
from .views import (
    dashboard,
)

# app_name = "courses"

urlpatterns = [
    path("", dashboard, name="home"),
]

