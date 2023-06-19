import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QTransform
from PyQt5.QtCore import Qt, QTimer, QDateTime, QRect
from BUBBLE import Bubble

class Fish:
    def __init__(self, image, flipped_image, initial_pos, speed):
        self.image = image
        self.flipped_image = flipped_image
        self.position = initial_pos
        self.direction = 1
        self.speed = speed

    def move(self, bounds, elapsed_time):
        x, y = self.position
        step = self.speed * elapsed_time / 1000

        if self.direction == 1:
            x += step
            if x >= bounds.width() - self.image.width():
                self.direction = -1
                self.image = self.flipped_image
        else:
            x -= step
            if x <= 0:
                self.direction = 1
                self.image = self.image.transformed(QTransform().scale(-1, 1))

        y = max(0, min(y, bounds.height() - self.image.height()))

        self.position = (x, y)

class Feed:
    def __init__(self, image, position, speed):
        self.image = image
        self.position = position
        self.speed = speed

    def move(self, bounds, elapsed_time):
        x, y = self.position
        step = self.speed * elapsed_time / 1000

        y += step
        if y >= bounds.height() - self.image.height():
            return True

        self.position = (x, y)
        return False

class AquariumEmulator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("Аквариум")
        self.setWindowState(Qt.WindowFullScreen)  # Установить окно в полноэкранный режим
        self.init_ui()

        self.fish_list = []
        self.feed_list = []
        self.fish_counter = 0
        self.bubble_list = []  # Добавлен список для пузырьков

        for _ in range(10):
            x = random.randint(50, self.width() - 50)
            y = random.randint(50, self.height() - 50)
            radius = random.randint(10, 30)
            bubble = Bubble((x, y), radius, "bubble.png")
            self.bubble_list.append(bubble)
            bubble.setParent(self.central_widget)

        fish_flipped_image = QPixmap("remove_fish.png").scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio)

        self.remove_fish_button = QPushButton(self)
        self.remove_fish_button.setGeometry(135, 10, 40, 40)
        self.remove_fish_button.setIcon(QIcon(fish_flipped_image))
        self.remove_fish_button.setIconSize(fish_flipped_image.rect().size())
        self.remove_fish_button.clicked.connect(self.remove_fish)

        self.remove_all_fish_button = QPushButton("Удалить всех рыбок", self)
        self.remove_all_fish_button.setGeometry(180, 10, 180, 40)
        self.remove_all_fish_button.clicked.connect(self.remove_all_fish)

        self.background_button = QPushButton("изменить фон", self)
        self.background_button.setGeometry(self.width() - 180, 10, 130, 30)
        self.background_button.clicked.connect(self.show_background)

        self.select_fish_button = QPushButton("Выбрать рыбку", self)
        self.select_fish_button.setGeometry(self.width() - 1910, 10, 120, 40)
        self.select_fish_button.clicked.connect(self.show_fish_selection)

        self.close_button = QPushButton(self)
        self.close_button.setGeometry(self.width() - 40, 10, 30, 30)
        self.close_button.setIcon(QIcon("cross.png"))
        self.close_button.setIconSize(self.close_button.rect().size())
        self.close_button.clicked.connect(self.close)

        self.background_widget = None
        self.feed_tool_enabled = False

        self.last_update_time = QDateTime.currentMSecsSinceEpoch()

        self.timer = QTimer(self)
        self.timer.setInterval(16)  # Фиксированный интервал обновления (приблизительно 60 кадров в секунду)
        self.timer.timeout.connect(self.update_aquarium)
        self.timer.start()

    def init_ui(self):
        self.set_background("akvarium6.jpg")
        self.create_fish_counter_label()

    def set_background(self, image_path):
        self.background_pixmap = QPixmap(image_path).scaled(self.width(), self.height())
        self.background_rect = self.background_pixmap.rect()
        self.update()

    def create_fish_counter_label(self):
        self.fish_counter_label = QLabel(self)
        self.fish_counter_label.setGeometry(10, 60, 200, 30)
        self.fish_counter_label.setStyleSheet("background-color: black; color: white;")
        self.fish_counter_label.setAlignment(Qt.AlignCenter)
        self.fish_counter_label.setText("Количество рыб: 0")

    def update_fish_counter(self):
        self.fish_counter_label.setText(f"Количество рыб: {self.fish_counter}")

    def update_aquarium(self):
        current_time = QDateTime.currentMSecsSinceEpoch()
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time

        for fish in self.fish_list:
            fish.move(self.rect(), elapsed_time)

        for feed in self.feed_list:
            if feed.move(self.rect(), elapsed_time):
                self.feed_list.remove(feed)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.background_rect, self.background_pixmap)

        for fish in self.fish_list:
            painter.drawPixmap(
                QRect(fish.position[0], fish.position[1], fish.image.width(), fish.image.height()), fish.image
            )

        for feed in self.feed_list:
            painter.drawPixmap(
                QRect(feed.position[0], feed.position[1], feed.image.width(), feed.image.height()), feed.image
            )

        for bubble in self.bubble_list:
            x, y = bubble.position
            painter.drawPixmap(x - bubble.radius, y - bubble.radius, bubble.image)

    def add_fish(self):
        fish_image = QPixmap("fish.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        fish_flipped_image = QPixmap("fish_flipped.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)

        pos = (
            random.randint(0, self.width() - fish_image.width()),
            random.randint(0, self.height() - fish_image.height()),
        )
        speed = random.uniform(100, 200)
        fish = Fish(fish_image, fish_flipped_image, pos, speed)
        self.fish_list.append(fish)
        self.fish_counter += 1
        self.update_fish_counter()

    def remove_fish(self):
        if self.fish_list:
            self.fish_list.pop()
            self.fish_counter -= 1
            self.update_fish_counter()

    def remove_all_fish(self):
        self.fish_list = []
        self.fish_counter = 0
        self.update_fish_counter()

    def show_fish_selection(self):
        if self.background_widget is None:
            self.background_widget = QWidget(self)
            background_width = self.width() - 1000
            background_height = self.height() - 300
            x = int((self.width() - background_width) / 2)
            y = int((self.height() - background_height) / 2)
            self.background_widget.setGeometry(x, y, background_width, background_height)
            self.background_widget.setStyleSheet("background-color: white;")

            fish_images = ["fish.png", "fish2.png", "fish3.png", "fish4.png", "fish5.png", "fish6.png", "fish7.png",
                           "fish8.png", "fish9.png"]
            image_width = 200
            image_height = 200
            x_offset = (background_width - (image_width + 20) * 3) / 2
            y_offset = 50
            for i, image_path in enumerate(fish_images):
                fish_button = QPushButton(self.background_widget)
                fish_button.setGeometry(QRect(x_offset, y_offset, image_width, image_height))
                pixmap = QPixmap(image_path).scaled(image_width, image_height, Qt.AspectRatioMode.KeepAspectRatio)
                fish_button.setIcon(QIcon(pixmap))
                fish_button.setIconSize(pixmap.rect().size())
                fish_button.clicked.connect(lambda _, path=image_path: self.add_selected_fish(path))
                x_offset += image_width + 20
                if (i + 1) % 3 == 0:
                    x_offset = (background_width - (image_width + 20) * 3) / 2
                    y_offset += image_height + 20

            self.background_widget.show()
        else:
            self.background_widget.close()
            self.background_widget = None

    def select_feed_tool(self):
        self.feed_tool_enabled = not self.feed_tool_enabled
        if self.feed_tool_enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def add_selected_fish(self, image_path):
        fish_image = QPixmap(image_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        fish_flipped_image = QPixmap(image_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio).transformed(
            QTransform().scale(-1, 1)
        )

        pos = (
            random.randint(0, self.width() - fish_image.width()),
            random.randint(0, self.height() - fish_image.height()),
        )
        speed = random.uniform(100, 200)
        fish = Fish(fish_image, fish_flipped_image, pos, speed)
        self.fish_list.append(fish)
        self.fish_counter += 1
        self.update_fish_counter()

    def show_background(self):
        if self.background_widget is None:
            self.background_widget = QWidget(self)
            background_width = self.width() - 900
            background_height = self.height() - 100
            x = int((self.width() - background_width) / 2)
            y = int((self.height() - background_height) / 2)
            self.background_widget.setGeometry(x, y, background_width, background_height)
            self.background_widget.setStyleSheet("background-color: white;")

            images = [
                "akvarium.jpg",
                "akvarium2.jpg",
                "akvarium3.jpg",
                "akvarium4.jpg",
                "akvarium5.jpg",
                "akvarium6.jpg",
                "akvarium7.jpg",
                "akvarium8.jpg",
                "akvarium9.jpg",
            ]
            image_width = 290
            image_height = 290
            x_offset = (background_width - (image_width + 20) * 3) / 2
            y_offset = 50
            for i, image_path in enumerate(images):
                image_button = QPushButton(self.background_widget)
                image_button.setGeometry(QRect(x_offset, y_offset, image_width, image_height))
                pixmap = QPixmap(image_path).scaled(image_width, image_height, Qt.AspectRatioMode.KeepAspectRatio)
                image_button.setIcon(QIcon(pixmap))
                image_button.setIconSize(pixmap.rect().size())
                image_button.clicked.connect(lambda _, path=image_path: self.set_selected_background(path))
                x_offset += image_width + 20
                if (i + 1) % 3 == 0:
                    x_offset = (background_width - (image_width + 20) * 3) / 2
                    y_offset += image_height + 20

            self.background_widget.show()
        else:
            self.background_widget.close()
            self.background_widget = None

    def set_selected_background(self, image_path):
        self.set_background(image_path)
        if self.background_widget is not None:
            self.background_widget.close()
            self.background_widget = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    emulator = AquariumEmulator()
    emulator.show()
    sys.exit(app.exec_())