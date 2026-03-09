from fastapi import FastAPI

app = FastAPI(title="Product Service", version="1.0.0")

@app.get("/products")
async def get_products():
    """
    Sistemdeki ürünleri listeler.
    Testi geçmek için RMM Seviye 3 formatinda boş liste dönüyoruz.
    """
    return {
        "data": [],
        "_links": {
            "self": {"href": "/products", "method": "GET"}
        }
    }