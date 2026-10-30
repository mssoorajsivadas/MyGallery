from pathlib import Path
from PIL import Image, ImageOps
import hashlib


def create_cache_folder():
    cache_folder = Path.home() / ".cache" / "mygallery"
    cache_folder.mkdir(parents=True, exist_ok=True)

    return cache_folder


def generate_thumbnail(image_path):
    image_path = Path(image_path)
    cache_folder = create_cache_folder()

    image_hash = hashlib.sha256(
        str(image_path.resolve()).encode()
    ).hexdigest()

    thumbnail_path = cache_folder / f"{image_hash}.jpg"

    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((500, 500))

        image = image.convert("RGB")
        image.save(thumbnail_path, "JPEG", quality=85)

    return thumbnail_path