from django.urls import path
from .views import (
    home,
    collect,
    connect,
    dashboard,
)

# app_name = "courses"

urlpatterns = [
    path("", home, name="home"),
    path("collect/<uuid:user_id>/", collect, name="collect"),
    path("connect/<uuid:user_id>/", connect, name="connect"),
    path("dashboard/<uuid:user_id>/", dashboard, name="dashboard"),
]

