import base64
import uuid


def generate_new_uuid():
    """Generates a UUID and returns it in Base64

        Base64 is for making the generated ID URL-friendly.
    """
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')
    return r_uuid.replace('=', '')

