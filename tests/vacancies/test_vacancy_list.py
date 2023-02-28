from datetime import date

import pytest

from tests.factories import VacancyFactory
from vacancies.serializers import VacancyListSerializer


@pytest.mark.django_db  # pytest.mark.django_db - проверяет миграции и удаляет данные из БД после завершения теста
def test_vacancy_list(client):

    vacancies = VacancyFactory.create_batch(10)  # create_bach создает несколько экземпляров

    expected_response = {
        "count": 10,
        "next": None,
        "previous": None,
        "results": VacancyListSerializer(vacancies, many=True).data
    }

    response = client.get("/vacancy/")  # Слэши обязательно с двух сторон
    assert response.status_code == 200
    assert response.data == expected_response
