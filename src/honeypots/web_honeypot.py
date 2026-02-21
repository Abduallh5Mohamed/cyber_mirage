"""
🌐 Advanced HTTP/HTTPS Honeypot with Fake Login Pages
=====================================================

Simulates realistic web services with:
- WordPress admin login
- phpMyAdmin login  
- cPanel login
- Custom admin panels
- Form handling and credential capture
- Session tracking
"""

import socket
import threading
import logging
import json
import uuid
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_honeypot")


class WebHoneypot:
    """Advanced Web Honeypot with Multiple Fake Services"""
    
    def __init__(self, host="0.0.0.0", http_port=8080, https_port=8443):
        self.host = host
        self.http_port = http_port
        self.https_port = https_port
        self.sessions = {}
        
    def get_wordpress_login(self):
        """Fake WordPress admin login page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Log In &lsaquo; WordPress Admin</title>
    <style>
        body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen-Sans,Ubuntu,Cantarell,"Helvetica Neue",sans-serif; background: #f1f1f1; }
        #login { width: 320px; padding: 8% 0 0; margin: auto; }
        #loginform { background: #fff; padding: 26px 24px 46px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
        h1 { text-align: center; margin: 0 0 25px; }
        h1 a { background-image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48cGF0aCBkPSJNNjEuNyAyNTZjMC0xMDAuNyA4MS45LTE4Mi42IDE4Mi42LTE4Mi42czE4Mi42IDgxLjkgMTgyLjYgMTgyLjYtODEuOSAxODIuNi0xODIuNiAxODIuNlM2MS43IDM1Ni43IDYxLjcgMjU2em0zMzggMGMwLTg1LjgtNjkuOS0xNTUuNy0xNTUuNy0xNTUuN1MxMDkgMTcwLjIgMTA5IDI1NnM2OS45IDE1NS43IDE1NS43IDE1NS43UzM5OS43IDM0MS44IDM5OS43IDI1NnoiLz48L3N2Zz4=); width: 84px; height: 84px; background-size: 84px; display: block; margin: 0 auto 25px; text-indent: -9999px; }
        .input { font-size: 24px; width: 100%; padding: 3px; margin: 0 6px 16px 0; }
        label { font-size: 14px; line-height: 1.5; display: inline-block; margin-bottom: 3px; }
        .submit { background: #2271b1; border-color: #2271b1; color: #fff; text-decoration: none; text-shadow: none; height: 40px; padding: 0 12px; line-height: 40px; font-size: 14px; border: 1px solid; border-radius: 3px; cursor: pointer; width: 100%; margin-top: 16px; }
        .submit:hover { background: #135e96; border-color: #135e96; }
    </style>
</head>
<body class="login">
    <div id="login">
        <h1><a href="/">WordPress</a></h1>
        <form name="loginform" id="loginform" action="/wp-login.php" method="post">
            <p>
                <label for="user_login">Username or Email Address</label>
                <input type="text" name="log" id="user_login" class="input" value="" size="20" autocomplete="username">
            </p>
            <div>
                <label for="user_pass">Password</label>
                <input type="password" name="pwd" id="user_pass" class="input" value="" size="20" autocomplete="current-password">
            </div>
            <p class="submit">
                <input type="submit" name="wp-submit" id="wp-submit" class="submit" value="Log In">
            </p>
        </form>
    </div>
</body>
</html>"""

    def get_phpmyadmin_login(self):
        """Fake phpMyAdmin login page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>phpMyAdmin</title>
    <style>
        body { font-family: sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 100px auto; background: white; border: 1px solid #ddd; border-radius: 4px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,.1); }
        .logo { text-align: center; margin-bottom: 30px; font-size: 24px; color: #ff9900; font-weight: bold; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        input[type="text"], input[type="password"], select { width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; padding: 10px; background: #ff9900; color: white; border: none; border-radius: 3px; font-size: 16px; cursor: pointer; font-weight: 600; }
        input[type="submit"]:hover { background: #e68a00; }
        .server-info { font-size: 12px; color: #666; margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">phpMyAdmin</div>
        <form action="/phpmyadmin/index.php" method="post">
            <div class="form-group">
                <label for="pma_servername">Server:</label>
                <select name="pma_servername" id="pma_servername">
                    <option value="localhost">localhost</option>
                </select>
            </div>
            <div class="form-group">
                <label for="pma_username">Username:</label>
                <input type="text" name="pma_username" id="pma_username" autocomplete="username">
            </div>
            <div class="form-group">
                <label for="pma_password">Password:</label>
                <input type="password" name="pma_password" id="pma_password" autocomplete="current-password">
            </div>
            <input type="submit" value="Go">
        </form>
        <div class="server-info">phpMyAdmin 5.2.0 | MySQL 8.0.32</div>
    </div>
</body>
</html>"""

    def get_cpanel_login(self):
        """Fake cPanel login page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>cPanel Login</title>
    <style>
        body { margin: 0; font-family: Lato,'Helvetica Neue',Helvetica,Arial,sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,.2); width: 400px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo-text { font-size: 32px; font-weight: 700; color: #ff6c00; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; font-size: 14px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px; box-sizing: border-box; transition: border-color 0.3s; }
        input[type="text"]:focus, input[type="password"]:focus { outline: none; border-color: #ff6c00; }
        .btn-login { width: 100%; padding: 14px; background: #ff6c00; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; margin-top: 10px; }
        .btn-login:hover { background: #e65c00; }
        .version { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">
            <div class="logo-text">cPanel</div>
        </div>
        <form action="/cpanel/login" method="post">
            <div class="form-group">
                <label for="user">Username</label>
                <input type="text" name="user" id="user" autocomplete="username">
            </div>
            <div class="form-group">
                <label for="pass">Password</label>
                <input type="password" name="pass" id="pass" autocomplete="current-password">
            </div>
            <button type="submit" class="btn-login">Log in</button>
        </form>
        <div class="version">cPanel Version 110.0 (build 18)</div>
    </div>
</body>
</html>"""

    def get_admin_panel(self):
        """Generic admin panel login"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #141E30; background: linear-gradient(to right, #243B55, #141E30); height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: rgba(255, 255, 255, 0.95); padding: 50px 40px; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,.5); width: 380px; }
        h2 { text-align: center; color: #333; margin-bottom: 30px; font-size: 28px; }
        .icon { text-align: center; font-size: 60px; margin-bottom: 20px; }
        .input-group { position: relative; margin-bottom: 25px; }
        .input-group input { width: 100%; padding: 12px 15px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; transition: all 0.3s; }
        .input-group input:focus { outline: none; border-color: #4CAF50; }
        .input-group label { position: absolute; top: 12px; left: 15px; color: #999; transition: all 0.3s; pointer-events: none; }
        .input-group input:focus + label, .input-group input:not(:placeholder-shown) + label { top: -10px; left: 10px; font-size: 12px; color: #4CAF50; background: white; padding: 0 5px; }
        button { width: 100%; padding: 14px; background: linear-gradient(to right, #56ab2f, #a8e063); border: none; border-radius: 8px; color: white; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,.3); }
        .footer { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="icon">🔐</div>
        <h2>Admin Panel</h2>
        <form action="/admin/auth" method="post">
            <div class="input-group">
                <input type="text" name="username" placeholder=" " required autocomplete="username">
                <label>Username</label>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder=" " required autocomplete="current-password">
                <label>Password</label>
            </div>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">Admin Control Panel v2.5.1</div>
    </div>
</body>
</html>"""

    def get_router_login(self):
        """Fake router admin page"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Router Configuration</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f0f0f0; }
        .header { background: #003d82; color: white; padding: 15px 20px; font-size: 18px; font-weight: bold; }
        .container { max-width: 500px; margin: 80px auto; background: white; border: 1px solid #ccc; border-radius: 5px; }
        .login-area { padding: 40px; }
        h3 { color: #003d82; margin-bottom: 25px; text-align: center; }
        .form-row { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; }
        input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; }
        .btn { width: 100%; padding: 12px; background: #0066cc; color: white; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #0052a3; }
        .device-info { background: #f9f9f9; padding: 15px; margin-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">TP-Link Wireless N Router WR841N</div>
    <div class="container">
        <div class="login-area">
            <h3>Configuration Login</h3>
            <form action="/router/login" method="post">
                <div class="form-row">
                    <label>Username:</label>
                    <input type="text" name="username" value="admin" autocomplete="username">
                </div>
                <div class="form-row">
                    <label>Password:</label>
                    <input type="password" name="password" autocomplete="current-password">
                </div>
                <button type="submit" class="btn">Log In</button>
            </form>
            <div class="device-info">
                <strong>Device Model:</strong> TL-WR841N v14<br>
                <strong>Firmware Version:</strong> 3.16.9 Build 20190924 Rel.37644<br>
                <strong>Hardware Version:</strong> WR841N v14 00000001
            </div>
        </div>
    </div>
</body>
</html>"""

    def parse_post_data(self, data):
        """Parse POST form data"""
        try:
            # Find the body after \r\n\r\n
            parts = data.split(b'\r\n\r\n', 1)
            if len(parts) < 2:
                return {}
            
            body = parts[1].decode('utf-8', errors='ignore')
            parsed = parse_qs(body)
            
            # Convert to simple dict
            result = {}
            for key, values in parsed.items():
                result[key] = values[0] if values else ''
            
            return result
        except:
            return {}

    def handle_http_request(self, conn, addr, port):
        """Handle HTTP request and serve appropriate page"""
        session_id = str(uuid.uuid4())
        
        try:
            conn.settimeout(30)
            data = conn.recv(4096)
            
            if not data:
                return
            
            # Parse HTTP request
            request_line = data.split(b'\r\n')[0].decode('utf-8', errors='ignore')
            method, path, _ = request_line.split() if len(request_line.split()) >= 3 else ('GET', '/', 'HTTP/1.1')
            
            logger.info(f"[{port}] {addr[0]} -> {method} {path}")
            
            # Track session
            self.sessions[session_id] = {
                'ip': addr[0],
                'port': port,
                'path': path,
                'method': method,
                'timestamp': datetime.now().isoformat(),
                'attempts': 0
            }
            
            # Handle POST requests (login attempts)
            if method == 'POST':
                post_data = self.parse_post_data(data)
                logger.warning(f"[CREDS CAPTURED] {addr[0]} -> {post_data}")
                
                # Log credentials to file
                with open('/app/data/captured_credentials.json', 'a') as f:
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'ip': addr[0],
                        'path': path,
                        'credentials': post_data,
                        'session_id': session_id
                    }
                    f.write(json.dumps(log_entry) + '\n')
                
                # Send fake "login failed" response
                response = """HTTP/1.1 401 Unauthorized\r
Content-Type: text/html\r
Connection: close\r
\r
<!DOCTYPE html>
<html><head><title>Login Failed</title></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 100px;">
<h2>⚠️ Login Failed</h2>
<p>Invalid username or password. Please try again.</p>
<a href="/">Back to Login</a>
</body></html>"""
                conn.sendall(response.encode())
                return
            
            # Serve appropriate login page based on path
            if 'wp-admin' in path or 'wp-login' in path:
                html = self.get_wordpress_login()
            elif 'phpmyadmin' in path.lower():
                html = self.get_phpmyadmin_login()
            elif 'cpanel' in path.lower():
                html = self.get_cpanel_login()
            elif 'router' in path.lower() or 'admin' in path.lower():
                html = self.get_router_login()
            else:
                # Default: show generic admin panel
                html = self.get_admin_panel()
            
            # Send HTTP response
            response = f"""HTTP/1.1 200 OK\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: {len(html)}\r
Server: Apache/2.4.41 (Ubuntu)\r
Connection: close\r
\r
{html}"""
            
            conn.sendall(response.encode())
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
        finally:
            conn.close()

    def start_listener(self, port):
        """Start TCP listener for specific port"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind((self.host, port))
            sock.listen(5)
            logger.info(f"✅ Web honeypot listening on {self.host}:{port}")
            
            while True:
                conn, addr = sock.accept()
                threading.Thread(
                    target=self.handle_http_request,
                    args=(conn, addr, port),
                    daemon=True
                ).start()
                
        except Exception as e:
            logger.error(f"Error on port {port}: {e}")
        finally:
            sock.close()

    def start(self):
        """Start HTTP and HTTPS honeypots"""
        # HTTP listener
        threading.Thread(
            target=self.start_listener,
            args=(self.http_port,),
            daemon=True
        ).start()
        
        # HTTPS listener (same logic, just different port)
        threading.Thread(
            target=self.start_listener,
            args=(self.https_port,),
            daemon=True
        ).start()
        
        logger.info("🌐 Web honeypots started successfully!")


if __name__ == "__main__":
    honeypot = WebHoneypot()
    honeypot.start()
    
    # Keep running
    import time
    while True:
        time.sleep(60)
