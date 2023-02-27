

def test_root_not_found(client):
    response = client.get("/")  # client - встроенная фикстура которая посылает запросы (здесь get) на указанный адрес
    assert response.status_code == 404

