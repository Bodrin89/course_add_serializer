import pytest


@pytest.fixture
@pytest.mark.django_db
def hr_token(client, django_user_model):
    username = "hr"
    password = "1234"

    # Создание django пользователя
    django_user_model.objects.create_user(
        username=username, password=password, role="hr"
    )

    # Авторизация созданным пользователем
    response = client.post(
        "/user/login/",
        {"username": username, "password": password},
        format='json'
    )

    return response.data["token"]

