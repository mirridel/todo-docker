from django.contrib.admin import display
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now

from todo.apps.custom_account.models import User
from mptt.models import MPTTModel, TreeForeignKey


class Client(models.Model):
    title = models.CharField(max_length=200, verbose_name='название')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name='название')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='заказчик', related_name='client')
    location = models.CharField(max_length=200, verbose_name='местоположение')
    status = models.CharField(max_length=200, verbose_name='статус')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлено')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='создатель', related_name='creator')

    def get_total_tasks(self):
        return self.tasks.aggregate(Sum('total')).get('total__sum')

    def get_total_items(self):
        return self.items.aggregate(Sum('total')).get('total__sum')

    def get_total(self):
        total = self.price
        total_items = self.get_total_items()
        total_tasks = self.get_total_tasks()
        if total_items:
            total += total_items
        if total_tasks:
            total += total_tasks
        return f'{int(total)} руб'

    @property
    @display(description='смета', )
    def total_items(self):
        return f'{self.get_total_items()} руб'

    @property
    @display(description='задачи', )
    def total_tasks(self):
        return f'{self.get_total_tasks()} руб'

    @property
    @display(description='итого', )
    def total(self):
        return self.get_total()

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    def __str__(self):
        return f'{self.title}'


class Category(MPTTModel):
    title = models.CharField(max_length=128, verbose_name='название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', verbose_name='родитель')

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Job(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='категория')
    title = models.CharField(max_length=200, verbose_name='название')
    type = models.CharField(max_length=200, verbose_name='тип')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')

    def __str__(self):
        return f'{self.category.title} > {self.title}'

    class Meta:
        verbose_name = 'работа'
        verbose_name_plural = 'работы'


class Task(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('processed', 'Обработана'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks',
                                blank=True, null=True, verbose_name='проект')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job', verbose_name='работа')
    quantity = models.IntegerField(verbose_name='количество')

    coefficient = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, verbose_name='коэффициент')
    is_fixed_price = models.BooleanField(default=False, verbose_name='фикс. цена')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='цена')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='итого')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создание')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновление')
    expired_at = models.DateTimeField(verbose_name='завершение')
    completed_at = models.DateTimeField(blank=True, null=True, editable=False)

    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='created', verbose_name='статус')

    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executors',
                                 blank=True, null=True, verbose_name='исполнитель')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creators',
                                blank=True, null=True, verbose_name='создатель')

    extra = models.TextField(blank=True, null=True, verbose_name='дополнительно')

    def get_absolute_url(self, *args, **kwargs):
        return reverse('task-detail', kwargs={'uuid': self.id})

    def save(self, *args, **kwargs):
        self.total = self.job.price * self.quantity * self.coefficient
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f'Задача №{self.id}'


class Item(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items',
                                blank=True, null=True, verbose_name='проект')
    title = models.CharField(max_length=200, verbose_name='название')
    quantity = models.IntegerField(default=1, verbose_name='кол-во')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='итого')
    note = models.TextField(blank=True, null=True, verbose_name='примечание')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлено')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='создатель')

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'позиция сметы'
        verbose_name_plural = 'позиции сметы'


class Vacation(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('processed', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='сотрудник')
    start_date = models.DateField(verbose_name='начало')
    end_date = models.DateField(verbose_name='окончание')
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, verbose_name='статус')

    class Meta:
        verbose_name = 'отпуск'
        verbose_name_plural = 'отпуска'
        ordering = ['-start_date']


class Report(models.Model):
    creator = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE, verbose_name='отправитель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создано')
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name='обновлено')
    theme = models.CharField(max_length=200, verbose_name='тема')
    content = models.TextField(verbose_name='содержание')
    answer = models.TextField(blank=True, null=True, verbose_name='ответ')
    is_answered = models.BooleanField(blank=True, null=True, default=False, verbose_name='ответ?')

    def save(self, *args, **kwargs):
        self.updated_at = now()
        self.is_answered = True if self.answer else False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ['-updated_at']
