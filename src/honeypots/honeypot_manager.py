#!/usr/bin/env python3
"""Minimal honeypot manager used for local/dev runs.

Provides a simple HTTP /health endpoint and lightweight TCP listeners
on the ports declared in `docker-compose.production.yml` so the container
stays up and reports healthy. This is intentionally simple and safe.
"""
import logging
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
HTTP_PORT = 8080
HONEY_PORTS = [22, 21, 80, 443, 3306, 5432, 502, 1025]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("honeypot_manager")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{\"status\": \"ok\"}\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.info("HTTP %s - %s" % (self.path, format % args))


def start_http():
    server = HTTPServer((HOST, HTTP_PORT), HealthHandler)
    logger.info(f"HTTP health server listening on {HOST}:{HTTP_PORT}")
    try:
        server.serve_forever()
    except Exception:
        server.server_close()


def tcp_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, port))
        sock.listen(5)
        logger.info(f"TCP honeypot listening on {HOST}:{port}")
        while True:
            conn, addr = sock.accept()
            logger.info(f"Connection on port {port} from {addr}")
            try:
                # Simple polite banner, then close
                banner = f"Welcome to fake service on port {port}\n".encode()
                conn.sendall(banner)
            except Exception:
                pass
            finally:
                conn.close()
    except PermissionError:
        logger.warning(f"Permission denied binding to port {port}; continuing")
    except Exception as e:
        logger.exception(f"Listener on port {port} failed: {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass


def main():
    # Start HTTP health server
    t = threading.Thread(target=start_http, daemon=True)
    t.start()

    # Start lightweight TCP listeners for each honeypot port
    for p in HONEY_PORTS:
        th = threading.Thread(target=tcp_listener, args=(p,), daemon=True)
        th.start()

    # Keep main thread alive
    try:
        while True:
            threading.Event().wait(60)
    except KeyboardInterrupt:
        logger.info("Shutting down honeypot manager")


if __name__ == "__main__":
    main()
