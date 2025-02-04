from django.urls import path
from .views import UserCSVUploadView

urlpatterns = [
    path('upload-csv/', UserCSVUploadView.as_view(), name='upload-csv'),
]