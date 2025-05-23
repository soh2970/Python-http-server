# Simple Python HTTP Server

## Overview

This project is a lightweight multithreaded HTTP server written in Python. It handles GET and POST requests, manages per-client sessions, serves static files with dynamic string replacement, and automatically shuts down after a period of inactivity.

## Features

- Serve static HTML files for GET requests
- Handle POST requests to update session data (e.g., name)
- Replace placeholders like `{{name}}` in HTML based on session info
- Concurrent client handling with threading
- Graceful shutdown after a configurable timeout period
- Session tracking using client IP addresses

## How It Works

- Each client connection spawns a new thread
- Sessions are stored in a Python dictionary (`self.sessions`)
- GET requests serve files from the current working directory
- POST requests update session information using form data
- Placeholder `{{name}}` in HTML is dynamically replaced

## Getting Started

### Requirements

- Python 3.x

### Run the Server

```bash
python server.py
```

Default settings: `127.0.0.1:8080`, inactivity timeout = 10 seconds

## Example Requests

### GET

```
GET /index.html HTTP/1.1
Host: localhost
```

### POST

```
POST /name HTTP/1.1
Host: localhost
Content-Length: 9

name=Alice
```

## Code Overview

- `__init__`: Sets up the server socket, initializes sessions
- `start_server`: Main loop to listen and accept clients
- `handle_client`: Handles each request in a new thread
- `handle_get`: Serves HTML files and performs placeholder replacement
- `handle_post`: Updates client name in session
- `shutdown_server`: Called after inactivity to terminate server

## Notes

- Ensure HTML files use `{{name}}` where session info should be displayed.
- This is a minimal educational HTTP server; it doesn't support MIME types or security features.
- Designed for use in academic environments or learning projects.

## License

MIT License — Educational use only.
