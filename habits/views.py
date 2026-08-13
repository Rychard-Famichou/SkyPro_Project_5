from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated

from habits.models import Habit
from habits.paginators import HabitPaginator
from habits.serializers import HabitSerializer
from users.permissions import IsOwner


# Create your views here.
class HabitBaseView(generics.GenericAPIView):
    """Базовый класс для генериков"""

    serializer_class = HabitSerializer
    permission_classes = [IsOwner]
    queryset = Habit.objects.all()


class HabitCreateView(HabitBaseView, generics.CreateAPIView):
    """Создать привычку"""

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Пользователь не авторизован.")
        serializer.save(owner=self.request.user)


class HabitListView(HabitBaseView, generics.ListAPIView):
    """Лист моих привычек"""

    pagination_class = HabitPaginator

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(owner=user)


class HabitPublicListView(HabitBaseView, generics.ListAPIView):
    """Лист публичных привычек"""

    def get_queryset(self):
        return Habit.objects.filter(public=True)


class HabitDetailView(HabitBaseView, generics.RetrieveAPIView):
    """Детали моей привычки"""

    pass


class HabitUpdateView(HabitBaseView, generics.UpdateAPIView):
    """Изменить мою привычку"""

    pass


class HabitDeleteView(HabitBaseView, generics.DestroyAPIView):
    """Удалить мою привычку"""

    pass
