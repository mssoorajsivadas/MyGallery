import sqlite3


def init_db():
    connection = sqlite3.connect("my_gallery.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            thumbnail_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            modified_time REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def get_image(path):
    connection = sqlite3.connect("my_gallery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT file_size, modified_time
        FROM images
        WHERE path = ?
    """, (str(path),))

    data = cursor.fetchone()

    cursor.close()
    connection.close()

    return data


def needs_update(path, file_size, modified_time):
    existing = get_image(path)

    if existing is None:
        return True

    saved_file_size, saved_modified_time = existing

    return (
        saved_file_size != file_size
        or saved_modified_time != modified_time
    )


def save_or_update_image(
    path,
    thumbnail_path,
    file_size,
    modified_time
):
    connection = sqlite3.connect("my_gallery.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO images (
            path,
            thumbnail_path,
            file_size,
            modified_time
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(path) DO UPDATE SET
            thumbnail_path = excluded.thumbnail_path,
            file_size = excluded.file_size,
            modified_time = excluded.modified_time
    """, (
        str(path),
        str(thumbnail_path),
        file_size,
        modified_time
    ))

    connection.commit()
    connection.close()


def get_all_images():
    connection = sqlite3.connect("my_gallery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT path, thumbnail_path
        FROM images
        ORDER BY id DESC
    """)

    images = cursor.fetchall()

    cursor.close()
    connection.close()

    return images