import sqlite3
import sys
import csv

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QLabel, QFileDialog, QScrollArea, \
    QVBoxLayout, QPushButton, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6 import uic


class MainWindow(QMainWindow):
    # Главное окно
    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.search_button.clicked.connect(self.open_search_book)
        self.readed_button.clicked.connect(self.open_readed)
        self.parameters_search_button.clicked.connect(self.open_parameters_search)
        self.rec_button.clicked.connect(self.open_recommendations)

    def open_readed(self):
        self.readed = ReadedBooksWindow()
        self.readed.show()

    def open_search_book(self):
        self.search_book = SearchBookWindow()
        self.search_book.show()

    def open_parameters_search(self):
        self.parameters_search = SearchParametersWindow()
        self.parameters_search.show()

    def open_recommendations(self):
        self.recommendations_window = RecommendationsWindow()
        self.recommendations_window.show()

    def closeEvent(self, a0):
        connect.close()


class BookWindow(QWidget):
    # Окно детального отображения книги
    def __init__(self, book):
        super().__init__()
        self.book = book
        uic.loadUi('BookWindow_design.ui', self)
        self.initUI()

    def initUI(self):
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
        if self.ok:
            if cursor.execute(f"""SELECT * FROM ratings WHERE id = {self.book.id()}""").fetchone():
                cursor.execute(f"""UPDATE ratings SET rating = {self.number} WHERE id = {self.book.id()}""")
                connect.commit()
            else:
                cursor.execute(f"""INSERT INTO ratings(id, rating) VALUES({self.book.id()}, {self.number})""")
                connect.commit()
            self.ids = cursor.execute("""SELECT * FROM ratings""").fetchall()
            self.average_ratings = [0, 0, 0, 0]
            for book in self.ids:
                id = book[0]
                rate = book[1]
                self.book2 = Book(f"""SELECT * FROM books WHERE id={id}""")
                if self.book2.category() == self.book.category():
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


class SearchBookWindow(QWidget):
    # Окно поиска книги по названию
    def __init__(self):
        super().__init__()
        uic.loadUi('SearchBookWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.books_layout = BooksLayout(self.qwidget)
        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.scroll_area.setWidgetResizable(True)
        self.search_button.clicked.connect(self.search)

    def search(self):
        res = cursor.execute(f'''SELECT * FROM books WHERE title LIKE "%{self.title_edit.text()}%"''').fetchall()
        self.books_layout.show_books(res, self)

    def open(self):
        self.book = Book(f'''SELECT * FROM books WHERE title="{self.sender().text()}"''')
        self.book.show()


class ReadedBooksWindow(QWidget):
    # Окно для отображения прочитанных книг
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


class SearchParametersWindow(QWidget):
    # Окно для поиска по параметрам
    def __init__(self):
        super().__init__()
        uic.loadUi('SearchParametersWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.books_layout = BooksLayout(self.qwidget)
        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.scroll_area.setWidgetResizable(True)
        self.categories = cursor.execute(f'''SELECT name FROM categories ''').fetchall()
        self.category_box.addItem('Не выбрано')
        for category in self.categories:
            self.category_box.addItem(category[0])
        self.search_button.clicked.connect(self.search)
        self.csv_button.clicked.connect(self.save_csv)

    def search(self):
        query = f'''SELECT * FROM books WHERE title LIKE "%{self.title_edit.text()}%" 
                                        AND autor LIKE "%{self.author_edit.text()}%" '''
        if self.year_edit.text() != '':
            query += f'AND year = {int(self.year_edit.text())} '
        if self.category_box.currentText() != 'Не выбрано':
            query += f'''AND category = (SELECT id FROM categories 
            WHERE name = "{self.category_box.currentText()}")'''
        self.books = Recommender(cursor.execute(query).fetchall()).recommend(15)
        self.books_layout.show_books(self.books, self)

    def open(self):
        self.book = Book(f'''SELECT * FROM books WHERE title="{self.sender().text()}"''')
        self.book.show()

    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "CSV files (*.csv);;All files (*)"
        )
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['title', 'category', 'authors', 'year', 'rating on Goodreads'])
            for book in self.books:
                writer.writerow([book[1],
                                 cursor.execute(f'''SELECT name FROM categories WHERE id={book[2]}''').fetchone()[0],
                                 ', '.join(book[3].split(';')), book[-3], book[-1]])


class RecommendationsWindow(QWidget):
    # Окно с рекомендациями
    def __init__(self):
        super().__init__()
        uic.loadUi('RecommendationsWindow_design.ui', self)
        self.initUI()

    def initUI(self):
        self.books_layout = BooksLayout(self.qwidget)
        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.scroll_area.setWidgetResizable(True)
        self.books = Recommender(cursor.execute("""SELECT * FROM books""").fetchall()).recommend(15)
        self.books_layout.show_books(self.books, self)
        self.csv_button.clicked.connect(self.save_csv)

    def open(self):
        self.book = Book(f'''SELECT * FROM books WHERE title="{self.sender().text()}"''')
        self.book.show()

    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "CSV files (*.csv);;All files (*)"
        )
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['title', 'category', 'authors', 'year', 'rating on Goodreads'])
            for book in self.books:
                writer.writerow([book[1],
                                 cursor.execute(f'''SELECT name FROM categories WHERE id={book[2]}''').fetchone()[0],
                                 ', '.join(book[3].split(';')), book[-3], book[-1]])


class Book:
    # Класс для работы с книгами
    def __init__(self, query=None, info=None):
        if query is not None:
            info = cursor.execute(query).fetchone()
        self.info = {'id': info[0],
                     'title': info[1],
                     'category': info[2],
                     'authors': ', '.join(info[3].split(';')),
                     'year': info[4],
                     'cover': info[5],
                     'rating': info[6]}

    def show(self):
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
    # Класс для отображения кнопок с названиями книг из списка
    def __init__(self, window):
        super().__init__(window)

    def show_books(self, res, window):
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


class Recommender:
    # Класс, выдающий n лучших книг по рейтингу среди данных
    def __init__(self, books):
        self.books = books

    def recommend(self, n):
        for i in range(len(self.books)):
            self.books[i] = list(self.books[i])
            index = 1
            category_rating = cursor.execute(f'''SELECT rating FROM category_preferences 
            WHERE id={self.books[i][2]}''').fetchone()
            if category_rating is None:
                category_rating = 7
            else:
                category_rating = category_rating[0]
            index *= category_rating
            author_rating = cursor.execute(f'''SELECT rating FROM autor_preferences 
            WHERE autor="{self.books[i][3]}"''').fetchone()
            if author_rating is None:
                author_rating = 7
            else:
                author_rating = author_rating[0]
            index *= author_rating
            if self.books[i][-1] == '':
                self.books[i][-1] = '3.5'
            index *= float(self.books[i][-1]) * 2
            self.books[i].append(index)
        self.books = sorted(self.books, key=lambda x: -x[-1])
        for i in range(len(self.books)):
            self.books[i] = self.books[i][:-1]
        return self.books[:min(n, len(self.books))]


if __name__ == '__main__':
    connect = sqlite3.connect("DB.sqlite")
    cursor = connect.cursor()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
