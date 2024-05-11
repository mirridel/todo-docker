from django.contrib import admin

from todo.apps.custom_account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    username = None
