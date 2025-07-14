import webbrowser
import hashlib
import random
import string
import json
import threading
import os
from flask import Flask, render_template, request, jsonify, redirect, make_response

app = Flask(__name__)

# Bật chế độ debug
app.config['DEBUG'] = True

# Địa chỉ server Flask
HOST = "127.0.0.1"
PORT = 2502

# một số hàm tiện ích
def is_valid_session(session_id):
    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
        return any(sess["session_id"] == session_id for sess in sessions["active_sessions"])
    except:
        return False


@app.route("/")
def direct_index():
    session_id = request.cookies.get("sessionID")  # Lấy cookie sessionID từ người dùng

    # Nếu không có sessionID → redirect luôn
    if not session_id:
        return redirect("/dangnhap")

    # Đọc file session server
    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except Exception as e:
        print("Lỗi đọc session.json:", e)
        sessions = {"active_sessions": []}

    # Kiểm tra sessionID có hợp lệ không
    for sess in sessions["active_sessions"]:
        if sess["session_id"] == session_id:
            # Hợp lệ → render trang index
            return render_template("index.html")

    # Nếu không hợp lệ → xóa cookie và redirect về trang đăng nhập
    resp = make_response(redirect("/dangnhap"))
    resp.set_cookie("sessionID", "", expires=0)  # Xóa cookie
    return resp

@app.route("/trangchu")
def index():
    session_id = request.cookies.get("sessionID")  # Lấy cookie sessionID từ người dùng

    # Nếu không có sessionID → redirect luôn
    if not session_id:
        return redirect("/dangnhap")

    # Đọc file session server
    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except Exception as e:
        print("Lỗi đọc session.json:", e)
        sessions = {"active_sessions": []}

    # Kiểm tra sessionID có hợp lệ không
    for sess in sessions["active_sessions"]:
        if sess["session_id"] == session_id:
            # Hợp lệ → render trang index
            return render_template("index.html")

    # Nếu không hợp lệ → xóa cookie và redirect về trang đăng nhập
    resp = make_response(redirect("/dangnhap"))
    resp.set_cookie("sessionID", "", expires=0)  # Xóa cookie
    return resp

@app.route("/profile")
def profile():
    session_id = request.cookies.get("sessionID")

    if not session_id:
        return redirect("/dangnhap")

    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except Exception as e:
        print("Lỗi đọc session.json:", e)
        sessions = {"active_sessions": []}

    for sess in sessions["active_sessions"]:
        if sess["session_id"] == session_id:
            return render_template("tcn.html")  # Nếu session đúng, hiển thị trang cá nhân

    # Nếu session không hợp lệ → xóa cookie và chuyển về đăng nhập
    resp = make_response(redirect("/dangnhap"))
    resp.set_cookie("sessionID", "", expires=0)
    return resp

@app.route("/chat")
def chat():
    session_id = request.cookies.get("sessionID")

    if not session_id:
        return redirect("/dangnhap")

    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except Exception as e:
        print("Lỗi đọc session.json:", e)
        sessions = {"active_sessions": []}

    for sess in sessions["active_sessions"]:
        if sess["session_id"] == session_id:
            return render_template("chat.html")  # Nếu session đúng, hiển thị trang chat

    # Nếu session không hợp lệ → xóa cookie và chuyển về đăng nhập
    resp = make_response(redirect("/dangnhap"))
    resp.set_cookie("sessionID", "", expires=0)
    return resp


@app.route("/dangnhap")
def dn():
    session_id = request.cookies.get("sessionID")
    if session_id and is_valid_session(session_id):
        return redirect("/")  # Nếu đã đăng nhập thì không cho vào trang login nữa
    return render_template("login.html")


@app.route("/dangki")
def dk():
    session_id = request.cookies.get("sessionID")
    if session_id and is_valid_session(session_id):
        return redirect("/")  # Nếu đã đăng nhập thì không cho vào trang đăng ký nữa
    return render_template("signup.html")

@app.route("/api/logout", methods=["POST"])
def logout():
    session_id = request.cookies.get("sessionID")

    # Nếu không có session thì coi như đã đăng xuất
    if not session_id:
        resp = make_response(jsonify({
            "message": "Chưa đăng nhập",
            "code": 400
        }))
        resp.set_cookie("sessionID", "", expires=0)
        return resp

    try:
        # Đọc session hiện có
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)

        # Xóa sessionID khỏi danh sách
        original_count = len(sessions["active_sessions"])
        sessions["active_sessions"] = [
            sess for sess in sessions["active_sessions"]
            if sess["session_id"] != session_id
        ]

        # Ghi lại vào file
        with open("database/session.json", "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=4)

        # Tạo response xóa cookie và trả kết quả
        resp = make_response(jsonify({
            "message": "Đăng xuất thành công",
            "code": 200,
            "removed": original_count - len(sessions["active_sessions"])
        }))
        resp.set_cookie("sessionID", "", expires=0)
        return resp

    except Exception as e:
        print("Lỗi khi đăng xuất:", str(e))
        resp = make_response(jsonify({
            "message": "Lỗi server khi đăng xuất",
            "code": 500
        }))
        resp.set_cookie("sessionID", "", expires=0)
        return resp

@app.route("/api/dn", methods=["POST"])
def apidn():
    get_data = request.get_json()

    try:
        # Đọc dữ liệu người dùng
        with open("database/datauser.json", "r", encoding="UTF-8") as f:
            loaded_data = json.load(f)

        for user in loaded_data["userlist"]:
            if user["username"] == get_data['username']:
                if user["pass"] == get_data['pass']:
                    # Tạo chuỗi session ID
                    base_str = user["username"] + user["pass"] + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                    session_id = hashlib.sha256(base_str.encode()).hexdigest()

                    # Ghi session ID vào file session.json
                    with open("database/session.json", "r", encoding="utf-8") as f:
                        sessions = json.load(f)
                    
                    sessions["active_sessions"].append({
                        "session_id": session_id,
                        "username": user["username"]
                    })

                    with open("database/session.json", "w", encoding="utf-8") as f:
                        json.dump(sessions, f, indent=4)

                    # Trả về session ID cho client
                    return {
                        "message": "Đăng nhập thành công!",
                        "code": 200,
                        "session_id": session_id,  # phía JS sẽ ghi vào cookie
                        "user_data": {
                            "username": user["username"],
                            "age": user["age"],
                            "gender": user["gender"],
                            "hobby": user["hobby"]
                        }
                    }
                else:
                    return {
                        "message": "Sai mật khẩu!",
                        "code": 401
                    }

        return {
            "message": "Tài khoản không tồn tại",
            "code": 404
        }

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {
            "message": "Có lỗi xảy ra",
            "code": 500
        }

@app.route("/api/dki", methods = ["POST"])
def apidki(): 
    # lấy dữ liệu từ phía website gửi lên
    get_data = request.get_json()  
    
    try:
        # đọc dữ liệu từ file json trước
        with open("database/datauser.json","r",encoding="UTF-8") as openedfile: 
            loaded_data = json.load(openedfile)
        
        # kiểm tra tài khoản tồn tại
        for tk in loaded_data["userlist"]:
            if tk["username"] == get_data['username']:
                return { "message" : "tk đã tồn tại", "code" : 400}
            
        # tạo user mới nếu không trùng
        new_user = {
            "username": get_data['username'],
            "pass": get_data['pass'],
            "age": get_data['age'],
            "gender": get_data['gender'],
            "hobby": get_data['hobby']
        }
        
        # thêm user mới và ghi lại file
        loaded_data["userlist"].append(new_user)
        with open("database/datauser.json","w",encoding="UTF-8") as openedfile:
            json.dump(loaded_data, openedfile, indent=4, ensure_ascii=False)
            
        print("đã thêm tk mới")
        return { "message" : "thành công", "code" : 200}
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return { "message" : "có lỗi xảy ra", "code" : 500}
# Chỉ mở trình duyệt nếu đây là tiến trình chính (tránh auto-reload)
def open_browser():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  # Chỉ chạy khi Flask khởi động lần đầu
        webbrowser.open(f"http://{HOST}:{PORT}/", new=2)

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(host=HOST, port=PORT)