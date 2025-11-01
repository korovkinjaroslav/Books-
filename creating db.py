# Не запускайте этот файл, он тут на всякий случай
import sqlite3
import csv
con = sqlite3.connect('DB.sqlite')
cur = con.cursor()
categories = {}
cur_category = 1
with open('books.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        row["title"] = list(row['title'])
        for i in range(len(row['title'])):
            if row['title'][i] == '"':
                row['title'][i] = "'"
        row['title'] = ''.join(row['title'])
        print(row['title'])
        row["authors"] = list(row['authors'])
        for i in range(len(row['authors'])):
            if row['authors'][i] == '"':
                row['authors'][i] = "'"
        row['authors'] = ''.join(row['authors'])
        if row["average_rating"] == '':
            row["average_rating"] = '3.5'
        if row['published_year'] == '':
            row['published_year'] = '3000'
        if row['categories'] in categories.keys():
            print(row["title"])
            print(f'INSERT INTO books(title, category, autor, year, description, cover, average_rating)'
                        f' VALUES("{row["title"]}",'
                        f' {categories[row["categories"]]},'
                        f' "{row["authors"]}",'
                        f'{int(row["published_year"])},'
                        f' "default_cover.png",'
                        f' {round(float(row["average_rating"]), 2)})')
            cur.execute(f'INSERT INTO books(title, category, autor, year, cover, average_rating)'
                        f' VALUES("{row["title"]}",'
                        f' {categories[row["categories"]]},'
                        f' "{row["authors"]}",'
                        f'{int(row["published_year"])},'
                        f' "default_cover.png",'
                        f' {round(float(row["average_rating"]), 2)})')
        else:
            print(f'INSERT INTO books(title, category, autor, year, description, cover, average_rating)'
                  f' VALUES("{row["title"]}",'
                  f' {cur_category},'
                  f' "{row["authors"]}",'
                  f'{int(row["published_year"])},'
                  f' "default_cover.png",'
                  f' {round(float(row["average_rating"]), 2)})')
            categories[row["categories"]] = cur_category
            cur_category += 1
            cur.execute(f'INSERT INTO books(title, category, autor, year, cover, average_rating)'
                        f' VALUES("{row["title"]}",'
                        f' {categories[row["categories"]]},'
                        f' "{row["authors"]}",'
                        f'{int(row["published_year"])},'
                        f' "default_cover.png",'
                        f' {round(float(row["average_rating"]), 2)})')
for key in categories.keys():
    print(key, categories[key])
    cur.execute(f'INSERT INTO categories(id, name) VALUES({categories[key]}, "{key}")')
print(cur.execute("""SELECT * FROM categories""").fetchall())
con.commit()
con.close()
