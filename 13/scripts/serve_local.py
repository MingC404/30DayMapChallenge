"""Serve only ignored local output on loopback. Does not expose the repository."""
import http.server, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs)
print('Local review: http://127.0.0.1:8013/output/Where_Night_Comes_From.html', flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1',8013),handler).serve_forever()
