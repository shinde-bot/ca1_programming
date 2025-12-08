import socket
import sqlite3
import threading
import uuid
import json
import re
import traceback
import time

DB_PATH = "applicants.db"
HOST = "127.0.0.1"
PORT = 5000

ALLOWED_COURSES = {
    "MSc Cyber Security",
    "MSc Information Systems & Computing",
    "MSc Data Analytics",
    "MSc Cybersecurity",
    "MSc Information Systems and Computing",
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS applicants (
        app_number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        education TEXT NOT NULL,
        course TEXT NOT NULL,
        start_year TEXT NOT NULL,
        start_month TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


def recv_all(sock, size_limit=100_000, timeout=None):
    """
    Read until the peer closes the write side or a timeout occurs.
    Returns the bytes read (may be empty).
    Defensive: stops if accumulated size > size_limit.
    """
    if timeout is not None:
        sock.settimeout(timeout)
    chunks = []
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if sum(len(c) for c in chunks) > size_limit:
                
                break
    except socket.timeout:
       
        pass
    except Exception:
        
        raise
    finally:
        
        try:
            sock.settimeout(None)
        except Exception:
            pass
    return b"".join(chunks)


def validate_applicant(app):
    required = ["name","address","education","course","start_year","start_month"]
    if not all(field in app for field in required):
        return False, "Missing one or more required fields."
    
    if app["course"] not in ALLOWED_COURSES:
        return False, f"Course '{app['course']}' not recognized."
    if not re.fullmatch(r"\d{4}", app["start_year"]):
        return False, "start_year must be YYYY."
    if not re.fullmatch(r"\d{1,2}", app["start_month"]) or not (1 <= int(app["start_month"]) <= 12):
        return False, "start_month must be 1-12 (MM)."
    return True, ""


def handle_client(client_socket, addr):
    
    client_socket.settimeout(10)
    try:
        raw = recv_all(client_socket, timeout=10)
        print(f"[{addr}] Received {len(raw)} bytes")
        if not raw:
           
            print(f"[{addr}] No data received; closing connection")
            client_socket.close()
            return

        try:
            applicant = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"[{addr}] Invalid JSON received")
            safe_send(client_socket, {"status":"error","message":"Invalid JSON."})
            return

        print(f"[{addr}] Decoded JSON keys: {list(applicant.keys())}")

        ok, msg = validate_applicant(applicant)
        if not ok:
            safe_send(client_socket, {"status":"error","message":msg})
            return

        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        
        app_number = uuid.uuid4().hex[:8].upper()

        cur.execute('''
            INSERT INTO applicants (app_number, name, address, education, course, start_year, start_month)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            app_number,
            applicant["name"],
            applicant["address"],
            applicant["education"],
            applicant["course"],
            applicant["start_year"],
            str(int(applicant["start_month"])).zfill(2)
        ))
        conn.commit()
        conn.close()

        resp = {"status":"ok","application_number":app_number}
        safe_send(client_socket, resp)

        print(f"[{addr}] Stored application {app_number} for {applicant['name']} ({applicant['course']})")
    except Exception:
        print(f"Error handling client {addr}")
        traceback.print_exc()
        try:
            safe_send(client_socket, {"statsus":"error","message":"Internal server error."})
        except Exception:
            pass
    finally:
        try:
            client_socket.close()
        except Exception:
            pass


def safe_send(sock, obj):
    """Send JSON-encoded obj to sock; swallow socket errors to avoid raising while handling errors."""
    try:
        data = json.dumps(obj).encode("utf-8")
        sock.sendall(data)
    except Exception:
        
        pass


def main():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except Exception:
        print("Failed to bind to", HOST, PORT)
        traceback.print_exc()
        return

    server.listen(5)
    print(f"Server listening on {HOST}:{PORT} ... (CTRL+C to stop)")

    try:
        while True:
            try:
                client_sock, addr = server.accept()
            except KeyboardInterrupt:
                
                raise
            except Exception:
                print("Error during accept():")
                traceback.print_exc()
                time.sleep(0.5)
                continue

            print("Accepted connection from", addr)

            try:
                t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
                t.start()
            except Exception:
                print("Failed to start thread for", addr)
                traceback.print_exc()
                try:
                    client_sock.close()
                except Exception:
                    pass

    except KeyboardInterrupt:
        print("Shutting down server (KeyboardInterrupt).")
    except Exception:
        print("Unexpected server error:")
        traceback.print_exc()
    finally:
        try:
            server.close()
        except Exception:
            pass
        print("Server socket closed.")


if __name__ == "__main__":
    main()
