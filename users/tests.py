from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


# Create your tests here.
class AnonimCreateUserCase(APITestCase):
    """ Класс тестов для не авторизованного пользователя """

    def setUp(self):
        self.data = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password",
        }
        self.user_create_url = reverse('users:user_create')

    def test_user_create(self):
        """ Тест создания пользователя """
        response = self.client.post(self.user_create_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class UsersMixin(APITestCase):
    """Миксин пользователей."""

    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="owner_password"
        )
        self.revizor = CustomUser.objects.create_user(
            username="revizor",
            email="revizor@example.com",
            password="revizor_password"
        )
