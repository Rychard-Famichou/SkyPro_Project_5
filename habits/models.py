from django.db import models


# Create your models here.
class Habit(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Привычка")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    owner = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, verbose_name="Владелец")
    place = models.CharField(max_length=100, null=True, blank=True, verbose_name="Место")
    execute_time = models.CharField(max_length=100, null=True, blank=True, verbose_name="Время исполнения")
    perform = models.TextField(verbose_name="Действие")
    pleasant_sign = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    bound_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Связанная привычка"
    )
    period = models.IntegerField(null=True, blank=True, verbose_name="Периодичность")
    reward = models.TextField(null=True, blank=True, verbose_name="Вознаграждение")
    running_time = models.IntegerField(verbose_name="Время на выполнение")
    public = models.BooleanField(default=False, verbose_name="Публичность")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
