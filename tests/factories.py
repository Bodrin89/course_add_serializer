import factory.django

from authentication.models import User
from vacancies.models import Vacancy


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker("name")  # Faker используется для имитации имени, если поле должно быть уникальным
    password = "1234"


class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy
    slug = "test_slug"
    text = "test_text"
    user = factory.SubFactory(UserFactory)
