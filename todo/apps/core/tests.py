from django.test import TestCase, Client

from django.urls import reverse
from todo.apps.core import models
from todo.apps.custom_account.models import User


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='12345')
        self.client.login(email='test@example.com', password='12345')

        self.index_url = reverse('index')
        self.account_url = reverse('account')
        self.task_list_url = reverse('tasks')
        self.report_list_url = reverse('reports')
        self.send_report_url = reverse('send-report')

    def test_index_GET(self):
        response = self.client.get(self.index_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_account_GET(self):
        response = self.client.get(self.account_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account.html')

    def test_task_list_GET(self):
        response = self.client.get(self.task_list_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_list.html')

    def test_report_list_GET(self):
        response = self.client.get(self.report_list_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_list.html')

    def test_send_report_POST(self):
        response = self.client.post(self.send_report_url, {
            'theme': 'Test theme',
            'content': 'Test content',
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(models.Report.objects.first().theme, 'Test theme')
