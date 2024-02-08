import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt


def get_coords(scale, coords):
    if scale > 21:
        scale = 20
    elif scale <= 0:
        scale = 1
    scale = int(scale)

    if scale == 1 or scale == 0:  # более красивое отображение
        coords = coords.split(',')
        coords[-1] = '0'
        coords = ','.join(coords)
    return coords


def check_response(response):
    if not response:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        quit()


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.SCREEN_SIZE = [600, 520]
        self.coords = "39.847061,57.576481"
        self.scale = 1
        self.cur_type_map = 'map'
        self.setGeometry(100, 100, *self.SCREEN_SIZE)
        self.setWindowTitle('Задание 4')
        self.get_image(self.coords, self.scale)

        self.combobox = Combo(self)
        self.combobox.move(240, 465)
        self.combobox.resize(110, 20)
        self.combobox.addItems(('карта', 'спутник', 'гибрид'))

        self.btn = QPushButton('Сменить тип карты', self)
        self.btn.move(240, 485)
        self.btn.resize(110, 30)
        self.btn.clicked.connect(self.btn_click)

        # Изображение
        self.pixmap = QPixmap('map.png')
        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def btn_click(self):
        translate = {'карта': 'map', 'спутник': 'sat', 'гибрид': 'sat,skl'}
        self.cur_type_map = translate[self.combobox.currentText()]
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))

    def get_image(self, coords, scale):
        coords = get_coords(scale, coords)

        search_params = {
            'll': coords,
            'z': scale,
            'l': self.cur_type_map
        }
        link = 'http://static-maps.yandex.ru/1.x/'

        response = requests.get(link, search_params)
        check_response(response)

        # Запишем полученное изображение в файл.
        self.map_file = f"map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.scale < 20:
            self.scale += 1
        elif event.key() == Qt.Key_PageDown and self.scale > 0:
            self.scale -= 1

        if event.key() == Qt.Key_Left:
            cords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            cords[0] = str(float(cords[0]) - abs(step))
            if abs(float(cords[0])) >= 180:
                return
            self.coords = ','.join(cords)

        elif event.key() == Qt.Key_Right:
            cords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            cords[0] = str(float(cords[0]) + abs(step))
            if abs(float(cords[0])) >= 180:
                return
            self.coords = ','.join(cords)

        elif event.key() == Qt.Key_Up:
            cords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            cords[1] = str(float(cords[1]) + abs(step))
            if abs(float(cords[1])) >= 90:
                return
            self.coords = ','.join(cords)

        elif event.key() == Qt.Key_Down:
            cords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            cords[1] = str(float(cords[1]) - abs(step))
            if abs(float(cords[1])) >= 90:
                return
            self.coords = ','.join(cords)

        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap('map.png'))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove('map.png')


class Combo(QComboBox):
    def keyPressEvent(self, event):
        ex.keyPressEvent(event)


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = Example()
    ex.show()
    sys.exit(app.exec())
