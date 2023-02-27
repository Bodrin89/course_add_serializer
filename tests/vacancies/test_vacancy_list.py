from datetime import date

import pytest

from vacancies.models import Vacancy


@pytest.mark.django_db  # pytest.mark.django_db - проверяет миграции и удаляет данные из БД после завершения теста
def test_vacancy_list(client):
    vacancy = Vacancy.objects.create(text="123", slug="123")

    expected_response = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [{
            "id": vacancy.pk,
            "skills": [],
            "slug": "123",
            "status": "draft",
            "text": "123",
            "created": date.today().strftime("%Y-%m-%d"),
            "username": None
        }]
    }

    response = client.get("/vacancy/")  # Слэши обязательно с двух сторон
    assert response.status_code == 200
    assert response.data == expected_response
