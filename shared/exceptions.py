"""Sistem hata yönetim merkezi """

class AppException(Exception):
    """
    Sistemdeki tüm özel hataların miras alacağı temel sınıf.
    FastAPI hata yakalarken sadece burayı kullanacak.
    """
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code  # Örn: 404, 401, 500 vb.
        self.detail = detail            # Kullanıcıya gösterilecek mesaj
        self.error_code = error_code    # Sistem içindeki standart hata kodu (Örn: "USER_NOT_FOUND")
        
        # Exception sınıfını başlatıyoruz
        super().__init__(self.detail)

class NotFoundException(AppException):
    """Aranılan kaynak bulunamadığında 404 döner."""
    def __init__(self, resource_name: str, resource_id: str):
        super().__init__(
            status_code=404,
            detail=f"{resource_name} bulunamadı: '{resource_id}'",
            error_code="RESOURCE_NOT_FOUND"
        )


class UnauthorizedException(AppException):
    """Yetkisiz erişim denemelerinde (Token yok/geçersiz) 401 döner."""
    def __init__(self, detail: str = "Geçersiz veya süresi dolmuş token tespit edildi."):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="UNAUTHORIZED"
        )


class ConflictException(AppException):
    """Zaten var olan veriyi tekrar oluşturma (Örn: aynı email) denemesinde 409 döner."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT"
        )


class ServiceUnavailableException(AppException):
    """Dispatcher'ın hedef mikroservise bağlanamadığı durumda 503 döner."""
    def __init__(self, service_name: str):
        super().__init__(
            status_code=503,
            detail=f"{service_name} servisine şu an ulaşılamıyor. Lütfen daha sonra tekrar deneyin.",
            error_code="SERVICE_UNAVAILABLE"
        )
