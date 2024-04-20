from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path("", views.CalendarViewNew.as_view(), name="calendars"),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),  # Используйте LoginView
    path('logout/', views.logout, name='logout'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('update_event/<int:event_id>/', views.update_event, name='update_event'),
    path('notes/', views.notes, name='notes_list'),
    path('add_note/', views.add_note, name='add_note'),
    path('edit_note/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete_note/<int:pk>/', views.delete_note, name='delete_note'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)