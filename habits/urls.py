from django.urls import path

from habits.views import (
    HabitCreateView,
    HabitDeleteView,
    HabitDetailView,
    HabitListView,
    HabitPublicListView,
    HabitUpdateView,
)

app_name = "habits"

urlpatterns = [
    path("create/", HabitCreateView.as_view(), name="habit_create"),
    path("list/", HabitListView.as_view(), name="habit_list"),
    path("public/", HabitPublicListView.as_view(), name="habit_public"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit_detail"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
]
