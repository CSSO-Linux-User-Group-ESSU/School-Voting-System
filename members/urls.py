from django.urls import path
from . import views

urlpatterns = [
    path("ESSUxLUG", views.members, name="ESSUxLUG")
]