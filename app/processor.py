from .scanner import scan_folder
from .database import needs_update, save_or_update_image
from .thumbnail import generate_thumbnail


def process_folder(folder_path):
    images = scan_folder(folder_path)

    processed = 0
    skipped = 0
    failed = 0

    for image in images:
        try:
            path = image["path"]
            file_size = image["file_size"]
            modified_time = image["modified_time"]

            if not needs_update(
                path,
                file_size,
                modified_time
            ):
                skipped += 1
                continue

            thumbnail_path = generate_thumbnail(path)

            save_or_update_image(
                path,
                thumbnail_path,
                file_size,
                modified_time
            )

            processed += 1

        except Exception as error:
            failed += 1
            print(f"Failed: {image['path']}")
            print(f"{type(error).__name__}: {error}")

    return {
        "processed": processed,
        "skipped": skipped,
        "failed": failed
    }