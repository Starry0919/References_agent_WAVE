import json
import urllib.parse
import urllib.request


class DatabaseUnavailable(Exception):
    pass


class JsonTransport:
    def get_json(self, url, params=None, headers=None):
        target = url
        if params:
            target += "?" + urllib.parse.urlencode(params, doseq=True)
        request = urllib.request.Request(target, headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise DatabaseUnavailable(str(exc)) from exc

