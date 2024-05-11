import calendar
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from todo.apps.core import models, forms


def index(request):
    context = {}
    return render(request, 'index.html', context)


@login_required
def account(request):
    tasks = models.Task.objects.filter(executor=request.user, status__in=['created', 'processed'])
    created_tasks = tasks.order_by('-created_at')[:5]
    expired_tasks = tasks.order_by('expired_at')[:5]
    vacation = models.Vacation.objects.filter(user=request.user, status__in=['planned', 'processed']).first()

    context = {'created_tasks': created_tasks,
               'expired_tasks': expired_tasks,
               'vacation': vacation}

    return render(request, 'account/account.html', context)


@login_required
def get_tasks(request):
    n = now()
    year = int(request.GET.get('year', n.year))
    month = int(request.GET.get('month', n.month))

    if month == 13:
        year += 1
        month = 1
        previous_year = year - 1
        next_year = year
    elif month == 0:
        year -= 1
        month = 12
        previous_year = year
        next_year = year + 1
    else:
        previous_year = year
        next_year = year

    previous_month = month - 1
    next_month = month + 1

    calendar_month = calendar.Calendar().monthdays2calendar(year, month)
    tasks = models.Task.objects.filter(executor=request.user, expired_at__month=month, expired_at__year=year)
    tasks_dict = defaultdict(list)
    for task in tasks:
        tasks_dict[task.expired_at.day].append(task)

    month_name = _(calendar.month_name[month])
    month_abbr = _(calendar.month_abbr[month])
    context = {
        'month': month,
        'year': year,
        'previous_year': previous_year,
        'next_year': next_year,
        'previous_month': previous_month,
        'next_month': next_month,
        'calendar_month': calendar_month,
        'tasks_dict': tasks_dict,
        'month_name': month_name,
        'month_abbr': month_abbr
    }

    return render(request, 'htmx/task_calendar.html', context)


@login_required
def task_list(request):
    return render(request, 'task_list.html')


@login_required
def task_detail(request, uuid):
    is_superuser = request.user.is_superuser
    task = get_object_or_404(models.Task, id=uuid)
    if is_superuser or task.executor == request.user:
        context = {'task': task}
        return render(request, 'task_detail.html', context)
    else:
        return HttpResponseNotFound('Объект не найден!')



@login_required
def vacation_list(request):
    vacations = models.Vacation.objects.filter(user=request.user).order_by('start_date')
    next_vacation = vacations.filter(status='planned').first()
    days_vacation = None
    if next_vacation:
        days_vacation = (next_vacation.end_date - next_vacation.start_date).days
    completed_vacations = vacations.filter(status='completed')
    cancelled_vacations = vacations.filter(status='cancelled')

    context = {
        'next_vacation': next_vacation,
        'days_vacation': days_vacation,
        'completed_vacations': completed_vacations,
        'cancelled_vacations': cancelled_vacations
    }

    return render(request, 'vacation_list.html', context)


@login_required
def report_detail(request):
    try:
        _id = int(request.GET.get('id', None))
    except ValueError:
        return HttpResponseNotFound('Объект не найден!')
    report = get_object_or_404(models.Report, id=_id, creator=request.user)
    context = {'obj': report}
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_list(request):
    reports = models.Report.objects.filter(creator=request.user)
    paginator = Paginator(reports, 25)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    if len(page_obj.object_list) > 0:
        last_report = page_obj.object_list[0]
        context['last_report'] = last_report
    return render(request, 'reports/report_list.html', context)


@login_required
def send_report(request):
    if request.method == 'POST':
        report_form = forms.ReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.creator = request.user
            report.save()
            messages.success(request, 'Вы успешно отправили письмо!')
            return redirect('reports')
    else:
        report_form = forms.ReportForm()
    context = {'report_form': report_form}
    return render(request, 'reports/send_report.html', context)
