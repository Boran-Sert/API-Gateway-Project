from fastapi.testclient import TestClient

# NOT: app.main henüz oluşturulmadığı için bu import satırı bilerek hata verecektir.
# Bu durum TDD'nin "RED" (Başarısız Test) aşamasının tam olarak kendisidir.
try:
    from app.main import app
    client = TestClient(app)
except ImportError:
    client = None

def test_get_empty_users_list():
    """
    Kullanıcı listesini getiren GET /users endpoint'inin testi.
    Sistemde hiç kullanıcı yokken boş bir liste ve HATEOAS linkleri dönmelidir.
    """
    assert client is not None, "Uygulama (app.main) henüz yazılmadı!"
    
    response = client.get("/users")
    
    # 1. Beklenen HTTP durum kodu 200 olmalı
    assert response.status_code == 200
    
    json_data = response.json()
    
    # 2. RMM Seviye 3'e uygun JSON gövdesi kontrolü (+5 puan için)
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    
    # 3. HATEOAS linkleri kontrolü
    assert "_links" in json_data
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"] == "/users"