from django.urls import path
from GraphLingo import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dialog/", views.DialogView.as_view(), name="dialog")
]