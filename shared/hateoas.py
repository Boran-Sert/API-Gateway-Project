""" RMM Seviye - 3 HATEOAS uyumlu response oluşturma """

from typing import Any

class HateoasLink:
    """ Tek bir HATEOAS linkini temsil eder """

    def __init__(self, href: str, method: str ="GET", rel: str | None = None):
        self.href = href
        self.method = method
        self.rel = rel
    
    def to_dict(self) -> dict[str,str]:
        result = {"href": self.href, "method": self.method}
        if self.rel:
            result["rel"] = self.rel
        return result

class HateoasBuilder:
    """ HATEOAS ile uyumlu response oluştur """

    def __init__(self, base_url: str = "/api/v1"):
        self.base_url = base_url
    
    def build_response(self, data: dict[str, Any], links: dict[str, HateoasLink]) -> dict [str, Any]:
        """Tek kaynak için HATEOAS response üretir."""
        return {
            **data,
            "_links": {name: link.to_dict() for name, link in links.items()},
        }
    def collection_response(
        self,
        items: list[dict],
        resource_name: str,
        page: int = 1,
        per_page: int = 20,
        total: int = 0,
    ) -> dict[str, Any]:
        """Koleksiyon için paginated HATEOAS response üretir."""
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        base = f"{self.base_url}/{resource_name}"
        links: dict[str, HateoasLink] = {
            "self": HateoasLink(href=f"{base}?page={page}&per_page={per_page}"),
            "create": HateoasLink(href=base, method="POST"),
        }
        if page > 1:
            links["prev"] = HateoasLink(
                href=f"{base}?page={page - 1}&per_page={per_page}"
            )
        if page < total_pages:
            links["next"] = HateoasLink(
                href=f"{base}?page={page + 1}&per_page={per_page}"
            )
        return {
            "data": items,
            "meta": {"page": page, "per_page": per_page, "total": total},
            "_links": {k: v.to_dict() for k, v in links.items()},
        }  