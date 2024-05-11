from django.apps import AppConfig


class CustomAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todo.apps.custom_account'
    verbose_name = 'Пользователи'
