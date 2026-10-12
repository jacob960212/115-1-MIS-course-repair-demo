from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_FORMATS = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF", "webp": "WEBP"}
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_BYTES + 1024 * 1024
app.config["UPLOAD_FOLDER"] = Path(app.static_folder) / "uploads"


@app.errorhandler(RequestEntityTooLarge)
def upload_too_large(error):
    return jsonify({"message": "圖片不得超過 5 MB，請縮小圖片後再送出。"}), 413


def save_image(upload):
    extension = Path(upload.filename).suffix.lower().lstrip(".")
    if extension not in IMAGE_FORMATS:
        raise ValueError("圖片格式不支援，請選擇 JPG、PNG、GIF 或 WebP。")
    content = upload.stream.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise ValueError("圖片不得超過 5 MB，請縮小圖片後再送出。")
    try:
        with Image.open(BytesIO(content)) as image:
            if image.format != IMAGE_FORMATS[extension]:
                raise ValueError("圖片內容與副檔名不符，請重新選擇圖片。")
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError("圖片無法讀取，請選擇有效的圖片檔案。") from error
    folder = Path(app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    (folder / filename).write_bytes(content)
    return url_for("static", filename=f"uploads/{filename}")

# 教學用：資料只暫存在記憶體。重新啟動程式後會清空。
tickets = []


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/admin")
def admin():
    return render_template("admin.html")


@app.get("/api/tickets")
def list_tickets():
    return jsonify(tickets)


@app.post("/api/tickets")
def create_ticket():
    # 保留原有 JSON 呼叫；圖片表單使用 multipart/form-data。
    data = (request.get_json(silent=True) or {}) if request.is_json else request.form

    location = str(data.get("location", "")).strip()
    equipment = str(data.get("equipment", "")).strip()
    description = str(data.get("description", "")).strip()
    urgency = str(data.get("urgency", "一般")).strip()
    contact = str(data.get("contact", "")).strip()

    missing = []
    if not location:
        missing.append("地點")
    if not equipment:
        missing.append("設備")
    if not description:
        missing.append("問題描述")
    if not contact:
        missing.append("聯絡方式")

    if missing:
        return jsonify({"message": f"請填寫：{'、'.join(missing)}"}), 400

    uploads = [item for item in request.files.getlist("image") if item.filename]
    if len(uploads) > 1:
        return jsonify({"message": "每張報修單只能附上一張圖片。"}), 400
    image_url = None
    if uploads:
        try:
            image_url = save_image(uploads[0])
        except ValueError as error:
            return jsonify({"message": str(error)}), 400

    ticket = {
        "id": f"T-{len(tickets) + 1:03d}",
        "location": location,
        "equipment": equipment,
        "description": description,
        "urgency": urgency or "一般",
        "contact": contact,
        "status": "待處理",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "image": image_url,
    }
    tickets.append(ticket)

    return jsonify(
        {
            "message": f"報修已建立，案件編號為 {ticket['id']}",
            "ticket": ticket,
        }
    ), 201


@app.patch("/api/tickets/<ticket_id>")
def update_ticket(ticket_id):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip()
    allowed_statuses = {"待處理", "處理中", "已完成"}

    if status not in allowed_statuses:
        return jsonify({"message": "案件狀態不正確"}), 400

    ticket = next((item for item in tickets if item["id"] == ticket_id), None)
    if ticket is None:
        return jsonify({"message": "找不到指定案件"}), 404

    ticket["status"] = status
    return jsonify({"message": f"{ticket_id} 已更新為「{status}」", "ticket": ticket})


if __name__ == "__main__":
    app.run(debug=True)
