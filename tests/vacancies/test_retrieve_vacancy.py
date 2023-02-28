from datetime import date

import pytest


@pytest.mark.django_db
def test_retrieve_vacancy(client, vacancy, hr_token):  # vacancy это VacancyFactory из factories.py
    expected_response = {
        "id": vacancy.pk,
        "created": date.today().strftime("%Y-%m-%d"),
        "skills": [],
        "slug": "test_slug",
        "text": "test_text",
        "status": "draft",
        "min_experience": None,
        "likes": 0,
        "update_at": None,
        "user": vacancy.user_id
    }

    response = client.get(
        f'/vacancy/{vacancy.pk}/',
        HTTP_AUTHORIZATION="Token " + hr_token
    )

    assert response.status_code == 200
    assert response.data == expected_response
