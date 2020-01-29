from django.urls import path
from .views import TestWorker

urlpatterns = [
    path('test/', TestWorker.as_view())
]
