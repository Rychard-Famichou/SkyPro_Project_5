from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.services import send_telegram_notification
from habits.tasks import remind_habit
from users.tests import UsersMixin


# Create your tests here.
class HabitAnonimCreateCase(APITestCase):
    """Класс тестов создания привычек анонимом."""

    def setUp(self):
        self.habit_create_url = reverse('habits:habit_create')

    def test_habit_create_useful(self):
        """Успешное создание полезной привычки с наградой."""
        self.data = {
            'title': 'Water',
            "perform": "Drink water",
            "period": 21,
            "reward": "Cake",
            "running_time": 10,
        }
        response = self.client.post(self.habit_create_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HabitSuccessCreateCase(UsersMixin):
    """Класс тестов создания привычек для владельца."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.owner)
        self.habit_create_url = reverse('habits:habit_create')

    def test_habit_create_useful(self):
        """Успешное создание полезной привычки с наградой."""
        self.data = {
            'title': 'Water',
            "owner": self.owner.pk,
            "perform": "Drink water",
            "period": 21,
            "reward": "Cake",
            "running_time": 10,
        }
        response = self.client.post(self.habit_create_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_pleasant_habit_success(self):
        """Успешное создание приятной привычки."""
        data = {
            'title': 'Cake',
            "owner": self.owner.pk,
            'pleasant_sign': True,
            "perform": "Eat cake",
            'period': 1,
            'running_time': 120,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class HabitsMixin(UsersMixin):
    """Миксин привычек."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.owner)
        self.water_habit = Habit.objects.create(
            title='Water',
            owner=self.owner,
            perform="Drink water",
            period=21,
            reward="Cake",
            running_time=10,
        )
        self.cake_habit = Habit.objects.create(
            title='Cake',
            owner=self.owner,
            pleasant_sign=True,
            perform="Eat cake",
            period=1,
            running_time=120,
            public=True,
        )
        self.habit_create_url = reverse('habits:habit_create')
        self.habit_list_url = reverse('habits:habit_list')
        self.habit_public_url = reverse('habits:habit_public')
        self.habit_detail_url = reverse('habits:habit_detail', kwargs={'pk': self.water_habit.pk})
        self.habit_update_url = reverse('habits:habit_update', kwargs={'pk': self.water_habit.pk})
        self.habit_delete_url = reverse('habits:habit_delete', kwargs={'pk': self.water_habit.pk})


class HabitValidCreateCase(HabitsMixin):
    """Класс тестов создания привычек с валидацией."""

    def test_running_time_out(self):
        """Ошибка: время выполнения больше 120 секунд"""
        data = {
            'title': 'Run',
            "owner": self.owner.pk,
            "perform": "Jogging",
            'reward': 'Rest',
            'running_time': 150,
            'period': 1,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_low_period(self):
        """Ошибка: период выполнения не реже 1 раза в неделю"""
        data = {
            'title': 'Run',
            "owner": self.owner.pk,
            "perform": "Jogging",
            'reward': 'Rest',
            'running_time': 120,
            'period': 0,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Периодичность выполнения привычки не реже 1 раза в неделю.', response.data['non_field_errors'])

    def test_habit_bound_habit(self):
        """Ошибка: полезная привычка не может связана с полезной"""
        data = {
            'title': 'Run',
            "owner": self.owner.pk,
            "perform": "Jogging",
            'bound_habit': self.water_habit.pk,
            'running_time': 120,
            'period': 1,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Связанная привычка обязательно должна быть приятной.', response.data['non_field_errors'])

    def test_pleasant_habit_with_reward(self):
        """Ошибка: приятная привычка не может иметь вознаграждение"""
        data = {
            'title': 'Rest',
            "owner": self.owner.pk,
            'pleasant_sign': True,
            "perform": "Laying",
            'reward': 'Chocolate',
            'running_time': 120,
            'period': 1,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Приятная привычка не может иметь вознаграждение.', response.data['non_field_errors'])

    def test_pleasant_habit_with_pleasant_habit(self):
        """Ошибка: приятная привычка + приятная привычка"""
        data = {
            'title': 'Rest',
            "owner": self.owner.pk,
            'pleasant_sign': True,
            "perform": "Laying",
            'bound_habit': self.cake_habit.pk,
            'running_time': 120,
            'period': 1,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Приятная привычка не может быть связана с другой привычкой.', response.data['non_field_errors'])

    def test_habit_with_any(self):
        """Ошибка: привычка должно награждаться"""
        data = {
            'title': 'Run',
            "owner": self.owner.pk,
            "perform": "Jogging",
            'running_time': 120,
            'period': 1,
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Обычная привычка должна иметь либо вознаграждение, либо связанную приятную привычку.',
                      response.data['non_field_errors'])

    def test_habit_with_two(self):
        """Ошибка: двойная награда"""
        data = {
            'title': 'Run',
            "owner": self.owner.pk,
            "perform": "Jogging",
            'running_time': 120,
            'period': 1,
            'bound_habit': self.cake_habit.pk,
            'reward': 'Rest',
        }
        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Вы должны выбрать что-то одно: приятную привычку или вознаграждение.',
                      response.data['non_field_errors'])


class HabitOwnerRUDCase(HabitsMixin):
    """Класс тестов для владельца на полный цикл с доступом"""

    def setUp(self):
        super().setUp()

    def test_list_habit_owner(self):
        """Просмотр списка своих привычек с пагинатором."""
        response = self.client.get(self.habit_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_detail_habit_owner(self):
        """Просмотр деталей своей привычки."""
        response = self.client.get(self.habit_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Water")

    def test_update_habit_owner(self):
        """Изменение данных своей привычки"""
        data = {
            'title': 'Water',
            'perform': "Drink water",
            'period': 21,
            'reward': "Cake",
            'running_time': 10,
            'public': True,
        }
        response = self.client.patch(self.habit_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.water_habit.refresh_from_db()
        self.assertEqual(self.water_habit.public, True)

    def test_delete_habit_owner(self):
        """Удаление своей привычки"""
        response = self.client.delete(self.habit_delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=self.water_habit.pk).exists())

class HabitRevizorRUDCase(HabitsMixin):
    """Класс тестов для ревизора на полный цикл без доступа"""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.revizor)

    def test_list_habit_revizor(self):
        """Просмотр списка своих привычек с пагинатором."""
        response = self.client.get(self.habit_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_public_habit_revizor(self):
        """Просмотр списка публичных привычек."""
        response = self.client.get(self.habit_public_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Cake')

    def test_detail_habit_revizor(self):
        """Просмотр деталей чужой привычки."""
        response = self.client.get(self.habit_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit_revizor(self):
        """Изменение данных чужой привычки"""
        data = {
            'title': 'Water',
            'perform': "Drink water",
            'period': 21,
            'reward': "Cake",
            'running_time': 10,
            'public': True,
        }
        response = self.client.patch(self.habit_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.water_habit.refresh_from_db()
        self.assertEqual(self.water_habit.public, False)

    def test_delete_habit_revizor(self):
        """Удаление чужой привычки"""
        response = self.client.delete(self.habit_delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Habit.objects.filter(pk=self.water_habit.pk).exists())


class TelegramNotificationTestCase(TestCase):

    def test_send_notification_success(self):
        """Успешная отправка уведомления."""
        with patch('habits.services.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            result = send_telegram_notification(chat_id="123", text="Привет")
            self.assertTrue(result)
            mock_post.assert_called_once()

    def test_send_notification_failure(self):
        """Ошибка при отправке уведомления."""
        with patch('habits.services.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Ошибка сети")
            result = send_telegram_notification(chat_id="123", text="Привет")
            self.assertFalse(result)


class RemindHabitTaskTestCase(TestCase):
    # Нужен работающий воркер Celery

    @patch('habits.tasks.send_telegram_notification')
    def test_remind_habit_at_trigger_hour(self, mock_send):
        """Задача отправляет уведомление в правильное время (например, в 12:00)."""
        specific_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        with patch('django.utils.timezone.localtime', return_value=specific_time):
            result = remind_habit.delay().get()
        self.assertEqual(result, "Успешно выполнено!")
        mock_send.assert_called_once_with("@RychardFamichou", "Пить воду")

    @patch('habits.tasks.send_telegram_notification')
    def test_remind_habit_at_wrong_hour(self, mock_send):
        """Задача НЕ отправляет уведомление в другое время (например, в 13:00)."""
        specific_time = timezone.now().replace(hour=13, minute=0, second=0, microsecond=0)
        with patch('django.utils.timezone.localtime', return_value=specific_time):
            result = remind_habit.delay().get()

        self.assertEqual(result, "Успешно выполнено!")
        mock_send.assert_not_called()