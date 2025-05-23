import socket
import threading
import time
import os

class Server:
    def __init__(self, addr, port, timeout):
        # initialize server variables
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.sessions = {}  # store client names
        
        # create and set up the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.addr, self.port))
        
        # for tracking when to timeout
        self.last_connection_time = time.time()
        self.running = True
        
    def start_server(self):
        # start listening for connections
        self.server_socket.listen(5)
        
        while self.running:
            try:
                # wait for client to connect
                self.server_socket.settimeout(self.timeout)
                client_socket, client_address = self.server_socket.accept()
                self.last_connection_time = time.time()
                
                # start a new thread for each client
                client_thread = threading.Thread(target=self.handle_request, args=(client_socket,))
                client_thread.start()
            except socket.timeout:
                # check if we should stop the server due to timeout
                if time.time() - self.last_connection_time > self.timeout:
                    self.stop_server()
                    break
            except socket.error:
                if not self.running:
                    break

    def stop_server(self):
        # stop the server
        self.running = False
        try:
            # connect to our own server to unblock accept()
            temp_socket = socket.create_connection((self.addr, self.port))
            temp_socket.close()
        except:
            pass  # if this fails, that's okay
        self.server_socket.close()

    def parse_request(self, request_data):
        try:
            # split the request into headers and body
            parts = request_data.split('\r\n\r\n')
            headers_part = parts[0]
            body = parts[1] if len(parts) > 1 else ''
            
            # get the request line and headers
            lines = headers_part.split('\r\n')
            request_line = lines[0]
            
            # parse headers into a dictionary
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
                    
            return request_line, headers, body
        except:
            # if anything goes wrong, return None for everything
            return None, None, None

    def handle_request(self, client_socket):
        try:
            # get the request data from client
            request_data = client_socket.recv(4096).decode('utf-8')
            if not request_data:
                return
            
            # parse the request
            request_line, headers, body = self.parse_request(request_data)
            if not request_line:
                return
            
            # get the method and path
            method, path, _ = request_line.split(' ')
            
            # handle different types of requests
            if method == 'GET':
                self.handle_get_request(client_socket, path)
            elif method == 'POST':
                self.handle_post_request(client_socket, path, headers, body)
            else:
                self.handle_unsupported_method(client_socket, method)
                
        except Exception as e:
            print(f"Oops, something went wrong: {e}")
        finally:
            client_socket.close()

    def handle_get_request(self, client_socket, file_path):
        # if no file specified, use index.html
        if file_path == '/':
            file_path = '/index.html'
            
        # get the actual file path
        full_path = os.path.join('assets', file_path.lstrip('/'))
        
        try:
            # try to open and read the file
            with open(full_path, 'r') as file:
                content = file.read()
                
                # replace {{name}} with client's name if we have it
                client_ip = client_socket.getpeername()[0]
                if client_ip in self.sessions:
                    content = content.replace('{{name}}', self.sessions[client_ip])
                else:
                    content = content.replace('{{name}}', '')
                    
                # create and send response
                response = f"HTTP/1.1 200 OK\r\n"
                response += f"Content-Type: text/html\r\n"
                response += f"Content-Length: {len(content)}\r\n"
                response += "\r\n"
                response += content
                
                client_socket.send(response.encode())
        except FileNotFoundError:
            # file wasn't found, send 404
            error_msg = "HTTP/1.1 404 Not Found\r\n\r\nFile not found"
            client_socket.send(error_msg.encode())

    def handle_post_request(self, client_socket, path, headers, body):
        if path == '/change_name':
            # try to get the name from the form data
            name = None
            if '=' in body:
                key, value = body.split('=', 1)
                if key == 'name':
                    name = value
            
            if name:
                # store the client's name and send success response
                client_ip = client_socket.getpeername()[0]
                self.sessions[client_ip] = name
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/html\r\n\r\n"
                response += f"<html><body>Name updated to {name}</body></html>"
            else:
                # no name provided in the form
                response = "HTTP/1.1 400 Bad Request\r\n\r\nName not provided"
        else:
            # tried to POST to an invalid path
            response = "HTTP/1.1 404 Not Found\r\n\r\nEndpoint not found"
            
        client_socket.send(response.encode())

    def handle_unsupported_method(self, client_socket, method):
        # handle any HTTP methods we don't support
        response = f"HTTP/1.1 405 Method Not Allowed\r\n"
        response += "Content-Type: text/html\r\n\r\n"
        response += f"<html><body>Method {method} is not supported</body></html>"
        client_socket.send(response.encode())