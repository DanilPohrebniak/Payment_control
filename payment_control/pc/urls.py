from django.urls import path

from . import views

urlpatterns = [
    path("", views.CalendarViewNew.as_view(), name="calendars"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('update_event/<int:event_id>/', views.update_event, name='update_event'),
]