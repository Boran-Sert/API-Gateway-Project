""" shared/tests/test_hateoas.py - HATEOAS Link Builder Testleri """

from shared.hateoas import HateoasLink, HateoasBuilder

def test_hateoas_link_default_method_is_get():
    """ Link oluşturulduğunda varsayılan metod GET olmalı """
    
    link = HateoasLink(href="/api/v1/users/1")
    assert link.href == "/api/v1/users/1"
    assert link.method == "GET"

def test_hateoas_link_custom_method():
    """ Farklı HTTP method belirtiğinde doğru dönmeli """

    link = HateoasLink(href="/api/v1/users", method="POST")
    assert link.method == "POST"

def test_hateoas_link_to_dict():
    """ to_dict() metodu href ve method içeren dict döndürmeli """
    link = HateoasLink(href="/api/v1/users", method="DELETE")
    result = link.to_dict()
    assert result == {"href": "/api/v1/users", "method": "DELETE"}

def test_build_response_contains_links():
    """Tek kaynak yanıtında _links anahtarı bulunmalı."""
    builder = HateoasBuilder(base_url="/api/v1")
    response = builder.build_response(
        data={"id": "1", "name": "Boran"},
        links={
            "self": HateoasLink(href="/api/v1/users/1"),
        }
    )
    assert "_links" in response
    assert response["_links"]["self"]["href"] == "/api/v1/users/1"
    assert response["name"] == "Boran"
    
def test_collection_response_has_pagination_meta():
    """Koleksiyon yanıtında meta (page, total) bilgisi olmalı."""
    builder = HateoasBuilder(base_url="/api/v1")
    response = builder.collection_response(
        items=[{"id": "1"}, {"id": "2"}],
        resource_name="users",
        page=1,
        per_page=10,
        total=25,
    )
    assert response["meta"]["page"] == 1
    assert response["meta"]["total"] == 25
    assert len(response["data"]) == 2

def test_collection_response_has_next_link_when_more_pages():
    """Sonraki sayfa varsa _links içinde 'next' linki olmalı."""
    builder = HateoasBuilder(base_url="/api/v1")
    response = builder.collection_response(
        items=[], resource_name="products", page=1, per_page=10, total=30
    )
    assert "next" in response["_links"]

def test_collection_response_has_prev_link_on_page_two():
    """Sayfa 2'deyken _links içinde 'prev' linki olmalı."""
    builder = HateoasBuilder(base_url="/api/v1")
    response = builder.collection_response(
        items=[], resource_name="products", page=2, per_page=10, total=30
    )
    assert "prev" in response["_links"]

def test_collection_response_no_prev_on_first_page():
    """İlk sayfada 'prev' linki olmamalı."""
    builder = HateoasBuilder(base_url="/api/v1")
    response = builder.collection_response(
        items=[], resource_name="products", page=1, per_page=10, total=30
    )
    assert "prev" not in response["_links"]