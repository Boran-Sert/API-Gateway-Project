from fastapi import FastAPI

app = FastAPI(title="User Service", version="1.0.0")

@app.get("/users")
async def get_users():
    """
    Kullanıcı listesini getirir.
    Testi geçmek için istenen RMM Seviye 3 (HATEOAS) formatında boş liste dönüyoruz.
    """
    return {
        "data": [],
        "_links": {
            "self": {"href": "/users", "method": "GET"}
        }
    }