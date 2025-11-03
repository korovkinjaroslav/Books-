import sqlite3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 800, 600)


class BookWindow(QWidget):
    def __init__(self, book):
        super().__init__()
        self.book = book
        uic.loadUi('BookWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Оображение книги')
        self.title.setText(self.book.info['title'])
        cover_pixmap = QPixmap(self.book.info['cover'])
        self.cover.setPixmap(cover_pixmap)
        self.cover.setScaledContents(True)
        self.authors.setText(self.book.info['authors'])
        self.categories.setText(cursor.execute(f"""SELECT name FROM categories 
        WHERE id={self.book.info['id']}""").fetchone()[0])
        self.year.setText(str(self.book.info['year']))


class Book:
    def __init__(self, query):
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
        window = BookWindow(self)
        window.show()


if __name__ == '__main__':
    connect = sqlite3.connect("DB.sqlite")
    cursor = connect.cursor()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    book = Book("""SELECT * FROM books WHERE id=1""")
    bw = BookWindow(book)
    bw.show()
    sys.exit(app.exec())
