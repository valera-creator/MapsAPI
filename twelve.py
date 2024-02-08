import math
import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox
from PyQt5.QtCore import Qt


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return round(distance)


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


def make_request_search(geocode, obj):
    link = 'https://search-maps.yandex.ru/v1/'
    params = {
        'lang': 'ru_RU',
        'apikey': 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
        'text': obj,
        'll': geocode,
        'results': 5

    }
    return requests.get(link, params=params)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.coords = "39.847061,57.576481"
        self.SCREEN_SIZE = [600, 530]
        self.pt = ''
        self.scale = 1
        self.cur_type_map = 'map'
        self.setGeometry(100, 100, *self.SCREEN_SIZE)
        self.setFixedSize(*self.SCREEN_SIZE)
        self.setWindowTitle('Задание 12')
        self.get_image(self.coords, self.scale)

        self.combobox = Combo(self)
        self.combobox.move(170, 465)
        self.combobox.resize(120, 20)
        self.combobox.addItems(('карта', 'спутник', 'гибрид'))

        self.btn_combobox = QPushButton('Сменить тип карты', self)
        self.btn_combobox.move(170, 485)
        self.btn_combobox.resize(120, 30)
        self.btn_combobox.clicked.connect(self.btn_combobox_click)

        self.search_lineedit = QLineEdit(self)
        self.search_lineedit.setPlaceholderText('Введите место поиска здесь')
        self.search_lineedit.move(300, 465)
        self.search_lineedit.resize(190, 25)

        self.btn_lineedit = QPushButton('Начать поиск', self)
        self.btn_lineedit.move(300, 490)
        self.btn_lineedit.resize(190, 25)
        self.btn_lineedit.clicked.connect(self.btn_lineedit_click)

        self.btn_reset = QPushButton('Сброс метки', self)
        self.btn_reset.move(500, 490)
        self.btn_reset.resize(90, 25)
        self.btn_reset.clicked.connect(self.btn_reset_click)

        self.btn_addresses = QPushButton('Вывод адреса', self)
        self.btn_addresses.move(500, 465)
        self.btn_addresses.resize(90, 25)
        self.btn_addresses.clicked.connect(self.btn_addresses_clicked)

        self.organization_lineedit = QLineEdit(self)
        self.organization_lineedit.move(10, 490)
        self.organization_lineedit.resize(150, 25)
        self.organization_lineedit.setPlaceholderText('Организация для поиска')

        self.response = self.get_response('39.847061,57.576481')

        # Изображение
        self.pixmap = QPixmap('map.png')
        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

        self.box_adresses = QCheckBox('почтовый индекс', self)
        self.box_adresses.move(10, 460)
        self.box_adresses.resize(130, 30)
        self.box_adresses.clicked.connect(self.postal_code)

        self.is_postal_code = False

    def get_response(self, geocode):
        seach_params = {
            'geocode': geocode,
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json'
        }

        link = 'https://geocode-maps.yandex.ru/1.x/'
        return requests.get(link, seach_params)

    def postal_code(self):
        self.is_postal_code = self.box_adresses.isChecked()
        data = self.response.json()

        try:
            coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            self.search_lineedit.setText(coords)
        except Exception:  # на случай если что-то произойдет с поиском
            return

        if self.is_postal_code:
            try:
                info = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['Address']['postal_code']
                self.search_lineedit.setText(f'{coords}, {info}')
            except Exception:  # если нет почтового индекса
                return

    def btn_lineedit_click(self):
        if not self.search_lineedit.text():
            return

        self.response = self.get_response(self.search_lineedit.text())
        check_response(self.response)
        data = self.response.json()

        try:
            coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        except Exception:  # на случай если что-то произойдет с поиском
            return
        coords = ','.join(coords)

        if self.scale < 8:
            self.scale = 8
        elif self.scale > 12:
            self.scale = 12

        self.pt = f'{coords},pm2lbm'
        self.get_image(coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))
        self.coords = coords

    def btn_addresses_clicked(self):
        data = self.response.json()
        try:
            coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            if self.is_postal_code:
                info = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['Address']['postal_code']
                coords += f", {info}"
            self.search_lineedit.setText(coords)
        except Exception:  # на случай если что-то произойдет с поиском
            return

    def btn_reset_click(self):
        self.pt = ''
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))

    def btn_combobox_click(self):
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
        if self.pt != '':
            search_params['pt'] = self.pt

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

        elif event.key() == Qt.Key_Left:
            cords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            cords[0] = str(float(cords[0]) - abs(step))
            if abs(float(cords[0])) >= 177:
                return
            self.coords = ','.join(cords)

        elif event.key() == Qt.Key_Right:
            cords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            cords[0] = str(float(cords[0]) + abs(step))
            if abs(float(cords[0])) >= 177:
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
        else:
            return

        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap('map.png'))

    def left_mouse_click(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if not (0 <= x <= 600 and 0 <= y <= 450):
            return
        if self.scale < 8:
            self.statusBar().showMessage(
                f'Использование меток при помощи мыши допустимо только при мастштабе от 8, '
                f'текущий масштаб: {self.scale}')
            return
        coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
        coords = self.coords.split(',')
        dy = 225 - y
        dx = x - 300

        lx = float(coords[0]) + dx * coord_to_geo_x * 2 ** (15 - self.scale)
        ly = float(coords[1]) + dy * coord_to_geo_y * math.cos(math.radians(float(coords[1]))) * 2 ** (
                15 - self.scale)
        if lx > 180:
            lx -= 360
        elif lx < -180:
            lx += 360

        self.pt = f"{lx},{ly},pm2lbm"
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))

        self.response = self.get_response(f'{lx},{ly}')
        check_response(self.response)
        self.postal_code()

    def right_mouse_click(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if not (0 <= x <= 600 and 0 <= y <= 450):
            return
        if self.scale < 8:
            self.statusBar().showMessage(
                f'Поиск организации при помощи мыши допустимо только при мастштабе от 8, '
                f'текущий масштаб: {self.scale}')
            return
        coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
        coords = self.coords.split(',')
        dy = 225 - y
        dx = x - 300

        lx = float(coords[0]) + dx * coord_to_geo_x * 2 ** (15 - self.scale)
        ly = float(coords[1]) + dy * coord_to_geo_y * math.cos(math.radians(float(coords[1]))) * 2 ** (
                15 - self.scale)
        if lx > 180:
            lx -= 360
        elif lx < -180:
            lx += 360
        coords_search = f'{lx},{ly}'
        if not self.organization_lineedit.text():
            self.statusBar().showMessage('Пустое поле организации')
            return
        response = make_request_search(coords_search, self.organization_lineedit.text())
        check_response(response)

        data = response.json()
        try:
            coords = list(map(float, data['features'][0]['geometry']['coordinates']))
        except Exception:  # если поиск не удался
            self.search_lineedit.setText('Ничего не найдено')

        s = lonlat_distance(list(map(float, coords_search.split(','))), coords)
        if s > 50:
            self.search_lineedit.setText('в расстоянии 50 метров ничего нет')
        else:
            self.search_lineedit.setText(f"адрес: {data['features'][0]['properties']['description']}")

    def mousePressEvent(self, event):
        self.statusBar().clearMessage()
        if event.button() == Qt.LeftButton:
            self.left_mouse_click(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_click(event)

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
