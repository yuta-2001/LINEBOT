import os

def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val][0]

def get_image_file_url(filename: str) -> str:
    return f"{os.environ.get('BASE_URL')}/images/{filename}"
