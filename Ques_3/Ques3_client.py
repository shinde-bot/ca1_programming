
import socket
import json

HOST = "127.0.0.1"
PORT = 5000

def collect_input():
    print("=== DBS Admission Application ===")
    name = input("Enter your full name: ").strip()
    address = input("Enter your address: ").strip()
    education = input("Enter your educational qualifications: ").strip()
    print("Available courses: MSc Cyber Security, MSc Information Systems & Computing, MSc Data Analytics")
    course = input("Enter the course you wish to enroll in: ").strip()
    start_year = input("Enter intended start year (YYYY): ").strip()
    start_month = input("Enter intended start month (MM or M): ").strip()

    return {
        "name": name,
        "address": address,
        "education": education,
        "course": course,
        "start_year": start_year,
        "start_month": start_month
    }

def main():
    applicant = collect_input()
    data = json.dumps(applicant).encode("utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        s.sendall(data)
        s.shutdown(socket.SHUT_WR)

        
        resp_chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp_chunks.append(chunk)
        resp = b"".join(resp_chunks).decode("utf-8")
        try:
            resp_json = json.loads(resp)
            if resp_json.get("status") == "ok":
                print("\nApplication successful.")
                print("Your application number:", resp_json.get("application_number"))
            else:
                print("\nServer returned an error:", resp_json.get("message"))
        except json.JSONDecodeError:
            print("\nUnexpected response from server:", resp)

if __name__ == "__main__":
    main()
