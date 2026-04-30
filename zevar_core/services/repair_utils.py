import uuid

def generate_secure_filename(repair_order: str, filename: str) -> str:
    ext = ".jpg"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    if filename and "." in filename:
        parsed_ext = "." + filename.rsplit(".", 1)[-1].lower()
        if parsed_ext in ALLOWED_EXTENSIONS:
            ext = parsed_ext
        
    return f"customer_photo_{repair_order}_{uuid.uuid4().hex[:12]}{ext}"
