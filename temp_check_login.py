import urllib.request
import urllib.error
try:
    resp = urllib.request.urlopen('http://127.0.0.1:5555/auth/login')
    data = resp.read().decode('utf-8', errors='replace')
    print('status', resp.status)
    print(data[:1200])
except urllib.error.HTTPError as e:
    print('status', e.code)
    print(e.read().decode('utf-8', errors='replace')[:1200])
except Exception as exc:
    print('error', repr(exc))
