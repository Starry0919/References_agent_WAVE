import json
import urllib.request


class DownloadError(Exception):
    pass


class BinaryTransport:
    def get(self, url, headers=None):
        request = urllib.request.Request(url, headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return {
                    "data": response.read(),
                    "content_type": response.headers.get("Content-Type", ""),
                    "final_url": response.geturl()
                }
        except Exception as exc:
            raise DownloadError(str(exc)) from exc


class JsonTransport:
    def get_json(self, url, headers=None):
        request = urllib.request.Request(url, headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise DownloadError(str(exc)) from exc
