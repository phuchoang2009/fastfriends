# FastFriend.com

## Tổng quan dự án
FastFriend.com là một nền tảng web giúp người dùng kết bạn, trò chuyện và quản lý thông tin cá nhân. Dự án sử dụng Python (Flask) cho backend, HTML/CSS/JS cho frontend, lưu trữ dữ liệu bằng file JSON.

## Công nghệ sử dụng
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS (W3.CSS, custom), JavaScript (XHR, fetch)
- **Database:** File JSON (datauser.json, session.json)
- **Thư viện:** FontAwesome, Google Fonts

## Các cơ chế và hệ thống đã làm
- Đăng ký, đăng nhập, đăng xuất tài khoản
- Quản lý session đăng nhập bằng cookie và session.json
- Quản lý thông tin cá nhân: họ tên, tuổi, giới tính, sở thích, ghi chú, avatar
- Upload và cập nhật avatar
- Chỉnh sửa thông tin cá nhân
- Giao diện hiện đại, responsive

## Các route và API đã có
### Route giao diện
- `/` : Trang chủ (yêu cầu đăng nhập)
- `/trangchu` : Trang chủ (yêu cầu đăng nhập)
- `/profile` : Trang cá nhân
- `/chat` : Trang chat
- `/dangnhap` : Trang đăng nhập
- `/dangki` : Trang đăng ký

### API
- `POST /api/dn` : Đăng nhập
- `POST /api/dki` : Đăng ký
- `POST /api/logout` : Đăng xuất
- `GET /api/get-user-info` : Lấy thông tin user hiện tại
- `POST /api/update-user-info` : Cập nhật thông tin user
- `POST /api/upload-avatar` : Upload avatar

## Cấu trúc dự án
```
fastfriend.com/
├── main.py
├── run.bat
├── test.bat
├── test.py
├── database/
│   ├── datauser.json
│   └── session.json
├── static/
│   ├── avatars/
│   ├── css/
│   │   └── profile.css
│   └── img/
│       ├── avt.jpg
│       └── logo.png
├── templates/
│   ├── chat.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── tcn.html
```

## Lưu ý về frontend
- Sử dụng XHR cho các API chính, có thể dùng fetch cho upload avatar.
- Giao diện responsive, sử dụng W3.CSS và custom CSS.
- Các trường thông tin user đều có thể chỉnh sửa trực tiếp trên giao diện.

## Lưu ý về backend
- Dữ liệu user và session lưu bằng file JSON, không dùng database SQL.
- Session quản lý bằng cookie và session.json, cần bảo mật khi triển khai thực tế.
- Khi upload avatar, file cũ sẽ bị xóa khỏi thư mục avatars.
- Các API đều trả về mã lỗi và thông báo rõ ràng.

---
Nếu cần mở rộng chức năng, có thể bổ sung các API mới hoặc chuyển sang dùng database chuyên nghiệp.
