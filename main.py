import sqlite3
import sys
from pickletools import read_decimalnl_short

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QLabel, QFileDialog, QScrollArea, \
    QVBoxLayout, QPushButton, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.search_button.clicked.connect(self.open_search_book)
        self.readed_button.clicked.connect(self.open_readed)

    def open_readed(self):
        self.readed = ReadedBooksWindow()
        self.readed.show()

    def open_search_book(self):
        self.search_book = SearchBookWindow()
        self.search_book.show()

    def closeEvent(self, a0):
        connect.close()


class BookWindow(QWidget):
    def __init__(self, book):
        super().__init__()
        self.book = book
        uic.loadUi('BookWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        try:
            self.setWindowTitle('Отбражение книги')
            self.title.setText(self.book.title())
            self.title.setWordWrap(True)
            self.cover_pixmap = QPixmap(self.book.cover())
            self.cover.setPixmap(self.cover_pixmap)
            self.cover.setScaledContents(True)
            self.authors.setText(self.book.authors())
            self.categories.setText(cursor.execute(f"""SELECT name FROM categories 
            WHERE id={self.book.category()}""").fetchone()[0])
            self.year.setText(str(self.book.year()))
            self.change_cover_button.clicked.connect(self.change_cover)
            self.rate_button.clicked.connect(self.rate)
        except Exception as e:
            self.statusBar().showMessage('Извините, возникла ошибка')

    def change_cover(self):
        self.new_cover = QFileDialog.getOpenFileName(self, 'Выбрать обложку', '')[0]
        self.cover_pixmap = QPixmap(self.new_cover)
        self.cover.setPixmap(self.cover_pixmap)
        self.book.info['cover'] = self.new_cover
        cursor.execute(f"""UPDATE books SET cover = '{self.new_cover}' WHERE id = {self.book.id()}""")
        connect.commit()

    def rate(self):
        self.number, self.ok = QInputDialog.getInt(
            self,
            "Оценка книги", "Введите вашу оценку (от 1 до 10)",
            value=1, min=1, max=10, step=1)
        print(self.ok)
        if self.ok:
            if cursor.execute(f"""SELECT * FROM ratings WHERE id = {self.book.id()}""").fetchone():
                cursor.execute(f"""UPDATE ratings SET rating = {self.number} WHERE id = {self.book.id()}""")
                connect.commit()
            else:
                cursor.execute(f"""INSERT INTO ratings(id, rating) VALUES({self.book.id()}, {self.number})""")
                connect.commit()
            try:
                self.ids = cursor.execute("""SELECT * FROM ratings""").fetchall()
                self.average_ratings = [0, 0, 0, 0]
                for book in self.ids:
                    id = book[0]
                    rate = book[1]
                    self.book2 = Book(f"""SELECT * FROM books WHERE id={id}""")
                    if self.book2.category()== self.book.category():
                        self.average_ratings[0] += 1
                        self.average_ratings[1] += rate
                    if self.book2.authors() == self.book.authors():
                        self.average_ratings[2] += 1
                        self.average_ratings[3] += rate

                id_category = cursor.execute(f"""
                        SELECT id FROM category_preferences WHERE id = {self.book.category()}""").fetchone()
                if id_category is None:
                    cursor.execute(f"""INSERT INTO category_preferences(id, rating)
                     VALUES({self.book.category()}, {self.average_ratings[1] / self.average_ratings[0]})""")
                else:
                    cursor.execute(f"""
                        UPDATE category_preferences SET rating = {self.average_ratings[1] / self.average_ratings[0]}
                        WHERE id = {self.book.category()}""")
                author = cursor.execute(f'''
                                        SELECT id FROM autor_preferences 
                                        WHERE autor = "{self.book.authors()}"''').fetchone()
                if author is None:
                    cursor.execute(f'''INSERT INTO autor_preferences(autor, rating)
                                     VALUES("{self.book.authors()}", 
                                    {self.average_ratings[1] / self.average_ratings[0]})''')
                else:
                    cursor.execute(f'''
                                        UPDATE autor_preferences SET rating = {self.average_ratings[1] / self.average_ratings[0]}
                                        WHERE autor = "{self.book.authors()}"''')
                connect.commit()
            except Exception as e:
                print(e, 'ERROR')


class SearchBookWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('SearchBookWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        try:
            self.books_layout = BooksLayout(self.qwidget)
            self.button_font = QFont()
            self.button_font.setPointSize(12)
            self.scroll_area.setWidgetResizable(True)
            self.search_button.clicked.connect(self.search)
        except Exception as e:
            self.statusBar().showMessage('Извините, возникла ошибка')

    def search(self):
        try:
            print(f'''SELECT * FROM books WHERE title LIKE "%{self.title_edit.text()}%"''')
            res = cursor.execute(f'''SELECT * FROM books WHERE title LIKE "%{self.title_edit.text()}%"''').fetchall()
            self.books_layout.show_books(res, self)
        except Exception as e:
            self.statusBar().showMessage('Извините, возникла ошибка')
            print(e)

    def open(self):
        try:
            self.book = Book(f'''SELECT * FROM books WHERE title="{self.sender().text()}"''')
            self.book.show()
        except Exception as e:
            self.statusBar().showMessage('Извините, возникла ошибка')


class ReadedBooksWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ReadedWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.ids = cursor.execute("""SELECT id FROM ratings""").fetchall()
        self.books = []
        for id in self.ids:
            self.books.append(cursor.execute(f'''SELECT * FROM books WHERE id={id[0]}''').fetchone())
        self.books_layout = BooksLayout(self.qwidget)
        self.scroll_area.setWidgetResizable(True)
        self.books_layout.show_books(self.books, self)

    def open(self):
        self.book = Book(f'''SELECT * FROM books WHERE title="{self.sender().text()}"''')
        self.book.show()


class Book:
    def __init__(self, query=None, info=None):
        print(query, info)
        if query is not None:
            info = cursor.execute(query).fetchone()
            print(info)
        self.info = {'id': info[0],
                     'title': info[1],
                     'category': info[2],
                     'authors': ', '.join(info[3].split(';')),
                     'year': info[4],
                     'cover': info[5],
                     'rating': info[6]}

    def show(self):
        print('creating successful')
        self.window = BookWindow(self)
        self.window.show()

    def id(self):
        return self.info['id']

    def title(self):
        return self.info['title']

    def category(self):
        return self.info['category']

    def authors(self):
        return self.info['authors']

    def year(self):
        return self.info['year']

    def cover(self):
        return self.info['cover']

    def rating(self):
        return self.info['rating']


class BooksLayout(QVBoxLayout):
    def __init__(self, window):
        try:
            super().__init__(window)
        except Exception as e:
            print(e)

    def show_books(self, res, window):
        try:
            while self.count():
                item = self.takeAt(0)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            for info in res:
                button = QPushButton(info[1])
                button.setMinimumHeight(50)
                button.setMaximumWidth(540)
                button.setFont(window.button_font)
                button.clicked.connect(window.open)
                self.addWidget(button)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    connect = sqlite3.connect("DB.sqlite")
    cursor = connect.cursor()
    print(cursor.execute(f"""SELECT name FROM categories 
            WHERE id=26""").fetchone()[0])
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # book = Book("""SELECT * FROM books WHERE id=1""")
    # bw = BookWindow(book)
    # bw.show()
    sys.exit(app.exec())
