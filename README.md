# 🚀 API Gateway & Microservices Ecosystem

Bu proje, Kocaeli Üniversitesi Bilişim Sistemleri Mühendisliği Yazılım Laboratuvarı-II dersi kapsamında geliştirilmiştir.

## 🛠️ Mimari ve Bileşenler
- **Dispatcher (API Gateway):** Sistemin tek giriş noktasıdır. TDD disipliniyle geliştirilmiş olup tüm trafiği izole bir NoSQL (MongoDB) tablosuna loglar.
- **Product Service (Göksel):** Richardson Olgunluk Modeli Seviye 3 (HATEOAS) standartlarına uygun, dinamik `_links` yapısı sunan mikroservistir.
- **Monitoring Dashboard:** Dispatcher üzerinden canlı trafik takibi yapılabilmektedir.

## 🧪 Kalite Standartları
- **Network Isolation:** Mikroservisler dış ağa kapalıdır, yalnızca Dispatcher üzerinden erişilebilir.
- **Dockerization:** Tüm sistem `docker-compose up` komutuyla orkestre edilmektedir.

## 📊 İş Akışı (Sequence Diagram)
```mermaid
sequenceDiagram
    participant Client as Kullanıcı (Tarayıcı)
    participant GW as Dispatcher (Gateway)
    participant LogDB as MongoDB (Log)
    participant Prod as Product Service
    
    Client->>GW: GET /api/products
    GW->>LogDB: Trafiği Kaydet (Log)
    GW->>Prod: İsteği Yönlendir (Internal)
    Prod-->>GW: JSON + HATEOAS Links
    GW-->>Client: 200 OK Response