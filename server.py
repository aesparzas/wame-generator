import os
import sqlite3

from flask import Flask, request, render_template

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
PLATFORMS = ['android', 'ios', 'iphone', 'windows', 'macintosh', 'macos']
DATABASE = os.path.join(PROJECT_ROOT, 'message.db')


class SQLiteContext:
    def __enter__(self):
        self.con = sqlite3.connect(DATABASE)
        self.cur = self.con.cursor()
        return self.con, self.cur

    def __exit__(self, *args):
        self.con.close()


app = Flask(__name__)


with SQLiteContext() as (con, cur):
    cur.execute('CREATE TABLE IF NOT EXISTS message(message)')


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        text = request.form.get('text', '')
        name = request.form.get('name', '')
        phone = request.form.get('phone', '').replace(' ', '')
        if len(phone) < 10:
            return 'Invalid phone', 400
        if len(phone) == 10:
            phone = '+52' + phone
        if text:
            with SQLiteContext() as (con, cur):
                cur.execute('DELETE FROM message')
                cur.execute('INSERT INTO message VALUES (?)', [text])
                con.commit()
            text = text.replace(' ', '%20')
            text = text.replace('<nombre>', name)
        link = f'https://wa.me/{phone}/?text={text}'

        return render_template('success.html', link=link)

    with SQLiteContext() as (con, cur):
        res = cur.execute('SELECT message FROM message')
        res = res.fetchall()
    if not res:
        res = ''
    else:
        res = res[0][0]

    return render_template('index.html', text=res)




if __name__ == '__main__':
    app.run()
