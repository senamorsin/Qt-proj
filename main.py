from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QPushButton, QComboBox, QLineEdit,
                             QInputDialog, QMessageBox, QTableView,
                             QPlainTextEdit, QLabel, QMenuBar)
from PyQt6.QtGui import QPixmap
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6 import uic
from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtCore import Qt
import sys
import datetime
import sqlite3


def correct_phone_format(s):
    if not s:
        return False
    if s[0] == '8':
        return len(s) == 11
    elif s[:2] == '+7':
        return len(s) == 12


def correct_date_format(s):
    try:
        datetime.datetime.strptime(s, '%d.%m.%Y %H:%M')
    except Exception:
        return False
    return True


def timetables_intersect(t1, t2):
    form = '%d.%m.%Y %H:%M'

    t1_start, t1_end = t1.split(' -- ')
    t2_start, t2_end = t2.split(' -- ')

    t1_start = datetime.datetime.strptime(t1_start, form)
    t1_end = datetime.datetime.strptime(t1_end, form)
    t2_start = datetime.datetime.strptime(t2_start, form)
    t2_end = datetime.datetime.strptime(t2_end, form)

    c1 = t2_start <= t1_start <= t2_end
    c2 = t2_start <= t1_end <= t2_end
    c3 = t1_start <= t2_start <= t1_end
    c4 = t1_start <= t2_end <= t1_end

    return c1 or c2 or c3 or c4


class Cinema:
    def __init__(self, name: str, address: str, phone: str, more=''):
        self._name = name
        self._address = address
        self._phone = phone
        self._more = more

    def get_name(self):
        return self._name

    def get_address(self):
        return self._address

    def get_phone(self):
        return self._phone

    def get_more(self):
        return self._more


class Room:
    def __init__(self, n_rows: int, n_cols: int, cinema_id: int):
        self._n_rows = n_rows
        self._n_cols = n_cols
        self._cinema_id = cinema_id
        self._booked_seats = list().copy()

    def get_n_rows(self):
        return self._n_rows

    def get_n_cols(self):
        return self._n_cols

    def get_booked_seats(self):
        return self._booked_seats

    def get_cinema_id(self):
        return self._cinema_id


class Film:
    def __init__(self, name: str, duration: int, price: int, info: str):
        self._name = name
        self._duration = duration
        self._price = price
        self._info = info

    def get_name(self):
        return self._name

    def get_duration(self):
        return self._duration

    def get_price(self):
        return self._price

    def get_info(self):
        return self._info


class Session:
    def __init__(self, cinema_address, room_n, film_name, timetable):
        self._cinema_address = cinema_address
        self._room_n = room_n
        self._film_name = film_name
        self._timetable = timetable

    def get_cinema_address(self):
        return self._cinema_address

    def get_room_n(self):
        return self._room_n

    def get_film_name(self):
        return self._film_name

    def get_timetable(self):
        return self._timetable


class Booking:
    def __init__(self, s_id, f_n, c_n, date, row_n, col_n, b_p, b_c):
        self._session_id = s_id
        self._film_name = f_n
        self._cinema_name = c_n
        self._date = date
        self._row_number = row_n
        self._column_number = col_n
        self._booking_price = b_p
        self._booking_contact = b_c

    def get_session_id(self):
        return self._session_id

    def get_film_name(self):
        return self._film_name

    def get_cinema_name(self):
        return self._cinema_name

    def get_date(self):
        return self._date

    def get_row_number(self):
        return self._row_number

    def get_column_number(self):
        return self._column_number

    def get_booking_price(self):
        return self._booking_price

    def get_booking_contact(self):
        return self._booking_contact


class ShowSeats(QMainWindow):
    def __init__(self, address, room_n):
        super().__init__()
        self.text = QPlainTextEdit(self)
        self.setCentralWidget(self.text)
        self.resize(1250, 600)
        self.setWindowTitle(f'Зал № {room_n}')

        self.set_text(address, room_n)

    def set_text(self, address, room_n):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = '''SELECT RoomRows, RoomColumns FROM Rooms
                WHERE RoomNumber = ? AND CinemaId in (
                SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?)'''

        data = cur.execute(query, (room_n, address)).fetchall()

        text = []
        p = '  '.join(['[■]'] * data[0][1])

        for _ in range(data[0][0]):
            text.append(p)

        self.text.setPlainText('\n'.join(text))
        self.text.show()


class ReadReviews(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Отзывы')
        self.setGeometry(800, 100, 700, 900)

        self.pixMap = QPixmap('image.jpg')
        self.lbl = QLabel(self)
        self.lbl.move(20, 10)
        self.lbl.resize(700, 900)
        self.lbl.setPixmap(self.pixMap)

        self.text = QPlainTextEdit(self)
        self.text.move(0, 720)
        self.text.resize(700, 170)

        with open('reviews.txt', mode='r', encoding='utf-8') as f:
            self.text.setPlainText(f.read())
        self.text.setEnabled(False)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 1200, 800)
        uic.loadUi('MainMenu.ui', self)

        self.setWindowTitle('КИНОТЕАТРЫ 2.0')

        self.status_bar = self.statusBar()

        self.cinemas_widget = QWidget(self)
        self.tabWidget.addTab(self.cinemas_widget, 'Кинотеатры')

        self.cinemas_view = QTableView(self.cinemas_widget)
        self.cinemas_view.move(10, 70)
        self.cinemas_view.resize(1150, 620)

        self.add_cinema_btn = QPushButton(
            'Добавить кинотеатр', self.cinemas_widget)
        self.add_cinema_btn.clicked.connect(self.create_cinema)
        self.add_cinema_btn.move(10, 10)
        self.add_cinema_btn.resize(180, 40)

        self.delete_cinema_btn = QPushButton(
            'Удалить кинотеатр', self.cinemas_widget)
        self.delete_cinema_btn.clicked.connect(self.delete_cinema)
        self.delete_cinema_btn.move(200, 10)
        self.delete_cinema_btn.resize(180, 40)

        self.edit_cinema_btn = QPushButton(
            'Редактировать информацию о кинотеатре',
            self.cinemas_widget)
        self.edit_cinema_btn.clicked.connect(self.edit_cinema)
        self.edit_cinema_btn.move(390, 10)
        self.edit_cinema_btn.resize(300, 40)

        self.rooms_widget = QWidget(self)
        self.tabWidget.addTab(self.rooms_widget, 'Кинозалы')

        self.rooms_view = QTableView(self.rooms_widget)
        self.rooms_view.move(10, 70)
        self.rooms_view.resize(1150, 620)

        self.add_room_btn = QPushButton('Добавить кинозал', self.rooms_widget)
        self.add_room_btn.clicked.connect(self.create_room)
        self.add_room_btn.move(10, 10)
        self.add_room_btn.resize(180, 40)

        self.delete_room_btn = QPushButton(
            'Удалить кинозал', self.rooms_widget)
        self.delete_room_btn.clicked.connect(self.delete_room)
        self.delete_room_btn.move(200, 10)
        self.delete_room_btn.resize(180, 40)

        self.edit_room_btn = QPushButton(
            'Редактировать информацию о кинозале',
            self.rooms_widget)
        self.edit_room_btn.clicked.connect(self.edit_room)
        self.edit_room_btn.move(390, 10)
        self.edit_room_btn.resize(300, 40)

        self.rooms_info_btn = QPushButton(
            'Информация о сиденьях', self.rooms_widget)
        self.rooms_info_btn.clicked.connect(self.show_seats)
        self.rooms_info_btn.move(700, 10)
        self.rooms_info_btn.resize(200, 40)

        self.films_widget = QWidget(self)
        self.tabWidget.addTab(self.films_widget, 'Фильмы')

        self.films_view = QTableView(self.films_widget)
        self.films_view.move(10, 70)
        self.films_view.resize(1150, 620)

        self.add_film_btn = QPushButton('Добавить фильм', self.films_widget)
        self.add_film_btn.clicked.connect(self.create_film)
        self.add_film_btn.move(10, 10)
        self.add_film_btn.resize(180, 40)

        self.delete_film_btn = QPushButton('Удалить фильм', self.films_widget)
        self.delete_film_btn.clicked.connect(self.delete_film)
        self.delete_film_btn.move(200, 10)
        self.delete_film_btn.resize(180, 40)

        self.edit_film_btn = QPushButton(
            'Редактировать информацию о фильме',
            self.films_widget)
        self.edit_film_btn.clicked.connect(self.edit_film)
        self.edit_film_btn.move(390, 10)
        self.edit_film_btn.resize(300, 40)

        self.sessions_widget = QWidget(self)
        self.tabWidget.addTab(self.sessions_widget, 'Сеансы')
        self.sessions_view = QTableView(self.sessions_widget)
        self.sessions_view.move(10, 70)
        self.sessions_view.resize(1150, 620)

        self.add_session_btn = QPushButton(
            'Добавить сеанс', self.sessions_widget)
        self.add_session_btn.clicked.connect(self.create_session)
        self.add_session_btn.move(10, 10)
        self.add_session_btn.resize(180, 40)

        self.delete_session_btn = QPushButton(
            'Удалить сеанс', self.sessions_widget)
        self.delete_session_btn.clicked.connect(self.delete_session)
        self.delete_session_btn.move(200, 10)
        self.delete_session_btn.resize(180, 40)

        self.edit_session_btn = QPushButton(
            'Редактировать информацию о сеансе',
            self.sessions_widget)
        self.edit_session_btn.clicked.connect(self.edit_session)
        self.edit_session_btn.move(390, 10)
        self.edit_session_btn.resize(300, 40)

        self.bookings_widget = QWidget(self)
        self.tabWidget.addTab(self.bookings_widget, 'Брони')

        self.bookings_view = QTableView(self.bookings_widget)
        self.bookings_view.move(10, 70)
        self.bookings_view.resize(1150, 620)

        self.add_booking_btn = QPushButton(
            'Добавить бронь', self.bookings_widget)
        self.add_booking_btn.clicked.connect(self.create_booking)
        self.add_booking_btn.move(10, 10)
        self.add_booking_btn.resize(180, 40)

        self.delete_booking_btn = QPushButton(
            'Удалить бронь', self.bookings_widget)
        self.delete_booking_btn.clicked.connect(self.delete_booking)
        self.delete_booking_btn.move(200, 10)
        self.delete_booking_btn.resize(180, 40)

        self.lbl = QLabel(self.bookings_widget)
        self.lbl.setText('Поиcк:')
        self.lbl.move(550, 10)
        self.lbl.resize(200, 40)

        self.proxy = QSortFilterProxyModel(self.bookings_widget)

        self.filter_edit = QLineEdit(self.bookings_widget)
        self.filter_edit.move(600, 10)
        self.filter_edit.resize(250, 40)
        self.filter_edit.textChanged.connect(self.proxy.setFilterFixedString)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.resize(1200, 25)
        self.settings_menu = self.menu_bar.addMenu('Настройки')

        self.clear_db_action = self.settings_menu.addAction(
            'Очистить базу данных')
        self.see_reviews_action = self.settings_menu.addAction(
            'Смотреть отзывы')

        self.clear_db_action.triggered.connect(self.clear_database)
        self.see_reviews_action.triggered.connect(self.read_reviews)

        self.schedule_widget = QWidget(self)
        self.tabWidget.addTab(self.schedule_widget, 'Афиша')

        self.lbl_1 = QLabel(self.schedule_widget)
        self.lbl_1.setText('Поиск ближайших сеансов по:')
        self.lbl_1.resize(180, 40)
        self.lbl_1.move(10, 10)

        self.search_by = QComboBox(self.schedule_widget)
        self.search_by.resize(180, 40)
        self.search_by.move(210, 10)
        self.search_by.addItem('Дате (dd.mm.yyyy)')
        self.search_by.addItem('Кинотеатру (адрес)')
        self.search_by.addItem('Фильму')
        self.search_by.currentTextChanged.connect(self.status_bar.clearMessage)

        self.schedule_filter = QLineEdit(self.schedule_widget)
        self.schedule_filter.resize(240, 40)
        self.schedule_filter.move(400, 10)

        self.search_btn = QPushButton('Искать', self.schedule_widget)
        self.search_btn.resize(140, 40)
        self.search_btn.move(650, 10)
        self.search_btn.clicked.connect(self.search_sessions)

        self.search_result_1 = QLabel('- - - - - - - -', self.schedule_widget)
        self.search_result_1.resize(1000, 40)
        self.search_result_1.move(10, 150)

        self.search_result_2 = QLabel('- - - - - - - -', self.schedule_widget)
        self.search_result_2.resize(1000, 40)
        self.search_result_2.move(10, 250)

        self.search_result_3 = QLabel('- - - - - - - -', self.schedule_widget)
        self.search_result_3.resize(1000, 40)
        self.search_result_3.move(10, 350)

        self.init_all_tables()

    def clear_database(self):
        ok = QMessageBox(self).question(
            self,
            'Очистка базы данных',
            'Вы уверены, что хотите удалить все данные из базы данных?')
        if ok == QMessageBox.StandardButton.Yes:
            con = sqlite3.connect('Cinemas_db.sqlite')
            cur = con.cursor()

            cur.execute('DELETE FROM Cinemas')
            cur.execute('DELETE FROM Rooms')
            cur.execute('DELETE FROM Films')
            cur.execute('DELETE FROM Sessions')
            cur.execute('DELETE FROM Bookings')

            con.commit()
            con.close()

            self.update_all_tables()

            self.search_result_1.setText('- - - - - - - -')
            self.search_result_2.setText('- - - - - - - -')
            self.search_result_3.setText('- - - - - - - -')
            self.status_bar.clearMessage()

    def read_reviews(self):
        try:
            self.second_form = ReadReviews()
            self.second_form.show()
            return
        except Exception:
            QMessageBox(self).information(
                self, 'Нет отзывов', 'Пока нет отзывов(')
            return

    def init_all_tables(self):
        self.init_cinema_table()
        self.init_rooms_table()
        self.init_films_table()
        self.init_sessions_table()
        self.init_bookings_table()

    def init_cinema_table(self):
        header = self.cinemas_view.horizontalHeader()
        header.setStretchLastSection(True)

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """CREATE TABLE IF NOT EXISTS Cinemas (
                CinemaId      INTEGER PRIMARY KEY,
                CinemaName    TEXT,
                CinemaAddress TEXT,
                CinemaPhone   TEXT,
                CinemaInfo    TEXT)"""

        cur.execute(query)
        con.commit()
        con.close()

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Cinemas')
        model.select()

        db.close()
        self.cinemas_view.setModel(model)

    def init_rooms_table(self):
        header = self.rooms_view.horizontalHeader()
        header.setStretchLastSection(True)

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """CREATE TABLE IF NOT EXISTS Rooms (
                RoomId        INTEGER PRIMARY KEY,
                CinemaId      INTEGER,
                RoomNumber    INTEGER,
                RoomColumns   INTEGER,
                RoomRows      INTEGER)"""

        cur.execute(query)
        con.commit()
        con.close()

        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Rooms')
        model.select()

        db.close()
        self.rooms_view.setModel(model)

    def init_films_table(self):
        header = self.films_view.horizontalHeader()
        header.setStretchLastSection(True)

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """CREATE TABLE IF NOT EXISTS Films (
                FilmId            INTEGER PRIMARY KEY,
                FilmName          TEXT,
                FilmDuration      INTEGER,
                FilmPrice         INTEGER,
                FilmInfo          TEXT)"""

        cur.execute(query)
        con.commit()
        con.close()

        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Films')
        model.select()

        db.close()
        self.films_view.setModel(model)

    def init_sessions_table(self):
        header = self.sessions_view.horizontalHeader()
        header.setStretchLastSection(True)

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """CREATE TABLE IF NOT EXISTS Sessions (
                SessionId         INTEGER PRIMARY KEY,
                CinemaAddress     TEXT,
                RoomNumber        INTEGER,
                TimeTable         TEXT,
                FilmName          TEXT)"""

        cur.execute(query)
        con.commit()
        con.close()

        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Sessions')
        model.select()

        db.close()
        self.sessions_view.setModel(model)

    def init_bookings_table(self):
        header = self.bookings_view.horizontalHeader()
        header.setStretchLastSection(True)

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """CREATE TABLE IF NOT EXISTS Bookings (
                BookingId         INTEGER PRIMARY KEY,
                SessionId         INTEGER,
                FilmName          TEXT,
                CinemaName        TEXT,
                Date              TEXT,
                RowNumber         INTEGER,
                ColumnNumber      INTEGER,
                BookingPrice      INTEGER,
                BookingContact    TEXT)"""

        cur.execute(query)
        con.commit()
        con.close()

        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Bookings')
        model.select()

        db.close()

        self.proxy.setSourceModel(model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.bookings_view.setModel(self.proxy)
        self.bookings_view.setSortingEnabled(True)
        self.bookings_view.setModel(self.proxy)

    def update_cinema_table(self):
        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Cinemas')
        model.select()

        self.cinemas_view.setModel(model)
        db.close()

    def update_rooms_table(self):
        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Rooms')
        model.select()

        self.rooms_view.setModel(model)
        db.close()

    def update_film_table(self):
        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Films')
        model.select()

        self.films_view.setModel(model)
        db.close()

    def update_session_table(self):
        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Sessions')
        model.select()

        self.sessions_view.setModel(model)
        db.close()

    def update_booking_table(self):
        db = QSqlDatabase.database('QSQLITE')
        db.setDatabaseName('Cinemas_db.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('Bookings')
        model.select()

        db.close()

        self.proxy.setSourceModel(model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.bookings_view.setModel(self.proxy)
        self.bookings_view.setSortingEnabled(True)
        self.bookings_view.setModel(self.proxy)

        self.bookings_view.setModel(self.proxy)

    def update_all_tables(self):
        self.update_cinema_table()
        self.update_rooms_table()
        self.update_film_table()
        self.update_session_table()
        self.update_booking_table()

    def show_seats(self):
        address, ok = QInputDialog(self).getText(
            self, 'Просмотр сидений',
            'Введите адрес кинотеатра, где расположен интересующий вас зал')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Просмотр сидений',
            'Введите номер интересующего вас зала', 1, 1)

        if not ok:
            con.close()
            return

        query = '''SELECT RoomNumber FROM Rooms
                WHERE CinemaId in (
                SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?)'''

        if room_n not in [i[0]
                          for i in cur.execute(query, (address,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'В кинотеатре нет кинозала с таким номером')
            con.close()
            return

        self.second_form = ShowSeats(address, room_n)
        self.second_form.show()

    def create_cinema(self):
        name, ok_name = QInputDialog(self).getText(
            self, 'Новый кинотеатр', 'Введите название кинотеатра')

        if not ok_name:
            return

        while not name:
            if not ok_name:
                return
            QMessageBox.critical(
                self, 'Ошибка', 'Имя кинотеатра должно быть введено')
            name, ok_name = QInputDialog(self).getText(
                self, 'Новый кинотеатр', 'Введите название кинотеатра')

        address, ok_address = QInputDialog(self).getText(
            self, 'Новый кинотеатр', 'Введите адрес кинотеатра')

        if not ok_address:
            return

        while not address:
            if not ok_address:
                return
            QMessageBox.critical(
                self, 'Ошибка', 'Адрес кинотеатра должен быть введен')
            address, ok_address = QInputDialog(self).getText(
                self, 'Новый кинотеатр', 'Введите адрес кинотеатра')

        phone, ok_phone = QInputDialog(self).getText(
            self, 'Новый кинотеатр', 'Введите контактный номер кинотеатра')

        if not ok_phone:
            return

        while not correct_phone_format(phone):
            if not ok_phone:
                return
            QMessageBox.critical(
                self, 'Ошибка', 'Неправильный формат номера телефона')
            phone, ok_phone = QInputDialog(self).getText(
                self, 'Новый кинотеатр',
                'Введите контактный номер кинотеатра')

        more, ok = QInputDialog(self).getText(
            self, 'Новый кинотеатр',
            'Введите дополнительную информацию (опиционально)')
        if ok:
            cinema = Cinema(name, address, phone, more)
            self.add_cinema(cinema)

    def add_cinema(self, cinema: Cinema):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        if cinema.get_address() in [i[0] for i in cur.execute(
                "SELECT CinemaAddress FROM Cinemas").fetchall()]:
            QMessageBox.critical(
                self, 'Ошибка', 'Кинотеатр с таким адресом уже существует')
            con.close()
            return

        query = """INSERT INTO Cinemas
                (CinemaName, CinemaAddress, CinemaPhone, CinemaInfo)
                VALUES (?, ?, ?, ?)"""

        cur.execute(
            query,
            (cinema.get_name(),
             cinema.get_address(),
             cinema.get_phone(),
             cinema.get_more()))

        con.commit()
        con.close()

        self.update_cinema_table()

    def delete_cinema(self):
        address, ok = QInputDialog(self).getText(
            self, 'Удаление кинотеатра',
            'Введите адрес удаляемого кинотеатра')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Нет кинотеатра с таким адресом')
            con.close()
            return

        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'
        cinema_id = cur.execute(query, (address,)).fetchone()[0]

        query = 'DELETE FROM Rooms WHERE CinemaId = ?'
        cur.execute(query, (cinema_id,))

        query = 'DELETE FROM Sessions WHERE CinemaAddress = ?'
        cur.execute(query, (address,))

        query = 'DELETE FROM Cinemas WHERE CinemaAddress = ?'
        cur.execute(query, (address,))

        con.commit()
        con.close()

        self.update_cinema_table()
        self.update_rooms_table()
        self.update_session_table()

    def edit_cinema(self):
        address, ok = QInputDialog(self).getText(
            self, 'Редактирование информации',
            'Введите адрес изменяемого кинотеатра')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Нет кинотеатра с таким адресом')
            con.close()
            return

        edit, ok = QInputDialog(self).getItem(
            self, 'Редактирование информации',
            'Выберите, что хотите изменить', [
                'Имя', 'Адрес', 'Телефон', 'Дополнительная информация'])

        if not ok:
            con.close()
            return

        if edit == 'Имя':
            name, ok = QInputDialog(self).getText(
                self, 'Изменение имени', 'Введите новое имя')

            if not ok:
                con.close()
                return

            query = '''UPDATE Cinemas SET CinemaName = ?
                    WHERE CinemaAddress = ?'''
            cur.execute(query, (name, address))

            con.commit()
            con.close()

        elif edit == 'Адрес':
            new_address, ok = QInputDialog(self).getText(
                self, 'Редактирование информаци', 'Введите новый адрес')

            if not ok:
                con.close()
                return

            query = 'SELECT CinemaAddress FROM Cinemas'

            if new_address in [i[0] for i in cur.execute(query).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка',
                    'По такому адресу уже существует кинотеатр')
                return

            query = '''UPDATE Cinemas SET CinemaAddress = ?
                    WHERE CinemaAddress = ?'''
            cur.execute(query, (new_address, address))

            con.commit()
            con.close()

        elif edit == 'Телефон':
            phone, ok = QInputDialog(self).getText(
                self, 'Редактирование информаци', 'Введите новый телефон')

            if not ok:
                con.close()
                return

            if not correct_phone_format(phone):
                QMessageBox(self).critical(
                    self, 'Ошибка', 'Неправильный формат телефона')
                return

            query = '''UPDATE Cinemas SET CinemaPhone = ?
                    WHERE CinemaAddress = ?'''
            cur.execute(query, (phone, address))

            con.commit()
            con.close()

        elif edit == 'Дополнительная информация':
            more, ok = QInputDialog(self).getText(
                self, 'Редактирование информации',
                'Введите дополнительную информацию')

            if not ok:
                con.close()
                return

            query = '''UPDATE Cinemas SET CinemaInfo = ?
                    WHERE CinemaAddress = ?'''
            cur.execute(query, (more, address))

            con.commit()
            con.close()

        else:
            QMessageBox(self).critical(self, 'Ошибка', 'Неизвестный признак')
            con.close()
            return

        self.update_cinema_table()

    def create_room(self):
        address, ok = QInputDialog(self).getText(
            self, 'Новый кинозал',
            'Введите адрес кинотеатра, куда добавляете кинозал')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'

        cin_id = cur.execute(query, (address,)).fetchone()[0]

        con.close()

        n_rows, ok = QInputDialog(self).getInt(
            self, 'Новый кинозал',
            'Введите количество рядов сидений', 10, 1, 30)

        if not ok:
            return

        n_cols, ok = QInputDialog(self).getInt(
            self, 'Новый кинозал',
            'Введите количество сидений в одном ряду', 10, 1, 50)

        if not ok:
            return

        room = Room(n_rows, n_cols, cin_id)
        self.add_room(room)

    def add_room(self, room: Room):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT MAX(RoomNumber) FROM Rooms WHERE CinemaId = ?'

        max_room_n = cur.execute(query, (room.get_cinema_id(),)).fetchone()[0]
        if max_room_n is None:
            query = """INSERT INTO Rooms
                    (CinemaId, RoomNumber, RoomColumns, RoomRows)
                    VALUES (?, ?, ?, ?)"""

            cur.execute(
                query,
                (room.get_cinema_id(),
                 1,
                 room.get_n_cols(),
                 room.get_n_rows()))
        else:
            query = """INSERT INTO Rooms
                    (CinemaId, RoomNumber, RoomColumns, RoomRows)
                    VALUES (?, ?, ?, ?)"""

            cur.execute(
                query,
                (room.get_cinema_id(),
                 max_room_n + 1,
                 room.get_n_cols(),
                 room.get_n_rows()))

        con.commit()
        con.close()

        self.update_rooms_table()

    def delete_room(self):
        address, ok = QInputDialog(self).getText(
            self, 'Удаление кинозала',
            'Введите адрес кинотеатре, где хотите удалить кинозал')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Удаление кинозала', 'Введите номер удаляемого кинозала', 1)

        if not ok:
            con.close()
            return

        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'
        cinema_id = cur.execute(query, (address,)).fetchone()[0]

        query = 'SELECT RoomNumber FROM Rooms WHERE CinemaId = ?'

        if room_n not in [i[0]
                          for i in cur.execute(query,
                          (cinema_id,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'В кинотеатре нет кинозала с таким номером')
            con.close()
            return

        query = 'DELETE FROM Rooms WHERE RoomNumber = ? AND CinemaId = ?'

        cur.execute(query, (room_n, cinema_id))

        query = '''DELETE FROM Sessions
                WHERE CinemaAddress = ? AND RoomNumber = ?'''

        cur.execute(query, (address, room_n))

        con.commit()
        con.close()

        self.update_rooms_table()
        self.update_session_table()

    def edit_room(self):
        address, ok = QInputDialog(self).getText(
            self, 'Редактирование кинозала',
            'Введите адрес кинотеатре, где хотите отредактировать кинозал')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Редактирование кинозала',
            'Введите номер редактируемого кинозала', 1, 1)

        if not ok:
            con.close()
            return

        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'
        cinema_id = cur.execute(query, (address,)).fetchone()[0]

        query = 'SELECT RoomNumber FROM Rooms WHERE CinemaId = ?'

        if room_n not in [i[0]
                          for i in cur.execute(query,
                          (cinema_id,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'В кинотеатре нет кинозала с таким номером')
            con.close()
            return

        edit, ok = QInputDialog.getItem(self, 'Редактирование кинозала',
                                              'Выберите, что хотите изменить',
                                              ('Количество рядов',
                                               'Количество сидений в ряду'))
        if edit == 'Количество рядов':
            n_rows, ok = QInputDialog.getInt(
                    self, 'Редактирование кинозала',
                    'Введите новое количество рядов', 10, 1, 30)

            if not ok:
                con.close()
                return

            query = '''UPDATE Rooms SET RoomRows = ?
                    WHERE CinemaId = ? and RoomNumber = ?'''
            cur.execute(query, (n_rows, cinema_id, room_n))

        elif edit == 'Количество сидений в ряду':
            n_cols, ok = QInputDialog(self).getInt(
                self, 'Редактирование кинозала',
                'Введите новое количество сидений в ряду', 10, 1, 50)

            if not ok:
                con.close()
                return

            query = '''UPDATE Rooms SET RoomColumns = ?
                    WHERE CinemaId = ? and RoomNumber = ?'''
            cur.execute(query, (n_cols, cinema_id, room_n))

        else:
            QMessageBox(self).critical(self, 'Ошибка', 'Неизвестный признак')

        con.commit()
        con.close()

        self.update_rooms_table()

    def create_film(self):
        name, ok = QInputDialog(self).getText(
            self, 'Новый фильм', 'Введите название фильма')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT FilmName FROM Films'

        if name in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Фильм с таким названием уже существует')
            con.close()
            return

        con.close()

        duration, ok = QInputDialog(self).getInt(
            self, 'Новый фильм',
            'Введите длительность в минутах', 60, 10, 300)

        if not ok:
            return

        price, ok = QInputDialog(self).getInt(
            self, 'Новый фильм', 'Введите цену билета', 300, 0)

        if not ok:
            return

        info, ok = QInputDialog(self).getText(
            self, 'Новый фильм', 'Введите описание фильма')

        if not ok:
            return

        self.add_film(Film(name, duration, price, info))

    def add_film(self, film: Film):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """INSERT INTO Films
                (FilmName, FilmDuration, FilmPrice, FilmInfo)
                VALUES (?, ?, ?, ?)"""

        cur.execute(
            query,
            (film.get_name(),
             film.get_duration(),
             film.get_price(),
             film.get_info()))

        con.commit()
        con.close()

        self.update_film_table()

    def delete_film(self):
        name, ok = QInputDialog(self).getText(
            self, 'Удаление фильма',
            'Введите название фильма, который хотите удалить')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT FilmName FROM Films'

        if name not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Фильма с таким названием не существует')
            con.close()
            return

        query = 'DELETE FROM Sessions WHERE FilmName = ?'

        cur.execute(query, (name,))

        query = 'DELETE FROM Films WHERE FilmName = ?'

        cur.execute(query, (name,))

        con.commit()
        con.close()

        self.update_film_table()
        self.update_session_table()

    def edit_film(self):
        name, ok = QInputDialog(self).getText(
            self, 'Удаление фильма',
            'Введите название фильма, который хотите удалить')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT FilmName FROM Films'

        if name not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Фильма с таким названием не существует')
            con.close()
            return

        edit, ok = QInputDialog(self).getItem(self, 'Редактирование фильма',
                                              'Выберите, что хотите изменить',
                                              ('Название', 'Длительность',
                                               'Цена билета', 'Описание'))

        if not ok:
            con.close()
            return

        if edit == 'Название':
            new_name, ok = QInputDialog(self).getText(
                self, 'Редактирование фильма', 'Введите новое название')

            if not ok:
                con.close()
                return

            query = 'SELECT FilmName FROM Films'

            if new_name in [i[0] for i in cur.execute(query).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка', 'Фильм с таким названием уже существует')
                con.close()
                return

            query = 'UPDATE Films SET FilmName = ? WHERE FilmName = ?'

            cur.execute(query, (new_name, name))

        elif edit == 'Длительность':
            duration, ok = QInputDialog(self).getInt(
                self, 'Редактирование фильма',
                'Введите новую длительность', 60, 10, 300)

            if not ok:
                con.close()
                return

            query = 'UPDATE Films SET FilmDuration = ? WHERE FilmName = ?'

            cur.execute(query, (duration, name))

        elif edit == 'Цена билета':
            price, ok = QInputDialog(self).getInt(
                self, 'Редактирование фильма', 'Введите новую цену', 300, 0)

            if not ok:
                con.close()
                return

            query = 'UPDATE Films SET FilmPrice = ? WHERE FilmName = ?'

            cur.execute(query, (price, name))

        elif edit == 'Описание':
            info, ok = QInputDialog(self).getText(
                self, 'Редактирование фильма', 'Введите новое описание')

            if not ok:
                con.close()
                return

            query = 'UPDATE Films SET FilmInfo = ? WHERE FilmName = ?'

            cur.execute(query, (info, name))

        else:
            QMessageBox(self).critical(self, 'Ошибка', 'Неизвестный признак')
            con.close()
            return

        con.commit()
        con.close()

        self.update_film_table()

    def create_session(self):
        address, ok = QInputDialog(self).getText(
            self, 'Новый сеанс', 'Введите адрес кинотеатра, где будет сеанс')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Новый сеанс',
            'Введите номер кинозала, в котором будет проходить сеанс', 1)

        if not ok:
            con.close()
            return

        query = '''SELECT RoomNumber FROM Rooms
                WHERE CinemaId IN
                SELECT CinemaId FROM Cinemas
                WHERE CinemaAddress = ?)'''

        if room_n not in [i[0] for i in cur.execute(query, (address,))]:
            QMessageBox(self).critical(
                self, 'Ошибка',
                'В этом кинотеатре нет кинозала с таким номером')
            con.close()
            return

        film_name, ok = QInputDialog(self).getText(
            self, 'Новый сеанс', 'Введите название фильма')

        if not ok:
            con.close()
            return

        query = 'SELECT FilmName FROM Films'

        if film_name not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Нет фильма с таким названием')
            con.close()
            return

        date_start, ok = QInputDialog(self).getText(
            self, 'Новый сеанс',
            'Введите дату начала. Формат: dd.mm.yyyy hh:MM')

        if not ok:
            con.close()
            return

        if not correct_date_format(date_start):
            QMessageBox(self).critical(
                self, 'Ошибка', 'Неправильный формат даты')
            con.close()
            return

        query = 'SELECT FilmDuration FROM Films WHERE FilmName = ?'
        film_duration = datetime.timedelta(
            minutes=cur.execute(
                query, (film_name,)).fetchone()[0])

        form = '%d.%m.%Y %H:%M'

        timetable = date_start + ' -- ' + datetime.datetime.strftime(
            datetime.datetime.strptime(date_start,
                                       form) + film_duration, form)

        query = 'SELECT * FROM Sessions'

        for i in [j for j in cur.execute(query).fetchall()]:
            if address == i[1] and room_n == i[2]:
                if timetables_intersect(timetable, i[3]):
                    QMessageBox(self).critical(
                        self, 'Ошибка', 'Накладка времен сеансов')
                    con.close()
                    return

        con.close()

        self.add_session(Session(address, room_n, film_name, timetable))

    def add_session(self, session: Session):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = '''INSERT INTO Sessions (
                CinemaAddress, RoomNumber, FilmName, TimeTable)
                VALUES (?, ?, ?, ?)'''

        cur.execute(
            query,
            (session.get_cinema_address(),
             session.get_room_n(),
             session.get_film_name(),
             session.get_timetable()))

        con.commit()
        con.close()

        self.update_session_table()

    def delete_session(self):
        address, ok = QInputDialog(self).getText(
            self, 'Удаление сеанса',
            'Введите адрес кинотеатра, где проходит сеанс')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Sessions'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'В кинотеатре по такому адресу нет сеансов')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Удаление сеанса',
            'Введите номер кинозала, где проходит сеанс', 1, 1)

        if not ok:
            con.close()
            return

        query = 'SELECT RoomNumber FROM Sessions WHERE CinemaAddress = ?'

        if room_n not in [i[0]
                          for i in cur.execute(query, (address,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка',
                'В этом кинотеатре нет кинозала с таким номером')
            con.close()
            return

        timetable, ok = QInputDialog(self).getText(
            self, 'Удаление сеанса',
            'Введите расписание сеанса в таком формате,\
 в каком он показан в таблице')

        if not ok:
            con.close()
            return

        query = '''SELECT TimeTable FROM Sessions
                WHERE CinemaAddress = ? AND RoomNumber = ?'''

        if timetable not in [
            i[0] for i in cur.execute(
                query, (address, room_n))]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Такого сеанса не существует')
            con.close()
            return

        query = '''DELETE FROM Sessions
                WHERE CinemaAddress = ?
                AND RoomNumber = ? AND TimeTable = ?'''

        cur.execute(query, (address, room_n, timetable))

        con.commit()
        con.close()

        self.update_session_table()

    def edit_session(self):
        address, ok = QInputDialog(self).getText(
            self, 'Редактирование сеанса',
            'Введите адрес кинотеатра, где проходит сеанс')

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Sessions'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'В кинотеатре по такому адресу нет сеансов')
            con.close()
            return

        room_n, ok = QInputDialog(self).getInt(
            self, 'Редактирование сеанса',
            'Введите номер кинозала, где проходит сеанс', 1, 1)

        if not ok:
            con.close()
            return

        query = 'SELECT RoomNumber FROM Sessions WHERE CinemaAddress = ?'

        if room_n not in [i[0]
                          for i in cur.execute(query, (address,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка',
                'В этом кинотеатре нет кинозала с таким номером')
            con.close()
            return

        timetable, ok = QInputDialog(self).getText(
            self, 'Редактирование сеанса',
            'Введите расписание сеанса в таком формате,\
 в каком он показан в таблице')

        if not ok:
            con.close()
            return

        query = '''SELECT TimeTable FROM Sessions
                WHERE CinemaAddress = ? AND RoomNumber = ?'''

        if timetable not in [
            i[0] for i in cur.execute(
                query, (address, room_n))]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Такого сеанса не существует')
            con.close()
            return

        query = '''SELECT FilmName FROM Sessions
                WHERE CinemaAddress = ?
                AND RoomNumber = ? AND TimeTable = ?'''

        film_name = cur.execute(
            query, (address, room_n, timetable)).fetchone()[0]

        edit, ok = QInputDialog(self).getItem(self, 'Редактирование сеанса',
                                              'Выберите, что хотите изменить',
                                              ('Адрес кинотеатра',
                                               'Номер кинозала', 'Фильм',
                                               'Расписание'))

        if not ok:
            con.close()
            return

        if edit == 'Адрес кинотеатра':
            new_address, ok = QInputDialog(self).getText(
                self, 'Редактирование сеанса', 'Введите новый адрес')

            if not ok:
                con.close()
                return

            query = 'SELECT CinemaAddress FROM Cinemas'

            if new_address not in [i[0]
                                   for i in cur.execute(query).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка', 'По такому адресу нет кинотеатра')
                con.close()
                return

            query = '''SELECT RoomNumber FROM Rooms
                    WHERE CinemaId in (
                    SELECT CinemaId FROM Cinemas
                    WHERE CinemaAddress = ?)'''

            if room_n not in [
                i[0] for i in cur.execute(
                    query, (new_address,)).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка',
                    'В этом кинотеатре нет подходящего кинозала')
                con.close()
                return

            query = '''SELECT TimeTable FROM Sessions
                    WHERE CinemaAddress = ? AND RoomNumber = ?'''

            for i in cur.execute(query, (new_address, room_n)):
                if timetables_intersect(i[0], timetable):
                    QMessageBox(self).critical(
                        self, 'Ошибка',
                        'При таком изменении возникает\
 накладка времен сеансов')
                    con.close()
                    return

            query = '''UPDATE Sessions SET CinemaAddress = ?
                    WHERE CinemaAddress = ? AND RoomNumber = ?
                    AND TimeTable = ?'''

            cur.execute(
                query,
                (new_address,
                 address,
                 room_n,
                 timetable))

            con.commit()
            con.close()

            self.update_rooms_table()

        elif edit == 'Номер кинозала':
            new_room_n, ok = QInputDialog(self).getInt(
                self, 'Редактирование сеанса',
                'Введите новый номер зала, где будет сеанс', 1, 1)

            if not ok:
                con.close()
                return

            query = '''SELECT RoomNumber FROM Rooms
                    WHERE CinemaId in (
                    SELECT CinemaId FROM Cinemas
                    WHERE CinemaAddress = ?)'''

            if new_room_n not in [
                i[0] for i in cur.execute(
                    query, (address,)).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка',
                    'В этом кинотеатре нет кинозала с таким номером')
                con.close()
                return

            query = '''SELECT TimeTable FROM Sessions
                    WHERE CinemaAddress = ?
                    AND RoomNumber = ?'''

            for i in cur.execute(query, (address, new_room_n)):
                if timetables_intersect(i[0], timetable):
                    QMessageBox(self).critical(
                        self, 'Ошибка',
                        'При таком изменении возникает\
 накладка времен сеансов')
                    con.close()
                    return

            query = '''UPDATE Sessions SET RoomNumber = ?
                    WHERE CinemaAddress = ?
                    AND RoomNumber = ? AND TimeTable = ?'''

            cur.execute(
                query,
                (new_room_n,
                 address,
                 room_n,
                 timetable))

            con.commit()
            con.close()

            self.update_session_table()

        elif edit == 'Фильм':
            new_film_name, ok = QInputDialog(self).getText(
                self, 'Редактирование сеанса',
                'Введите новое название фильма')

            if not ok:
                con.close()
                return

            query = 'SELECT FilmName FROM Films'

            if new_film_name not in [i[0]
                                     for i in cur.execute(query).fetchall()]:
                QMessageBox(self).critical(
                    self, 'Ошибка', 'Такого фильма не существует')
                con.close()
                return

            query = 'SELECT FilmDuration FROM Films WHERE FilmName = ?'

            new_film_duration = datetime.timedelta(
                minutes=cur.execute(query, (new_film_name,)).fetchone()[0])

            form = '%d.%m.%Y %H:%M'

            date_start = timetable.split(' -- ')[0]
            new_timetable = date_start + ' -- ' + datetime.datetime.strftime(
                datetime.datetime.strptime(date_start,
                                           form) + new_film_duration, form)

            query = """SELECT TimeTable FROM Sessions
                    WHERE CinemaAddress = ? AND RoomNumber = ?
                    AND NOT (TimeTable = ?)"""

            for i in cur.execute(
                    query, (address, room_n, timetable)).fetchall():
                if timetables_intersect(i[0], new_timetable):
                    QMessageBox(self).critical(
                        self, 'Ошибка',
                        'При таком изменении возникает\
 накладка времен сеансов')
                    con.close()
                    return

            query = '''UPDATE Sessions SET TimeTable = ?
                    WHERE CinemaAddress = ?
                    AND RoomNumber = ?
                    AND TimeTable = ?'''

            cur.execute(query, (new_timetable, address, room_n, timetable))

            con.commit()
            con.close()

            self.update_session_table()

        elif edit == 'Расписание':
            new_start, ok = QInputDialog(self).getText(
                self, 'Редактирование сеанса',
                'Введите время начала в формате dd.mm.yyyy hh:mm')

            if not ok:
                con.close()
                return

            if not correct_date_format(new_start):
                QMessageBox(self).critical(
                    self, 'Ошибка', 'Некорректый формать времени')
                con.close()
                return

            query = 'SELECT FilmDuration FROM Films WHERE FilmName = ?'
            film_duration = datetime.timedelta(
                minutes=cur.execute(
                    query, (film_name,)).fetchone()[0])

            form = '%d.%m.%Y %H:%M'

            new_timetable = new_start + ' -- ' + datetime.datetime.strftime(
                datetime.datetime.strptime(new_start,
                                           form) + film_duration, form)

            query = """SELECT TimeTable FROM Sessions
                    WHERE CinemaAddress = ? AND RoomNumber = ?
                    AND NOT (TimeTable = ?)"""

            for i in cur.execute(
                    query, (address, room_n, timetable)).fetchall():
                if timetables_intersect(i[0], new_timetable):
                    QMessageBox(self).critical(
                        self, 'Ошибка',
                        'При таком изменении возникает\
 накладка времен сеансов')
                    con.close()
                    return

            query = '''UPDATE Sessions SET TimeTable = ?
                    WHERE CinemaAddress = ?
                    AND RoomNumber = ? AND TimeTable = ?'''

            cur.execute(query, (new_timetable, address, room_n, timetable))

            con.commit()
            con.close()

            self.update_session_table()

        else:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Такого признака не существует')
            con.close()
            return

    def create_booking(self):
        session_id, ok = QInputDialog(self).getInt(
            self, 'Новая бронь',
            'Введите идентификатор сеанса,\
 место на котором хотите забронировать', 1, 1)

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT SessionId FROM Sessions'

        if session_id not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка',
                'Сеанса с таким идентификатором не существует')
            con.close()
            return

        query = """SELECT RoomRows FROM Rooms
                WHERE CinemaId in (
                SELECT CinemaId FROM Cinemas
                WHERE CinemaAddress in (
                SELECT CinemaAddress FROM Sessions
                WHERE SessionId = ?))"""

        max_row = cur.execute(query, (session_id,)).fetchone()[0]

        row_n, ok = QInputDialog(self).getInt(
            self, 'Новая бронь',
            'Введите номер ряда,\
 сиденье на котором бронируете', 1, 1, max_row)

        if not ok:
            con.close()
            return

        query = """SELECT RoomColumns FROM Rooms
                WHERE CinemaId in (
                SELECT CinemaId FROM Cinemas
                WHERE CinemaAddress in (
                SELECT CinemaAddress FROM Sessions
                WHERE SessionId = ?))"""

        max_col = cur.execute(query, (session_id,)).fetchone()[0]

        col_n, ok = QInputDialog(self).getInt(
            self, 'Новая бронь',
            'Введите номер сиденья, которое бронируете', 1, 1, max_col)

        if not ok:
            con.close()
            return

        query = '''SELECT RowNumber, ColumnNumber FROM Bookings
                WHERE SessionId = ?'''

        if (row_n, col_n) in [i for i in cur.execute(
                query, (session_id,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Это сиденье уже занято')
            con.close()
            return

        booking_contact, ok = QInputDialog(self).getText(
            self, 'Новая бронь',
            'Введите контактные данные (в любом формате)')

        if not ok:
            con.close()
            return

        query = """SELECT FilmName FROM Sessions
                WHERE SessionId = ?"""

        film_name = cur.execute(query, (session_id,)).fetchone()[0]

        query = """SELECT CinemaName FROM Cinemas
                WHERE CinemaAddress in (
                SELECT CinemaAddress FROM Sessions
                WHERE SessionId = ?)"""

        cinema_name = cur.execute(query, (session_id,)).fetchone()[0]

        query = """SELECT TimeTable FROM Sessions
                WHERE SessionId = ?"""

        date = cur.execute(query, (session_id,)).fetchone()[0].split()[0]

        query = """SELECT FilmPrice FROM Films
                WHERE FilmName = ?"""

        film_price = cur.execute(query, (film_name,)).fetchone()[0]

        con.close()

        self.add_booking(
            Booking(
                session_id,
                film_name,
                cinema_name,
                date,
                row_n,
                col_n,
                film_price,
                booking_contact))

    def add_booking(self, bk: Booking):
        s_id = bk.get_session_id()
        f_n = bk.get_film_name()
        c_n = bk.get_cinema_name()
        date = bk.get_date()
        row_n = bk.get_row_number()
        col_n = bk.get_column_number()
        b_p = bk.get_booking_price()
        b_c = bk.get_booking_contact()

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = """INSERT INTO Bookings
                (SessionId, FilmName, CinemaName, Date,
                RowNumber, ColumnNumber, BookingPrice,
                BookingContact) VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)"""

        cur.execute(query, (s_id, f_n, c_n, date, row_n, col_n, b_p, b_c))

        con.commit()
        con.close()

        self.update_booking_table()

    def delete_booking(self):
        session_id, ok = QInputDialog(self).getInt(
            self, 'Удаление брони',
            'Введите идентификатор сеанса,\
 на котором хотите отменить бронь', 1, 1)

        if not ok:
            return

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT SessionId FROM Sessions'

        if session_id not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка',
                'Сеанса с таким идентификатором не существует')
            con.close()
            return

        query = """SELECT RoomRows FROM Rooms
                WHERE CinemaId in (
                SELECT CinemaId FROM Cinemas
                WHERE CinemaAddress in (
                SELECT CinemaAddress FROM Sessions
                WHERE SessionId = ?))"""

        max_row = cur.execute(query, (session_id,)).fetchone()[0]

        row_n, ok = QInputDialog(self).getInt(
            self, 'Удаление брони',
            'Введите номер ряда,\
 на котором хотите отменить бронь', 1, 1, max_row)

        if not ok:
            con.close()
            return

        query = """SELECT RoomColumns FROM Rooms
                WHERE CinemaId in (
                SELECT CinemaId FROM Cinemas
                WHERE CinemaAddress in (
                SELECT CinemaAddress FROM Sessions
                WHERE SessionId = ?))"""

        max_col = cur.execute(query, (session_id,)).fetchone()[0]

        col_n, ok = QInputDialog(self).getInt(
            self, 'Удаление брони',
            'Введите номер сиденья,\
 бронь которого хотите отменить', 1, 1, max_col)

        if not ok:
            con.close()
            return

        query = '''SELECT RowNumber, ColumnNumber FROM Bookings
                WHERE SessionId = ?'''

        if (row_n, col_n) not in [i for i in cur.execute(
                query, (session_id,)).fetchall()]:
            QMessageBox(self).critical(
                self, 'Ошибка', 'Это сиденье не забронировано')
            con.close()
            return

        query = """DELETE FROM Bookings
                WHERE RowNumber = ?
                AND ColumnNumber = ?
                AND SessionId = ?"""

        cur.execute(query, (row_n, col_n, session_id))

        con.commit()
        con.close()

        self.update_booking_table()

    def search_sessions(self):
        self.status_bar.clearMessage()

        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        if self.search_by.currentText() == 'Дате (dd.mm.yyyy)':
            date = self.schedule_filter.text()

            if not correct_date_format(date.strip() + ' 00:00'):
                self.status_bar.showMessage('Неправильный формат даты')

                for i in [
                        self.search_result_1,
                        self.search_result_2,
                        self.search_result_3]:
                    i.setText('- - - - - - - -')

            else:
                form = '%d.%m.%Y %H:%M'

                sessions = cur.execute(
                    f'''SELECT * FROM Sessions
                    WHERE TimeTable LIKE "{date}%"''').fetchall()
                sessions.sort(
                    key=lambda x: abs(
                        datetime.datetime.now() -
                        datetime.datetime.strptime(
                            ' '.join(
                                x[3].split()[
                                    :2]),
                            form)))
                sessions = sessions[:3]

                labels = [
                    self.search_result_1,
                    self.search_result_2,
                    self.search_result_3]

                for i in range(3):
                    labels[i].setText('- - - - - - - -')
                    try:
                        cur = sessions[i]
                        text = '''Фильм {} показывается в кинотеатре по
                        адресу {} {} в кинозале {}'''.format(
                            cur[-1], cur[1], cur[3], cur[2])
                        labels[i].setText(text)
                    except Exception:
                        self.status_bar.showMessage(
                            'Не нашли и трех подходящих сеансов :(')
        elif self.search_by.currentText() == 'Кинотеатру (адрес)':
            cinema_address = self.schedule_filter.text()

            form = '%d.%m.%Y %H:%M'

            sessions = cur.execute(
                'SELECT * FROM Sessions WHERE CinemaAddress = ?',
                (cinema_address,
                 )).fetchall()
            sessions.sort(
                key=lambda x: abs(
                    datetime.datetime.now() -
                    datetime.datetime.strptime(
                        ' '.join(
                            x[3].split()[
                                :2]),
                        form)))
            sessions = sessions[:3]

            labels = [
                self.search_result_1,
                self.search_result_2,
                self.search_result_3]

            for i in range(3):
                labels[i].setText('- - - - - - - -')
                try:
                    cur = sessions[i]
                    text = '''Фильм {} показывается в кинотеатре по адресу
                    {} {} в кинозале {}'''.format(
                        cur[-1], cur[1], cur[3], cur[2])
                    labels[i].setText(text)
                except Exception:
                    self.status_bar.showMessage(
                        'Не нашли и трех подходящих сеансов :(')
        elif self.search_by.currentText() == 'Фильму':
            film_name = self.schedule_filter.text()

            form = '%d.%m.%Y %H:%M'

            sessions = cur.execute(
                'SELECT * FROM Sessions WHERE FilmName = ?',
                (film_name,)).fetchall()
            sessions.sort(
                key=lambda x: abs(
                    datetime.datetime.now() -
                    datetime.datetime.strptime(
                        ' '.join(
                            x[3].split()[
                                :2]),
                        form)))
            sessions = sessions[:3]

            labels = [
                self.search_result_1,
                self.search_result_2,
                self.search_result_3]

            for i in range(3):
                labels[i].setText('- - - - - - - -')
                try:
                    cur = sessions[i]
                    text = '''Фильм {} показывается в кинотеатре по
                    адресу {} {} в кинозале {}'''.format(
                        cur[-1], cur[1], cur[3], cur[2])
                    labels[i].setText(text)
                except Exception:
                    self.status_bar.showMessage(
                        'Не нашли и трех подходящих сеансов :(')
        con.close()

    def closeEvent(self, event):
        review, ok = QInputDialog(self).getMultiLineText(
            self, 'Отзыв', 'Пожалуйста, оставьте отзыв о работе программы!')

        if ok and review:
            with open('reviews.txt', mode='a', encoding='utf-8') as f:
                f.write(review.replace('\n', ' ') + '\n' * 2)


def main():
    app = QApplication(sys.argv)
    ex = MyWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
