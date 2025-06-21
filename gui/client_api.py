import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = b'Sixteen byte key'  # בדיוק כמו בשרת!
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

def encrypt_msg(msg):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(msg.encode(), AES.block_size))
    return cipher.iv + ct_bytes

def decrypt_msg(enc_msg):
    iv = enc_msg[:16]
    ct = enc_msg[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def send_request(action, data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        payload = {"action": action}
        payload.update(data)
        json_data = json.dumps(payload)
        enc_data = encrypt_msg(json_data)
        client_socket.send(enc_data)
        enc_resp = client_socket.recv(16384)
        resp_json = decrypt_msg(enc_resp)
        client_socket.close()
        return json.loads(resp_json)
    except Exception as e:
        return {"status": "fail", "message": str(e)}


# --- פעולות משתמשים ---
def register(username, password, email):
    return send_request("register", {"username": username, "password": password, "email": email})

def login(username, password):
    return send_request("login", {"username": username, "password": password})

# --- פעולות שוברים ---
def add_coupon(user_id, coupon_data):
    return send_request("add_coupon", {"user_id": user_id, "coupon": coupon_data})

def delete_coupon(coupon_id):
    return send_request("delete_coupon", {"coupon_id": coupon_id})

def get_user_coupons(user_id):
    return send_request("get_user_coupons", {"user_id": user_id})

def toggle_favorite(user_id, coupon_id):
    return send_request("toggle_favorite", {"user_id": user_id, "coupon_id": coupon_id})

def get_favorites(user_id):
    return send_request("get_favorites", {"user_id": user_id})

def duplicate_coupon(coupon_id, user_id):
    return send_request("duplicate_coupon", {"coupon_id": coupon_id, "user_id": user_id})

def get_deleted_coupons(user_id):
    return send_request("get_deleted_coupons", {"user_id": user_id})

def restore_coupon(coupon_id):
    return send_request("restore_coupon", {"coupon_id": coupon_id})

def get_expiring_coupons(user_id, days):
    return send_request("get_expiring_coupons", {"user_id": user_id, "days": days})

def filter_coupons(user_id, filters, sort_by=None):
    return send_request("filter_coupons", {"user_id": user_id, "filters": filters, "sort_by": sort_by})

# --- ייצוא ---
def export_excel(user_id):
    return send_request("export_excel", {"user_id": user_id})

def export_csv(user_id):
    return send_request("export_csv", {"user_id": user_id})

# --- יומן פעילות ---
def get_logs(user_id):
    return send_request("get_logs", {"user_id": user_id})

def get_user_logs(user_id):

    return send_request("get_logs", {"user_id": user_id})

def db_get_user_logs(user_id):
    return send_request("get_logs", {"user_id": user_id})

