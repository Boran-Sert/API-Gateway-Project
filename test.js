import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 20,           // 20 eşzamanlı kullanıcı
    duration: '1m',    // 1 dakika boyunca aralıksız test
};

const BASE_URL = 'http://localhost:8000';

export default function () {
    // Rastgele kullanıcı (Admin ve Normal User simülasyonu)
    const id = Math.floor(Math.random() * 1000000);
    const isAdmin = Math.random() < 0.3; // %30 ihtimalle admin üret
    const email = `${isAdmin ? 'admin' : 'user'}_${id}@proje.com`;
    const password = 'Sifre123!';

    const headers = { 'Content-Type': 'application/json' };

    // --- 1. AUTH SERVİSİ (Prefix: /api/auth) ---
    let regRes = http.post(`${BASE_URL}/api/auth/register`, JSON.stringify({ email, password }), { headers });
    check(regRes, { 'Register Basarili (201/409)': (r) => r.status === 201 || r.status === 409 });

    let loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({ email, password }), { headers });

    if (check(loginRes, { 'Login Basarili (200)': (r) => r.status === 200 })) {
        const token = loginRes.json().token;
        const authHeaders = { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } };

        // --- 2. USER SERVİSİ (Prefix: /api/users) ---
        // user_db'de profil oluşturur veya var olanı çeker
        let meRes = http.get(`${BASE_URL}/api/users/me`, authHeaders);
        check(meRes, { 'User Profil Okundu (200)': (r) => r.status === 200 });

        // --- 3. PRODUCT SERVİSİ (Prefix: /api/products) ---
        let listRes = http.get(`${BASE_URL}/api/products`, authHeaders);
        check(listRes, { 'Product Liste Alindi (200)': (r) => r.status === 200 });

        // Eğer admin ise product_db'ye veri yazar
        if (isAdmin) {
            let createRes = http.post(`${BASE_URL}/api/products`, JSON.stringify({
                name: `Urun_${id}`,
                price: parseFloat((Math.random() * 500).toFixed(2)),
                category: 'Test',
                stock: Math.floor(Math.random() * 100)
            }), authHeaders);
            check(createRes, { 'Product Eklendi (201)': (r) => r.status === 201 || r.status === 403 });
        }
    }

    // Sunucuyu boğmamak için her döngüde 0.5 sn bekle
    sleep(0.5);
}