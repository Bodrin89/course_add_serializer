from pytest_factoryboy import register

from tests.factories import VacancyFactory, UserFactory


pytest_plugins = "tests.fixtures"  # Регистрация фикстур

register(VacancyFactory)  # Регистрация фабрики Вакансии
register(UserFactory)
