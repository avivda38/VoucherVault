import socket
import threading
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from database import add_log


import database

AES_KEY = b'Sixteen byte key'  # 16/24/32 bytes, keep same key in client too!

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

def handle_client(client_socket):
    try:
        enc_data = client_socket.recv(16384)
        if not enc_data:
            client_socket.close()
            return
        data = decrypt_msg(enc_data)
        request = json.loads(data)
        action = request.get('action')
        response = {}

        # --- Register --- #
        if action == "register":
            username = request['username']
            password = request['password']
            email = request.get('email', None)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            result = database.add_user(username, password_hash, email)
            response = {"status": "ok"} if result else {"status": "fail", "message": "User already exists or DB error"}

        # --- Login --- #
        elif action == "login":
            username = request['username']
            password = request['password']
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = database.login_user(username, password_hash)
            if user:
                response = {"status": "ok", "user_id": user['id'], "username": user['username']}
            else:
                response = {"status": "fail", "message": "Invalid username or password"}

        # --- Add Coupon --- #
        elif action == "add_coupon":
            user_id = request['user_id']
            coupon_data = request['coupon']
            result = database.add_coupon(user_id, **coupon_data)
            if result:
                add_log(user_id, "הוספת שובר", f"{coupon_data.get('code', '')}")
                response = {"status": "ok"}
            else:
                response = {"status": "fail"}




        # --- Delete Coupon --- #
        elif action == "delete_coupon":
            coupon_id = request['coupon_id']
            result = database.delete_coupon(coupon_id)
            if result:

                response = {"status": "ok"}
            else:
                response = {"status": "fail"}

        # --- Update Coupon --- #
        elif action == "update_coupon":
            coupon_id = request['coupon_id']
            updates = request['updates']
            result = database.update_coupon(coupon_id, updates)
            response = {"status": "ok"} if result else {"status": "fail"}

        # --- Get User Coupons --- #
        elif action == "get_user_coupons":
            user_id = request['user_id']
            database.get_user_logs(user_id)
            coupons = database.get_user_coupons(user_id)
            response = {"status": "ok", "coupons": coupons}

        # --- Favorites --- #
        elif action == "toggle_favorite":
            coupon_id = request['coupon_id']
            user_id = request['user_id']
            result = database.toggle_favorite(user_id, coupon_id)
            response = {"status": "ok"} if result else {"status": "fail"}

        elif action == "get_favorites":
            user_id = request['user_id']
            favorites = database.get_favorite_coupons(user_id)
            response = {"status": "ok", "favorites": favorites}

        # --- Export to Excel --- #
        elif action == "export_excel":
            user_id = request['user_id']
            file_path = database.export_coupons_to_excel(user_id)
            response = {"status": "ok", "file_path": file_path} if file_path else {"status": "fail"}

        # --- Export to CSV --- #
        elif action == "export_csv":
            user_id = request['user_id']
            file_path = database.export_coupons_to_csv(user_id)
            response = {"status": "ok", "file_path": file_path} if file_path else {"status": "fail"}

        # --- Search Coupons --- #
        elif action == "search_coupons":
            user_id = request['user_id']
            query = request['query']
            results = database.search_coupons(user_id, query)
            response = {"status": "ok", "results": results}

        # --- Filter & Sort Coupons --- #
        elif action == "filter_sort_coupons":
            user_id = request['user_id']
            filters = request.get('filters', {})
            sort_by = request.get('sort_by', "expiration_date")
            sorted_coupons = database.filter_and_sort_coupons(user_id, filters, sort_by)
            response = {"status": "ok", "coupons": sorted_coupons}

        # --- Get Alerts --- #
        elif action == "get_alerts":
            user_id = request['user_id']
            alerts = database.get_expiring_coupons(user_id)
            response = {"status": "ok", "alerts": alerts}

        # --- Mark Alert as Read --- #
        elif action == "mark_alert_read":
            user_id = request['user_id']
            coupon_id = request['coupon_id']
            result = database.mark_alert_as_read(user_id, coupon_id)
            response = {"status": "ok"} if result else {"status": "fail"}

        elif action == "get_logs":
            user_id = request.get("user_id")
            database.get_user_logs(user_id)
            response = database.get_user_logs(user_id)  # ✅ מחזיר מילון מוכן!


        else:
            response = {"status": "fail", "message": "Unknown action"}

        resp_json = json.dumps(response)
        enc_resp = encrypt_msg(resp_json)
        client_socket.send(enc_resp)

    except Exception as e:
        print("Server error:", e)
        try:
            error_resp = encrypt_msg(json.dumps({"status": "fail", "message": str(e)}))
            client_socket.send(error_resp)
        except Exception:
            pass
    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen()
    print("Server ready, waiting for connections...")

    while True:
        client, addr = server_socket.accept()
        print("Client connected:", addr)
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == "__main__":
    start_server()
