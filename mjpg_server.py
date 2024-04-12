import time
import io
from picamera2 import Picamera2
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# MJPEG streamer class
class MJPEGStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--myboundary')
            self.end_headers()

            try:
                with Picamera2() as camera:
                    print("Config camera")
                    camera.start()
                    data = io.BytesIO()
                    print("Camera started")
                    start = time.time()
                    bytes_tx = 0
                    while True:
                        camera.capture_file(data, format='jpeg')
                        self.wfile.write(b'--myboundary\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        jpg_size = len(data.getvalue())
                        bytes_tx += jpg_size
                        self.send_header('Content-length', jpg_size)
                        self.end_headers()
                        self.wfile.write(data.getvalue())
                        data.seek(0)
                        data.truncate()
                        #time.sleep(0.1)
                        stop = time.time()
                        if (stop - start) > 1.0:
                          diff = stop - start
                          mbps = (bytes_tx / diff) / 1000000
                          print(f'Mbps: {mbps}')
                          bytes_tx = 0
                          start = stop

            except Exception as e:
                print(f"Error: {e}")
        else:
            self.send_response(404)
            self.end_headers()

# HTTP server setup
def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    print("Starting MJPG server")
    server_thread = threading.Thread(target=run_server, args=(HTTPServer, MJPEGStreamHandler, 8000))
    server_thread.start()
