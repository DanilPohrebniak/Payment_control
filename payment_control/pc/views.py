from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from .utils import Calendar
from .models import Event
from .forms import EventForm


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

def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

class CalendarViewNew(generic.ListView):
    template_name = "calendarapp/calendar.html"
    form_class = EventForm

    def get(self, request, *args, **kwargs):
        # request.user
        forms = self.form_class()
        events = Event.objects.get_all_events(user=1)
        events_month = Event.objects.get_running_events(user=1)
        event_list = []
        for event in events:
            print(event.end_time.strftime("%Y-%m-%dT%H:%M:%S"))
            event_list.append(
                {
                    "title": event.title,
                    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end111": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "description": event.description,
                    "id": event.id,
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
            form.user = User.objects.get(pk=1)
            form.save()
            return redirect("calendars")
        context = {"form": forms}
        return render(request, self.template_name, context)