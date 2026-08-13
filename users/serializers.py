from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(label="Почта")
    password = serializers.CharField(write_only=True, label="Пароль")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        attrs[self.username_field] = attrs.get("email")
        return super().validate(attrs)


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        # Хеширование пароля
        return CustomUser.objects.create_user(**validated_data)
