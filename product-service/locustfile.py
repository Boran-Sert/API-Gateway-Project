from locust import HttpUser, task, between
import random

class ProductServiceSimulator(HttpUser):
    """
    
    Her kullanici, işlemler arasinda 1 ile 3 saniye arasi rastgele bekler.
    """
    wait_time = between(1, 3)

    @task(3)
    def view_products(self):
        """
        Ürünleri listelemek.
        @task(3) diyerek bu işlemin diğerine göre 3 kat daha fazla yapmayi sagladik.
        """
        with self.client.get("/products", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Listeleme Başarisiz: {response.status_code}")

    @task(1)
    def add_product(self):
        """
        Yeni ürün ekleme.
        """
        new_product = {
            "name": f"Locust Test Ürünü {random.randint(1, 10000)}",
            "price": round(random.uniform(50.0, 5000.0), 2),
            "category": "Yük Testi",
            "stock": random.randint(1, 100)
        }
        
        with self.client.post("/products", json=new_product, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Ekleme Başarisiz: {response.status_code}")