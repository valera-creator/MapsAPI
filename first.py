import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.SCREEN_SIZE = [600, 450]
        self.coords = "39.847061,57.576481"
        self.scale = 1  # значения от 1 до 21

        self.setGeometry(100, 100, *self.SCREEN_SIZE)
        self.setWindowTitle('Задание 1')
        self.get_image(self.coords, self.scale)

        # Изображение
        self.pixmap = QPixmap('map.png')
        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def get_image(self, coords, scale):
        if scale > 21:
            scale = 21
        elif scale <= 0:
            scale = 1
        scale = int(scale)

        if scale == 1 or scale == 0:  # более красивое отображение
            coords = coords.split(',')
            coords[-1] = '0'
            coords = ','.join(coords)

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={coords}&z={scale}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            quit()

        # Запишем полученное изображение в файл.
        self.map_file = f"map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove('map.png')


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = Example()
    ex.show()
    sys.exit(app.exec())
