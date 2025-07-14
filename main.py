import webbrowser
import hashlib
import random
import string
import time
import json
import threading
import os
from flask import Flask, render_template, request, jsonify, redirect, make_response
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Bật chế độ debug
app.config['DEBUG'] = True

# Địa chỉ server Flask
HOST = "127.0.0.1"
PORT = 2502

# Khai báo các biến quan trọng
# Thêm các constant cho upload
UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Tạo thư mục upload nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Khai báo các hàm quan trọng
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            
        for sess in sessions["active_sessions"]:
            if sess["session_id"] == session_id:
                return render_template("tcn.html")

        resp = make_response(redirect("/dangnhap"))
        resp.set_cookie("sessionID", "", expires=0)
        return resp
            
    except Exception as e:
        print("Lỗi:", str(e))
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
    
@app.route('/api/upload-avatar', methods=['POST'])
def upload_avatar():
    # Kiểm tra đăng nhập
    session_id = request.cookies.get("sessionID")
    if not session_id:
        return jsonify({"message": "Chưa đăng nhập", "code": 401})

    # Lấy username từ session
    try:
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
            
        username = None
        for sess in sessions["active_sessions"]:
            if sess["session_id"] == session_id:
                username = sess["username"]
                break
                
        if not username:
            return jsonify({"message": "Phiên đăng nhập không hợp lệ", "code": 401})
            
    except Exception as e:
        return jsonify({"message": "Lỗi server", "code": 500})

    # Kiểm tra file upload
    if 'avatar' not in request.files:
        return jsonify({"message": "Không tìm thấy file", "code": 400})
        
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"message": "Chưa chọn file", "code": 400})

    # Kiểm tra định dạng và kích thước file
    if not allowed_file(file.filename):
        return jsonify({
            "message": f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}", 
            "code": 400
        })
        
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return jsonify({
            "message": "File quá lớn. Kích thước tối đa là 5MB",
            "code": 400
        })

    try:
        # Tạo tên file mới từ username
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{username}_avatar_{int(time.time())}.{extension}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Xóa avatar cũ nếu có
        try:
            with open("database/datauser.json", "r", encoding="UTF-8") as f:
                users_data = json.load(f)
                
            for user in users_data["userlist"]:
                if user["username"] == username and "avatar" in user:
                    old_avatar = user["avatar"].split("/")[-1]
                    old_path = os.path.join(UPLOAD_FOLDER, old_avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
        except:
            pass # Bỏ qua lỗi khi xóa file cũ
        
        # Lưu file mới
        file.save(filepath)
        
        # Cập nhật database
        with open("database/datauser.json", "r", encoding="UTF-8") as f:
            users_data = json.load(f)
            
        for user in users_data["userlist"]:
            if user["username"] == username:
                user["avatar"] = f"/static/avatars/{filename}"
                break
                
        with open("database/datauser.json", "w", encoding="UTF-8") as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
        
        return jsonify({
            "message": "Upload thành công",
            "code": 200,
            "avatar_url": f"/static/avatars/{filename}"
        })
        
    except Exception as e:
        return jsonify({
            "message": f"Lỗi khi xử lý file: {str(e)}",
            "code": 500
        })
    
@app.route("/api/get-user-info", methods=["GET"])
def get_user_info():
    session_id = request.cookies.get("sessionID")
    if not session_id:
        return jsonify({"message": "Chưa đăng nhập", "code": 401})

    try:
        # Lấy username từ session
        with open("database/session.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
            
        username = None
        for sess in sessions["active_sessions"]:
            if sess["session_id"] == session_id:
                username = sess["username"]
                break
                
        if not username:
            return jsonify({"message": "Phiên đăng nhập không hợp lệ", "code": 401})

        # Lấy thông tin user từ database
        with open("database/datauser.json", "r", encoding="UTF-8") as f:
            users_data = json.load(f)
            
        for user in users_data["userlist"]:
            if user["username"] == username:
                return jsonify({
                    "code": 200,
                    "data": {
                        "username": user["username"],
                        "age": user.get("age", ""),
                        "gender": user.get("gender", ""),
                        "hobby": user.get("hobby", ""),
                        "note": user.get("note", ""),
                        "avatar": user.get("avatar", "https://i.imgur.com/JqkXKzL.jpg")
                    }
                })
                
        return jsonify({"message": "Không tìm thấy thông tin người dùng", "code": 404})
            
    except Exception as e:
        print("Lỗi:", str(e))
        return jsonify({"message": "Lỗi server", "code": 500})
    

# Chỉ mở trình duyệt nếu đây là tiến trình chính (tránh auto-reload)
def open_browser():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  # Chỉ chạy khi Flask khởi động lần đầu
        webbrowser.open(f"http://{HOST}:{PORT}/", new=2)

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(host=HOST, port=PORT)