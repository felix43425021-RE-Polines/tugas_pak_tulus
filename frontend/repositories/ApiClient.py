import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


class ApiError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url=None, timeout=3):
        self.base_url = (base_url or os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
        self.timeout = timeout

    def request(self, method, path, data=None, params=None):
        url = f"{self.base_url}{path}"
        if params:
            query = urlencode({key: value for key, value in params.items() if value is not None})
            if query:
                url = f"{url}?{query}"

        body = None
        headers = {"Accept": "application/json"}
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8")
                if not raw_body:
                    return None
                return json.loads(raw_body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ApiError(detail or str(exc), status_code=exc.code) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ApiError(str(exc)) from exc

    def get(self, path, params=None):
        return self.request("GET", path, params=params)

    def post(self, path, data=None):
        return self.request("POST", path, data=data)

    def patch(self, path, data=None):
        return self.request("PATCH", path, data=data)

    def delete(self, path, params=None):
        return self.request("DELETE", path, params=params)

    def is_available(self):
        try:
            self.get("/")
            return True
        except ApiError:
            return False
