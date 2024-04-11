from django.urls import path

from . import views

urlpatterns = [
    path("", views.CalendarViewNew.as_view(), name="calendars"),
]