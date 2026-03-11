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
    Kullanici listesini getiren GET /users endpoint'inin testi.
    Sistemde hiç kullanici yokken boş bir liste ve HATEOAS linkleri dönmelidir.
    """
    assert client is not None, "Uygulama (app.main) henüz yok!"
    
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

def test_create_users():
    """
    Yeni bir kullanıcı oluşturma POST /users endpoint'inin testi.
    """
    assert client is not None, "Uygulama (app.main) henüz yok!"

    new_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }
    response = client.post("/users", json= new_user_data)

    # 1. Başarılı HTTP Kodunu Kontrol Et (Genellikle 201 Created döndürülür)
    assert response.status_code == 201

    json_data = response.json()

    # 2. Gelen yanıtı kontrol et
    assert "data" in json_data
    assert json_data["data"]["username"] == "testuser"
    assert json_data["data"]["email"] == "test@example.com"
    assert "id" in json_data["data"]
    assert "_links" in json_data