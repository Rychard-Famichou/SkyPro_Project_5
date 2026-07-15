from rest_framework import serializers


class HabitValidator:
    def __call__(self, attrs):
        bound_habit = attrs.get("bound_habit")
        reward = attrs.get("reward")
        pleasant_sign = attrs.get("pleasant_sign")
        running_time = attrs.get("running_time")
        period = attrs.get("period")

        if not pleasant_sign:
            if not bound_habit and not reward:
                raise serializers.ValidationError(
                    "Обычная привычка должна иметь либо вознаграждение, либо связанную приятную привычку."
                )
            if bound_habit and reward:
                raise serializers.ValidationError(
                    "Вы должны выбрать что-то одно: приятную привычку или вознаграждение."
                )

        if pleasant_sign:
            if bound_habit:
                raise serializers.ValidationError("Приятная привычка не может быть связана с другой привычкой.")
            if reward:
                raise serializers.ValidationError("Приятная привычка не может иметь вознаграждение.")

        if bound_habit:
            is_pleasant = getattr(bound_habit, "pleasant_sign")
            if not is_pleasant:
                raise serializers.ValidationError("Связанная привычка обязательно должна быть приятной.")

        if running_time is not None:
            if running_time < 1 or running_time > 120:
                raise serializers.ValidationError("Время на выполнение привычки может быть от 1 до 120 секунд.")

        if period is not None and period < 1:
            raise serializers.ValidationError("Периодичность выполнения привычки не реже 1 раза в неделю.")
