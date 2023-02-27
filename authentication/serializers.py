
from rest_framework import serializers

from authentication.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        """Хеширование пароля"""
        user = super().create(validated_data)
        user.set_password(user.password)  # Пересохранение пароля в виде хэша
        user.save()
        return user

