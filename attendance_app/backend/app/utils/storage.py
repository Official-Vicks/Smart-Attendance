from supabase import create_client
from app.config import settings
import uuid

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def upload_profile_image(file, user_id: int):
    ext = file.filename.split(".")[-1]
    filename = f"user_{user_id}_{uuid.uuid4()}.{ext}"

    content = file.file.read()

    supabase.storage.from_("profile-images").upload(
        filename,
        content,
        {
            "content-type": file.content_type
        }
    )

    public_url = supabase.storage.from_("profile-images").get_public_url(filename)
    return public_url
