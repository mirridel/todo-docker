"""
URL configuration for todo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from todo import settings
from todo.apps.core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),

    path('reports/', views.report_list, name='reports'),
    path('reports/send/', views.send_report, name='send-report'),
    path('api/report/', views.report_detail, name='report-detail'),

    path('tasks/', views.task_list, name='tasks'),
    path('tasks/<int:uuid>/', views.task_detail, name='task-detail'),

    path('vacations/', views.vacation_list, name='vacations'),

    path('api/tasks/', views.get_tasks, name='get-tasks'),

]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
