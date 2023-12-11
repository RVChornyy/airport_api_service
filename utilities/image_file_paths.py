import os
import uuid

from django.utils.text import slugify


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.call_sign)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)
