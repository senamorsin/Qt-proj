from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QPushButton, QComboBox, QLineEdit,
                             QInputDialog, QMessageBox, QTableWidgetItem,
                             QHeaderView, QTableView)
from PyQt6.QtGui import QImage
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6 import uic
import sys
import csv
import io
import datetime
import sqlite3

# autopep8 --in-place --aggressive --aggressive main.py


def correct_phone_format(s):
    if not s:
        return False
    if s[0] == '8':
        return len(s) == 11
    elif s[:2] == '+7':
        return len(s) == 12


class Cinema:
    def __init__(self, name: str, address: str, phone: str, more=''):
        self._name = name
        self._address = address
        self._phone = phone
        self._more = more

        self._rooms = list().copy()

    def info(self):
        return (f'Кинотеатр {self._name} расположен по адресу'
                f' {self._address}, контактный номер {self._phone}.'
                f' Дополнительно: {self._more}.')

    def add_room(self, room):
        self._rooms.append(room)

    def del_room(self, n):
        try:
            self._rooms.pop(n)
            return 0
        except IndexError:
            return 1

    def get_room(self, n):
        try:
            return self._rooms[n]
        except IndexError:
            return 1

    def amt_rooms(self):
        return len(self._rooms)

    def get_name(self):
        return self._name

    def get_address(self):
        return self._address

    def get_phone(self):
        return self._phone

    def get_more(self):
        return self._more

    def set_name(self, name):
        self._name = name

    def set_address(self, address):
        self._address = address

    def set_phone(self, phone):
        self._phone = phone

    def set_more(self, more):
        self._more = more


class Movie:
    def __init__(
            self,
            name: str,
            duration: datetime.timedelta,
            poster: QImage):
        self._name = name
        self._duration = duration
        self._poster = poster


class Room:
    def __init__(self, n_rows : int, n_cols : int, cinema_id : int):
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


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 1200, 800)
        uic.loadUi('MainMenu.ui', self)

        self.cinemas_widget = QWidget(self)
        self.tabWidget.addTab(self.cinemas_widget, 'Кинотеатры')

        self.cinemas_view = QTableView(self.cinemas_widget)
        self.cinemas_view.move(10, 70)
        self.cinemas_view.resize(1150, 620)

        self.add_cinema_btn = QPushButton('Добавить кинотеатр', self.cinemas_widget)
        self.add_cinema_btn.clicked.connect(self.create_cinema)
        self.add_cinema_btn.move(10, 10)
        self.add_cinema_btn.resize(180, 40)

        self.delete_cinema_btn = QPushButton('Удалить кинотеатр', self.cinemas_widget)
        self.delete_cinema_btn.clicked.connect(self.delete_cinema)
        self.delete_cinema_btn.move(200, 10)
        self.delete_cinema_btn.resize(180, 40)

        self.edit_cinema_btn = QPushButton('Редактировать информацию о кинотеатре', self.cinemas_widget)
        self.edit_cinema_btn.clicked.connect(self.edit_cinema)
        self.edit_cinema_btn.move(390, 10)
        self.edit_cinema_btn.resize(300, 40)

        self.rooms_widget = QWidget(self)
        self.tabWidget.addTab(self.rooms_widget, 'Кинозалы')

        self.rooms_view = QTableView(self.rooms_widget)
        self.rooms_view.move(10, 70)
        self.rooms_view.resize(1150, 620)

        self.add_room_btn = QPushButton('Добавить киноазл', self.rooms_widget)
        self.add_room_btn.clicked.connect(self.create_room)
        self.add_room_btn.move(10, 10)
        self.add_room_btn.resize(180, 40)

        self.delete_room_btn = QPushButton('Удалить киноазл', self.rooms_widget)
        self.delete_room_btn.clicked.connect(self.delete_room)
        self.delete_room_btn.move(200, 10)
        self.delete_room_btn.resize(180, 40)

        self.edit_room_btn = QPushButton('Редактировать информацию о киноазле', self.rooms_widget)
        self.edit_room_btn.clicked.connect(self.edit_room)
        self.edit_room_btn.move(390, 10)
        self.edit_room_btn.resize(300, 40)

        self.init_all_tables()

    def init_all_tables(self):
        self.init_cinema_table()
        self.init_rooms_table()

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
                self, 'Новый кинотеатр', 'Введите контактный номер кинотеатра')

        more, ok = QInputDialog(self).getText(
            self, 'Новый кинотеатр', 'Введите дополнительную информацию (опиционально)')
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
            self, 'Удаление кинотеатра', 'Введите адрес удаляемого кинотеатра')

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

        query = 'DELETE FROM Cinemas WHERE CinemaAddress = ?'
        cur.execute(query, (address,))

        con.commit()
        con.close()

        self.update_cinema_table()
        self.update_rooms_table()

    def edit_cinema(self):
        address, ok = QInputDialog(self).getText(
            self, 'Редактирование информации', 'Введите адрес изменяемого кинотеатра')

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
            self, 'Редактирование информации', 'Выберите, что хотите изменить', [
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

            query = 'UPDATE Cinemas SET CinemaName = ? WHERE CinemaAddress = ?'
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
                    self, 'Ошибка', 'По такому адресу уже существует кинотеатр')
                return

            query = 'UPDATE Cinemas SET CinemaAddress = ? WHERE CinemaAddress = ?'
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

            query = 'UPDATE Cinemas SET CinemaPhone = ? WHERE CinemaAddress = ?'
            cur.execute(query, (phone, address))

            con.commit()
            con.close()

        elif edit == 'Дополнительная информация':
            more, ok = QInputDialog(self).getText(
                self, 'Редактирование информации', 'Введите дополнительную информацию')

            if not ok:
                con.close()
                return

            query = 'UPDATE Cinemas SET CinemaInfo = ? WHERE CinemaAddress = ?'
            cur.execute(query, (more, address))

            con.commit()
            con.close()

        else:
            QMessageBox(self).critical(self, 'Ошибка', 'Неизвестный признак')
            con.close()
            return

        self.update_cinema_table()

    def create_room(self):
        address, ok = QInputDialog(self).getText(self, 'Новый кинозал', 'Введите адрес кинотеатра, куда добавляете кинозал')

        if not ok:
            return
        
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return

        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'

        cin_id = cur.execute(query, (address,)).fetchone()[0]
        
        con.close()

        n_rows, ok = QInputDialog(self).getInt(self, 'Новый кинозал', 'Введите количество рядов сидений', 10, 1, 30)

        if not ok:
            return
        
        n_cols, ok = QInputDialog(self).getInt(self, 'Новый кинозал', 'Введите количество сидений в одном ряду', 10, 1, 50)
        
        if not ok:
            return
        
        room = Room(n_rows, n_cols, cin_id)
        self.add_room(room)

    def add_room(self, room : Room):
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT MAX(RoomNumber) FROM Rooms WHERE CinemaId = ?'

        max_room_n = cur.execute(query, (room.get_cinema_id(),)).fetchone()[0]
        if max_room_n is None:
            query = """INSERT INTO Rooms
                    (CinemaId, RoomNumber, RoomColumns, RoomRows)
                    VALUES (?, ?, ?, ?)"""
                
            cur.execute(query, (room.get_cinema_id(), 1, room.get_n_cols(), room.get_n_rows()))
        else:
            query = """INSERT INTO Rooms
                    (CinemaId, RoomNumber, RoomColumns, RoomRows)
                    VALUES (?, ?, ?, ?)"""
                
            cur.execute(query, (room.get_cinema_id(), max_room_n + 1, room.get_n_cols(), room.get_n_rows()))
        
        con.commit()
        con.close()

        self.update_rooms_table()

    def delete_room(self):
        address, ok = QInputDialog(self).getText(self, 'Удаление кинозала', 'Введите адрес кинотеатре, где хотите удалить кинозал')

        if not ok:
            return
        
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return
        
        room_n, ok = QInputDialog(self).getInt(self, 'Удаление кинозала', 'Введите номер удаляемого кинозала')

        if not ok:
            con.close()
            return
        
        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'
        cinema_id = cur.execute(query, (address,)).fetchone()[0]

        query = 'SELECT RoomNumber FROM Rooms WHERE CinemaId = ?'

        if room_n not in [i[0] for i in cur.execute(query, (cinema_id,)).fetchall()]:
            QMessageBox(self).critical(self, 'Ошибка', 'В кинотеатре нет кинозала с таким номером')
            con.close()
            return
        
        query = 'DELETE FROM Rooms WHERE RoomNumber = ? AND CinemaId = ?'

        cur.execute(query, (room_n, cinema_id))

        con.commit()
        con.close()

        self.update_rooms_table()

    def edit_room(self):
        address, ok = QInputDialog(self).getText(self, 'Редактирование кинозала', 'Введите адрес кинотеатре, где хотите отредактировать кинозал')

        if not ok:
            return
        
        con = sqlite3.connect('Cinemas_db.sqlite')
        cur = con.cursor()

        query = 'SELECT CinemaAddress FROM Cinemas'

        if address not in [i[0] for i in cur.execute(query).fetchall()]:
            QMessageBox(self).critical(self, 'Ошибка', 'По такому адресу нет кинотеатра')
            con.close()
            return
        
        room_n, ok = QInputDialog(self).getInt(self, 'Редактирование кинозала', 'Введите номер редактируемого кинозала')

        if not ok:
            con.close()
            return
        
        query = 'SELECT CinemaId FROM Cinemas WHERE CinemaAddress = ?'
        cinema_id = cur.execute(query, (address,)).fetchone()[0]

        query = 'SELECT RoomNumber FROM Rooms WHERE CinemaId = ?'

        if room_n not in [i[0] for i in cur.execute(query, (cinema_id,)).fetchall()]:
            QMessageBox(self).critical(self, 'Ошибка', 'В кинотеатре нет кинозала с таким номером')
            con.close()
            return

        edit, ok = QInputDialog(self).getItem(self, 'Редактирование кинозала', 'Выберите, что хотите изменить', ('Количество рядов', 'Количество сидений в ряду'))
        if edit == 'Количество рядов':
            n_rows, ok = QInputDialog(self).getInt(self, 'Редактирование кинозала', 'Введите новое количество рядов', 10, 1, 30)

            if not ok:
                con.close()
                return
            
            query = 'UPDATE Rooms SET RoomRows = ? WHERE CinemaId = ? and RoomNumber = ?'
            cur.execute(query, (n_rows, cinema_id, room_n))
        
        elif edit == 'Количество сидений в ряду':
            n_cols, ok = QInputDialog(self).getInt(self, 'Редактирование кинозала', 'Введите новое количество сидений в ряду', 10, 1, 50)

            if not ok:
                con.close()
                return
            
            query = 'UPDATE Rooms SET RoomColumns = ? WHERE CinemaId = ? and RoomNumber = ?'
            cur.execute(query, (n_cols, cinema_id, room_n))
        
        else:
            QMessageBox(self).critical(self, 'Ошибка', 'Неизвестный признак')
        
        con.commit()
        con.close()

        self.update_rooms_table()


def main():
    app = QApplication(sys.argv)
    ex = MyWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
