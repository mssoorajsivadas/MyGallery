from pathlib import Path

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"
}


def scan_folder(folder_path):
    folder = Path(folder_path)
    images = []

    if not folder.exists() or not folder.is_dir():
        return images

    for item in folder.rglob("*"):
        try:
            if not item.is_file():
                continue

            if item.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            file_info = item.stat()

            images.append({
                "path": item,
                "file_size": file_info.st_size,
                "modified_time": file_info.st_mtime
            })

        except (PermissionError, OSError) as error:
            print(f"Skipping {item}: {error}")

    return images