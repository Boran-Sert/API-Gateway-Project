import yaml
from typing import Dict, Any, Optional
class RouteManager:
    """Yönlendirme rotalarını yöneten OCP uyumlu sınıf."""
    def __init__(self, config_file: str):
        self.routes = self._load_routes(config_file)
    def _load_routes(self, config_file: str) -> list[Dict[str, Any]]:
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("routes", [])
    def get_route(self, path: str) -> Optional[Dict[str, Any]]:
        """Path ile eşleşen ilk rotayı döndürür. (Bug #2 Çözümü)"""
        sorted_routes = sorted(
            self.routes, key=lambda x: len(x["match_prefix"]), reverse=True
        )
        for route in sorted_routes:
            prefix = route["match_prefix"]
            if path == prefix or path.startswith(prefix + "/"):
                return route
        return None
    def build_target_url(
        self, route: Dict[str, Any], original_path: str, query_params: str
    ) -> str:
        """Hedef URL'yi inşa eder."""
        target_base = route["target_url"]
        prefix = route["match_prefix"]
        if route.get("strip_prefix", False):
            path_remainder = original_path[len(prefix) :]
            if path_remainder and not path_remainder.startswith("/"):
                path_remainder = "/" + path_remainder
        else:
            path_remainder = original_path
        target_url = target_base.rstrip("/") + path_remainder
        if query_params:
            target_url = f"{target_url}?{query_params}"
        return target_url