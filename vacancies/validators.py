from datetime import date

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.templatetags.rest_framework import data


def check_date_not_past(value: data):
    """Валидатор проверки даты"""
    if value < date.today():
        raise ValidationError(f"{value} in the past")


class NotInStatusValidator:  # Пользовательский валидатор для сериализатора
    def __init__(self, statuses):  # Конструктор в который передаются данные для использования в __call__
        self.statuses = statuses
        if not isinstance(statuses, list):
            statuses = [statuses]

    def __call__(self, value):  # Условие при котором валидация данных не пройдет
        if value in self.statuses:
            raise serializers.ValidationError("Incorrect status")
