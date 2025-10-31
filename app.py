from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'tickets.db'


def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.execute('''CREATE TABLE tickets
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         title TEXT,
                         description TEXT,
                         status TEXT,
                         priority TEXT)''')
        conn.commit()
        conn.close()


@app.route('/', methods=['GET'])
def index():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = "SELECT id, title, description, status, priority FROM tickets"
    filters = []
    params = []

    if status_filter:
        filters.append("status = ?")
        params.append(status_filter)
    if priority_filter:
        filters.append("priority = ?")
        params.append(priority_filter)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    tickets = cursor.fetchall()

    # Calculate summary stats
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'")
    open_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE priority='High' AND status='Open'")
    high_open_count = cursor.fetchone()[0]

    conn.close()
    return render_template('index.html', tickets=tickets, status_filter=status_filter,
                           priority_filter=priority_filter, open_count=open_count,
                           high_open_count=high_open_count)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Low')
        if title:
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO tickets (title, description, status, priority) VALUES (?, ?, ?, ?)",
                         (title, description, "Open", priority))
            conn.commit()
            conn.close()
        return redirect('/')
    return render_template('create.html')


@app.route('/resolve/<int:ticket_id>')
def resolve(ticket_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE tickets SET status = 'Resolved' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
