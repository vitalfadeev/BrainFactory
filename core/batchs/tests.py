from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model


# insecure
class BatchesTests(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_public_page_status_code(self):
        response = self.client.get('/public')
        self.assertEqual(response.status_code, 200)

    def test_my_page_status_code(self):
        response = self.client.get('/my')
        self.assertEqual(response.status_code, 302)

    def test_view_project_page_status_code(self):
        response = self.client.get('/view/74/project')
        self.assertEqual(response.status_code, 302)


# secure
class SimpleTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_secure_page(self):
        User = get_user_model()
        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/my', follow=True)
        self.assertIsNotNone(response.context['query_results'])

    def test_send1(self):
        User = get_user_model()
        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/send1', follow=True)
        self.assertIsNotNone(response.context['form'])

    def test_send2(self):
        from . import models
        User = get_user_model()
        self.client.login(username='temporary', password='temporary')
        with self.assertRaises(models.Batchs.DoesNotExist):
            response = self.client.get('/send2/73', follow=True)
            user = User.objects.get(username='temporary')

