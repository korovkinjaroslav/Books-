import sqlite3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit
from PyQt6.QtCore import Qt


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
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 600)
        self.setWindowTitle('Оображение книги')
        self.title = QLineEdit(self)
        self.title.setText(self.book.info['title'])
        self.title.move(10, 10)
        self.title.resize(380, 50)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = self.title.font()
        f.setPointSize(15)
        self.title.setFont(f)
        self.title.setReadOnly(True)


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
    # book = Book("""SELECT * FROM books WHERE id=1""")
    # bw = BookWindow(book)
    # bw.show()
    sys.exit(app.exec())
