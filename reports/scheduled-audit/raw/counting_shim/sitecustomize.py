"""Counts every urllib request a tool makes, without changing tool behaviour."""
import atexit
import json
import os
import urllib.request

_OUT = os.environ.get("COUNT_OUT")
if _OUT:
    _orig = urllib.request.urlopen
    _calls = []

    def _counted(req, *args, **kwargs):
        url = getattr(req, "full_url", req)
        _calls.append(str(url).split("?")[0])
        return _orig(req, *args, **kwargs)

    urllib.request.urlopen = _counted
    atexit.register(lambda: json.dump(_calls, open(_OUT, "w")))
