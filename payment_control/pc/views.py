from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from .utils import Calendar
from .models import Event, EventPhoto, Notes
from .forms import EventForm, EventPhotoForm, NotesEntryForm, CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        print(request.POST);
        # Получаем данные из POST-запроса
        password = request.POST.get('password1')  # Используем password1 для передачи пароля
        # Добавляем значения в поля password1 и password2
        request.POST = request.POST.copy()
        request.POST['password'] = password
        request.POST['password1'] = password
        request.POST['password2'] = password
        # Создаем форму с переданными данными
        print(request.POST);
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('calendars')

        print(form.errors);
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('calendars')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login')  # Redirect to your home page

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month

@login_required
def delete_event(request, event_id):
    if request.method == 'POST':
        print('method is POST')
        try:
            print('we try to delete event')
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'success': True})
        except Event.DoesNotExist:
            print('can`t delete')
            return JsonResponse({'success': False, 'error': 'Event does not exist'}, status=404)
    else:
        print('method is GET')
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


class CalendarViewNew(generic.ListView):
    template_name = "calendarapp/calendar.html"
    form_class = EventForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # request.user
        forms = self.form_class()
        events = Event.objects.filter(user=request.user)
        events_month = Event.objects.get_running_events(user=request.user)
        event_list = []
        for event in events:
            photos = list(event.photos.values_list('image', flat=True))
            event_list.append(
                {
                    "title": event.title,
                    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end_t": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "description": event.description,
                    "id": event.id,
                    "photos": photos,
                }
            )
        context = {"form": forms, "events": event_list,
                   "events_month": events_month}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            form = forms.save(commit=False)
            # Need to change it for actual user
            form.user = request.user
            form.save()
            return redirect("calendars")
        context = {"form": forms}
        return render(request, self.template_name, context)


@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        photo_form = EventPhotoForm(request.POST, request.FILES)

        if photo_form.is_valid() or not request.FILES:  # Проверяем, есть ли файлы
            form.save()

            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.event = event
                photo.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@login_required
def notes(request):
    entries = Notes.objects.filter(user=request.user)
    return render(request, 'notes/notes_list.html', {'entries': entries})


@login_required
def add_note(request):
    if request.method == 'POST':
        form = NotesEntryForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('notes_list')
    else:
        form = NotesEntryForm()
    return render(request, 'notes/add_note.html', {'form': form})


@login_required
def edit_note(request, pk):
    note = get_object_or_404(Notes, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NotesEntryForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('notes_list')
    else:
        form = NotesEntryForm(instance=note)
    return render(request, 'notes/edit_note.html', {'form': form})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Notes, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('notes_list')
    return render(request, 'notes/delete_note.html', {'note': note})
