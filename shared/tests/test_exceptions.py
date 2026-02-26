""" shared/tests/test_exceptions.py - Hata Yönetimi Testleri """

from shared.exceptions import (
    AppException, 
    NotFoundException, 
    UnauthorizedException, 
    ConflictException, 
    ServiceUnavailableException, 
    app_exception_handler )

def tests_not_found_exception():
    """ NotFoundException sınıfını test eder """
    exc = NotFoundException("Kullanıcı", "123")
    assert exc.status_code == 404
    assert exc.detail == "Kullanıcı bulunamadı: '123'"
    assert exc.error_code == "RESOURCE_NOT_FOUND"

def tests_unauthorized_exception():
    """ UnauthorizedException sınıfını test eder """
    exc = UnauthorizedException()
    assert exc.status_code == 401
    assert exc.detail == "Geçersiz veya süresi dolmuş token tespit edildi."
    assert exc.error_code == "UNAUTHORIZED"

def tests_conflict_exception():
    """ ConflictException sınıfını test eder """
    exc = ConflictException("Kullanıcı zaten mevcut")
    assert exc.status_code == 409
    assert exc.detail == "Kullanıcı zaten mevcut"
    assert exc.error_code == "CONFLICT"

def tests_service_unavailable_exception():
    """ ServiceUnavailableException sınıfını test eder """
    exc = ServiceUnavailableException("Kullanıcı Servisi")
    assert exc.status_code == 503
    assert exc.detail == "Kullanıcı Servisi servisine şu an ulaşılamıyor. Lütfen daha sonra tekrar deneyin."
    assert exc.error_code == "SERVICE_UNAVAILABLE"

def tests_app_exception_handler():
    """ app_exception_handler fonksiyonunu test eder """
    request = Request({"type": "http", "method": "GET", "url": "/users/123"})
    exc = NotFoundException("Kullanıcı", "123")
    response = app_exception_handler(request, exc)
    assert response.status_code == 404
    assert response.body == {
        "success": False,
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "detail": "Kullanıcı bulunamadı: '123'",
        },
        "_links": {
            "self": {"href": "/users/123", "method": "GET"},
            "docs": {"href": "/docs"},
        },
    }

