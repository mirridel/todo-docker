from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse
from django.utils.timezone import now

from todo.apps.core import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)
    search_fields = ('title',)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'total')
    readonly_fields = ('total_items', 'total_tasks', 'total', 'created_at', 'updated_at', 'creator',)
    autocomplete_fields = ('client',)
    fieldsets = [
        (
            'Осн. информация',
            {
                'fields': ('title', 'client', 'location', 'status', 'price')
            },
        ),
        (
            'Стоимость',
            {
                'classes': ['collapse'],
                'fields': ['total_items', 'total_tasks', 'total'],
            },
        ),
        (
            'Доп. информация',
            {
                'classes': ['collapse'],
                'fields': ['created_at', 'updated_at', 'creator'],
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', )


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title', 'price', 'type')


class ExpiredListFilter(admin.SimpleListFilter):
    title = "Просрочено?"
    parameter_name = "expired"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Да"),
            ("no", "Нет"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                expired_at__lte=now(),
            )
        elif self.value() == "no":
            return queryset.filter(
                expired_at__gte=now(),
            )


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'job', 'created_at', 'expired_at', 'executor', 'status')
    readonly_fields = ('total', 'created_at', 'updated_at', 'creator',)
    list_filter = (ExpiredListFilter, 'created_at', 'updated_at', 'status')
    actions = ('close_expired_tasks',)

    fieldsets = [
        (
            'Осн. информация',
            {
                'fields': ('project', 'job', 'quantity', 'expired_at', 'executor', 'status')
            },
        ),
        (
            'Оплата',
            {
                'classes': ['collapse'],
                'fields': ['coefficient', 'is_fixed_price', 'price', 'total'],
            },
        ),
        (
            'Доп. информация',
            {
                'classes': ['collapse'],
                'fields': ['extra', 'created_at', 'updated_at', 'creator'],
            },
        ),
    ]

    @admin.action(description='Закрыть просроченные задачи')
    def close_expired_tasks(self, request, queryset):
        selected_tasks = queryset.filter(expired_at__lte=now())
        selected_tasks.update(status='cancelled', total=0, extra='Задача просрочена и закрыта.')

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Vacation)
class VacationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'end_date', 'status')


@admin.register(models.Report)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme', 'created_at', 'updated_at', 'creator', 'is_answered')
    readonly_fields = ('created_at', 'updated_at', 'creator', 'is_answered',)
    list_filter = ('created_at', 'updated_at', 'is_answered',)


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'title', 'quantity', 'price', 'total')
    list_filter = ('project',)
    search_fields = ('project__title', 'title',)
    readonly_fields = ('total', 'created_at', 'updated_at', 'creator',)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)
