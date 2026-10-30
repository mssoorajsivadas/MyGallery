from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QStackedWidget,
)

from PySide6.QtCore import Signal
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QTransform

from .database import get_all_images
from .processor import process_folder


class ImageLabel(QLabel):

    clicked = Signal(str)

    def __init__(self, pixmap, original_path, parent=None):
        super().__init__(parent)

        self.pixmap = pixmap
        self.original_path = str(original_path)

        self.setFixedSize(pixmap.size())
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), 12, 12)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.original_path)

        super().mousePressEvent(event)


class MainWindow(QMainWindow):

    FOLDERS = [
        Path.home() / "Pictures",
        Path.home() / "Downloads",
    ]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Gallery")
        self.resize(1400, 900)

        self.min_image_width = 210
        self.spacing = 16

        # State variables
        self.visible_images = []
        self.current_image_index = -1
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.current_pixmap = None

        # Pages: gallery and image viewer stay inside this main window.
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        # Gallery page
        self.gallery_page = QWidget()
        self.gallery_page.setObjectName("centralWidget")

        main_layout = QVBoxLayout(self.gallery_page)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(22)

        self.create_header(main_layout)
        self.create_gallery(main_layout)
        self.pages.addWidget(self.gallery_page)

        # Image viewer page
        self.create_viewer_page()

        # Search timer
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.load_gallery)

        # Initial load
        self.load_gallery()

    # ---------------------------------------------
    # Header
    # ---------------------------------------------

    def create_header(self, main_layout):

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_container = QVBoxLayout()

        title = QLabel("My Gallery")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Explore your image collection")
        subtitle.setObjectName("subtitle")

        title_container.addWidget(title)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search images...")
        self.search_input.setObjectName("searchInput")
        self.search_input.setFixedWidth(280)
        self.search_input.setFixedHeight(40)

        self.search_input.textChanged.connect(
            self.on_search_changed
        )

        header_layout.addWidget(self.search_input)

        # Refresh
        refresh_button = QPushButton("↻  Refresh")
        refresh_button.setObjectName("refreshButton")
        refresh_button.clicked.connect(self.refresh_gallery)
        refresh_button.setFixedHeight(40)

        header_layout.addWidget(refresh_button)

        main_layout.addWidget(header)

    # ---------------------------------------------
    # Gallery
    # ---------------------------------------------

    def create_gallery(self, main_layout):

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("galleryScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.gallery = QWidget()
        self.gallery.setObjectName("gallery")

        self.gallery_layout = QHBoxLayout(self.gallery)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout.setSpacing(self.spacing)
        self.gallery_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll_area.setWidget(self.gallery)

        main_layout.addWidget(self.scroll_area)

    # ---------------------------------------------
    # Search
    # ---------------------------------------------

    def on_search_changed(self, text):

        self.search_timer.start(250)

    # ---------------------------------------------
    # Load Gallery
    # ---------------------------------------------

    def load_gallery(self):

        images = get_all_images()

        search_text = self.search_input.text().lower()

        if search_text:
            images = [
                image for image in images
                if search_text in Path(image[0]).name.lower()
            ]

        # Keep the current gallery order for Previous / Next navigation.
        self.visible_images = [str(image[0]) for image in images]

        # Clear previous columns
        while self.gallery_layout.count():

            item = self.gallery_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        # Calculate available width
        available_width = self.scroll_area.viewport().width()

        if available_width <= 0:
            return

        # Calculate columns
        columns = max(
            1,
            (available_width + self.spacing)
            // (self.min_image_width + self.spacing)
        )

        # Calculate image width
        image_width = (
            available_width - (columns - 1) * self.spacing
        ) // columns

        column_layouts = []
        column_heights = [0] * columns

        # Create columns
        for _ in range(columns):

            column = QWidget()
            column.setObjectName("galleryColumn")

            layout = QVBoxLayout(column)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(self.spacing)

            column_layouts.append(layout)

            self.gallery_layout.addWidget(column)

        # Distribute images
        for original_path, thumbnail_path in images:

            pixmap = QPixmap(str(thumbnail_path))

            if pixmap.isNull():
                continue

            pixmap = pixmap.scaledToWidth(
                image_width,
                Qt.TransformationMode.SmoothTransformation
            )

            image_label = ImageLabel(pixmap, original_path)

            image_label.clicked.connect(
                self.show_image_viewer
            )

            # Find shortest column
            shortest_column = column_heights.index(
                min(column_heights)
            )

            column_layouts[shortest_column].addWidget(
                image_label,
                alignment=Qt.AlignmentFlag.AlignHCenter
            )

            column_heights[shortest_column] += (
                pixmap.height() + self.spacing
            )

        # Keep columns aligned at the top
        for layout in column_layouts:
            layout.addStretch()

        # Empty search result
        if not images:

            empty_label = QLabel("No images found")
            empty_label.setObjectName("emptyLabel")

            self.gallery_layout.addWidget(empty_label)

    # ---------------------------------------------
    # Refresh
    # ---------------------------------------------

    def refresh_gallery(self):

        for folder in self.FOLDERS:

            result = process_folder(folder)
            print(f"{folder}: {result}")

        self.load_gallery()

    # ---------------------------------------------
    # Window Resize
    # ---------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if hasattr(self, "pages") and self.pages.currentWidget() == getattr(self, "viewer_page", None):
            QTimer.singleShot(100, self.load_viewer_image)
        else:
            QTimer.singleShot(150, self.load_gallery)

    # ---------------------------------------------
    # Image Viewer Page
    # ---------------------------------------------

    def create_viewer_page(self):

        self.viewer_page = QWidget()
        self.viewer_page.setObjectName("viewerPage")

        viewer_layout = QVBoxLayout(self.viewer_page)
        viewer_layout.setContentsMargins(28, 22, 28, 22)
        viewer_layout.setSpacing(16)

        # Top bar
        top_bar = QHBoxLayout()

        back_button = QPushButton("←  Back to Gallery")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.show_gallery)
        top_bar.addWidget(back_button)

        top_bar.addStretch()

        self.viewer_filename = QLabel("")
        self.viewer_filename.setObjectName("viewerFilename")
        top_bar.addWidget(self.viewer_filename)

        top_bar.addStretch()

        viewer_layout.addLayout(top_bar)

        # Image area
        self.viewer_image_label = QLabel()
        self.viewer_image_label.setObjectName("viewerImage")
        self.viewer_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewer_image_label.setMinimumSize(200, 200)
        self.viewer_image_label.installEventFilter(self)
        viewer_layout.addWidget(self.viewer_image_label, 1)

        # Bottom bar
        bottom_bar = QHBoxLayout()

        self.viewer_file_info = QLabel("")
        self.viewer_file_info.setObjectName("viewerFileInfo")
        bottom_bar.addWidget(self.viewer_file_info)

        bottom_bar.addStretch()

        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setObjectName("navigationButton")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        bottom_bar.addWidget(self.zoom_out_button)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setObjectName("navigationButton")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        bottom_bar.addWidget(self.zoom_in_button)

        self.rotate_left_button = QPushButton("↶ Rotate")
        self.rotate_left_button.setObjectName("navigationButton")
        self.rotate_left_button.clicked.connect(self.rotate_left)
        bottom_bar.addWidget(self.rotate_left_button)

        self.rotate_right_button = QPushButton("↷ Rotate")
        self.rotate_right_button.setObjectName("navigationButton")
        self.rotate_right_button.clicked.connect(self.rotate_right)
        bottom_bar.addWidget(self.rotate_right_button)

        self.previous_button = QPushButton("←  Previous")
        self.previous_button.setObjectName("navigationButton")
        self.previous_button.clicked.connect(self.show_previous_image)
        bottom_bar.addWidget(self.previous_button)

        self.next_button = QPushButton("Next  →")
        self.next_button.setObjectName("navigationButton")
        self.next_button.clicked.connect(self.show_next_image)
        bottom_bar.addWidget(self.next_button)

        viewer_layout.addLayout(bottom_bar)

        self.pages.addWidget(self.viewer_page)

    def show_image_viewer(self, image_path):

        image_path = str(image_path)

        if image_path not in self.visible_images:
            return

        self.current_image_index = self.visible_images.index(image_path)
        self.pages.setCurrentWidget(self.viewer_page)
        self.load_viewer_image()

    def load_viewer_image(self):

        if not (0 <= self.current_image_index < len(self.visible_images)):
            return

        image_path = Path(self.visible_images[self.current_image_index])

        self.current_pixmap = QPixmap(str(image_path))
        self.viewer_filename.setText(image_path.name)

        try:
            file_size = image_path.stat().st_size
            if file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.1f} KB"
            else:
                size_text = f"{file_size / (1024 * 1024):.2f} MB"
        except OSError:
            size_text = "Unknown size"

        self.viewer_file_info.setText(
            f"{size_text}  •  {self.current_image_index + 1} of {len(self.visible_images)}"
        )

        self.update_viewer_image()

        self.previous_button.setEnabled(self.current_image_index > 0)
        self.next_button.setEnabled(
            self.current_image_index < len(self.visible_images) - 1
        )

    def show_previous_image(self):

        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_viewer_image()

    def show_next_image(self):

        if self.current_image_index < len(self.visible_images) - 1:
            self.current_image_index += 1
            self.load_viewer_image()

    def show_gallery(self):

        self.pages.setCurrentWidget(self.gallery_page)

    def update_viewer_image(self):

        if self.current_pixmap is None or self.current_pixmap.isNull():
            self.viewer_image_label.setText("Unable to open image")
            return

        # Rotate image
        transform = QTransform()
        transform.rotate(self.rotation_angle)

        rotated_pixmap = self.current_pixmap.transformed(
            transform,
            Qt.TransformationMode.SmoothTransformation
        )

        # Calculate display size
        available_size = self.viewer_image_label.contentsRect().size()

        if available_size.width() <= 0 or available_size.height() <= 0:
            return

        base_pixmap = rotated_pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Apply zoom
        final_pixmap = base_pixmap.scaled(
            int(base_pixmap.width() * self.zoom_factor),
            int(base_pixmap.height() * self.zoom_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.viewer_image_label.setPixmap(final_pixmap)

    def zoom_in(self):
        if self.pages.currentWidget() == self.viewer_page:
            self.zoom_factor = min(self.zoom_factor + 0.2, 3.0)
            self.update_viewer_image()

    def zoom_out(self):
        if self.pages.currentWidget() == self.viewer_page:
            self.zoom_factor = max(self.zoom_factor - 0.2, 0.2)
            self.update_viewer_image()

    def rotate_left(self):

        self.rotation_angle -= 90
        self.update_viewer_image()

    def rotate_right(self):

        self.rotation_angle += 90
        self.update_viewer_image()

    def eventFilter(self, watched, event):

        if watched == self.viewer_image_label:
            if event.type() == event.Type.Wheel:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:

                    if event.angleDelta().y() > 0:
                        self.zoom_in()
                    elif event.angleDelta().y() < 0:
                        self.zoom_out()

                    return True

        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        # Check if we are currently on the image viewer page
        if self.pages.currentWidget() == self.viewer_page:
            # Check for Ctrl + / Ctrl = (Zoom In)
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and (
                event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal
            ):
                self.zoom_in()
                event.accept()
                return

            # Check for Ctrl - (Zoom Out)
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and (
                event.key() == Qt.Key.Key_Minus
            ):
                self.zoom_out()
                event.accept()
                return

        super().keyPressEvent(event)