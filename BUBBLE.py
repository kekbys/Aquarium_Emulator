import random
from PyQt5 import Qt, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget


class Bubble(QWidget):
    def __init__(self, position, radius, image_path):
        super().__init__()
        self.position = position
        self.radius = radius
        self.image = QPixmap(image_path).scaledToWidth(2 * radius, QtCore.Qt.SmoothTransformation)
        self.x_speed = random.uniform(0, 0)  # Случайная скорость по горизонтали
        self.y_speed = random.uniform(-3, -1)  # Случайная скорость по вертикали
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # Обновление с частотой 60 Гц

    def update(self):
        x, y = self.position

        # Изменение позиции пузырька
        x += self.x_speed
        y += self.y_speed

        # Проверка, достиг ли пузырек верхней границы экрана
        if y <= -self.radius:
            # Сброс позиции пузырька на нижнюю границу экрана
            y = self.parent().height() + self.radius

        # Ограничение спавна пузырьков за пределами окна
        if x <= 0:
            x = 0
        elif x >= self.parent().width() - self.radius:
            x = self.parent().width() - self.radius

        self.setGeometry(x, y, 2 * self.radius, 2 * self.radius)

        self.position = (x, y)
        self.repaint()
