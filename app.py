from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

mai = Flask(__name__)
mai.secret_key = 'uac-secret-key-2026'

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('forum.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

init_db()

# Главная страница форума
@mai.route('/')
def index():
    conn = sqlite3.connect('forum.db')
    cursor = conn.execute('SELECT username, message, created_at FROM messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>UAC Forum</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #f8fafc;
                padding: 40px 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 24px;
                padding: 32px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                border: 1px solid #eef2f6;
            }
            h1 {
                font-size: 28px;
                margin-bottom: 8px;
                color: #1a2a32;
            }
            .sub {
                color: #64748b;
                margin-bottom: 32px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 16px;
            }
            label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }
            input, textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                font-family: inherit;
            }
            button {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 30px;
                font-weight: 600;
                cursor: pointer;
            }
            button:hover { background: #2563eb; }
            .message-card {
                background: #f8fafc;
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 12px;
                border: 1px solid #eef2f6;
            }
            .username {
                font-weight: 700;
                color: #3b82f6;
                margin-bottom: 8px;
            }
            .date {
                font-size: 11px;
                color: #94a3b8;
                margin-top: 8px;
            }
            hr { margin: 24px 0; border-color: #eef2f6; }
            .back-link {
                display: inline-block;
                margin-top: 20px;
                color: #3b82f6;
                text-decoration: none;
            }
            .nav-links {
                margin-bottom: 24px;
                display: flex;
                gap: 16px;
            }
            .nav-links a {
                color: #64748b;
                text-decoration: none;
            }
            .flash {
                background: #dcfce7;
                color: #166534;
                padding: 12px;
                border-radius: 12px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-links">
                <a href="/">🏠 Forum</a>
                <a href="/register">📝 Ro'yxatdan o'tish</a>
                <a href="/login">🔐 Kirish</a>
            </div>
            <h1>💬 UAC Forum</h1>
            <div class="sub">Kimyo bo'yicha savollar va muhokamalar</div>
            
            <form method="post" action="/post">
                <div class="form-group">
                    <label>Ismingiz</label>
                    <input type="text" name="username" placeholder="Elyorbek" required>
                </div>
                <div class="form-group">
                    <label>Xabar</label>
                    <textarea name="message" rows="4" placeholder="Savolingiz yoki fikringiz..." required></textarea>
                </div>
                <button type="submit">📨 Yuborish</button>
            </form>
            
            <hr>
            <h3>📝 So'nggi xabarlar</h3>
            {% for msg in messages %}
            <div class="message-card">
                <div class="username">👤 {{ msg[0] }}</div>
                <div>{{ msg[1] }}</div>
                <div class="date">📅 {{ msg[2] }}</div>
            </div>
            {% endfor %}
            
            <a href="https://elyorbekadkhamoz9-cell.github.io/uac-website/" class="back-link">← Bosh sahifaga qaytish</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, messages=messages)

# Отправка сообщения
@mai.route('/post', methods=['POST'])
def post_message():
    username = request.form['username']
    message = request.form['message']
    if username and message:
        conn = sqlite3.connect('forum.db')
        conn.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
        conn.commit()
        conn.close()
    return redirect('/')

# Страница регистрации
@mai.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('forum.db')
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return '''
                <div class="container"><div class="flash">✅ Ro'yxatdan o'tish muvaffaqiyatli! <a href="/login">Kirish</a></div></div>
                <script>setTimeout(function(){ window.location.href = "/login"; }, 2000);</script>
            '''
        except:
            return '<div class="container"><div class="flash">❌ Bunday foydalanuvchi mavjud</div></div>'
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Ro'yxatdan o'tish | UAC</title><meta charset="UTF-8"><style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Inter',sans-serif;background:#f8fafc;padding:40px 20px;}
        .container{max-width:500px;margin:0 auto;background:white;border-radius:24px;padding:32px;border:1px solid #eef2f6;}
        h1{font-size:28px;margin-bottom:24px;}
        .form-group{margin-bottom:16px;}
        label{display:block;font-weight:600;margin-bottom:8px;}
        input{width:100%;padding:12px;border:1px solid #e2e8f0;border-radius:12px;}
        button{background:#3b82f6;color:white;border:none;padding:12px 24px;border-radius:30px;cursor:pointer;width:100%;}
        .back-link{display:block;margin-top:20px;text-align:center;color:#64748b;}
    </style></head>
    <body>
        <div class="container">
            <h1>📝 Ro'yxatdan o'tish</h1>
            <form method="post">
                <div class="form-group"><label>Ismingiz</label><input name="username" required></div>
                <div class="form-group"><label>Parol</label><input type="password" name="password" required></div>
                <button type="submit">Ro'yxatdan o'tish</button>
            </form>
            <a href="/" class="back-link">← Orqaga</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

# Страница входа
@mai.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('forum.db')
        cursor = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            return '<div class="container"><div class="flash">✅ Tizimga kirdingiz! <a href="/">Forumga o\'tish</a></div><script>setTimeout(function(){ window.location.href = "/"; }, 2000);</script></div>'
        else:
            return '<div class="container"><div class="flash">❌ Xato login yoki parol</div></div>'
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Kirish | UAC</title><meta charset="UTF-8"><style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Inter',sans-serif;background:#f8fafc;padding:40px 20px;}
        .container{max-width:500px;margin:0 auto;background:white;border-radius:24px;padding:32px;border:1px solid #eef2f6;}
        h1{font-size:28px;margin-bottom:24px;}
        .form-group{margin-bottom:16px;}
        label{display:block;font-weight:600;margin-bottom:8px;}
        input{width:100%;padding:12px;border:1px solid #e2e8f0;border-radius:12px;}
        button{background:#3b82f6;color:white;border:none;padding:12px 24px;border-radius:30px;cursor:pointer;width:100%;}
        .back-link{display:block;margin-top:20px;text-align:center;color:#64748b;}
    </style></head>
    <body>
        <div class="container">
            <h1>🔐 Kirish</h1>
            <form method="post">
                <div class="form-group"><label>Ismingiz</label><input name="username" required></div>
                <div class="form-group"><label>Parol</label><input type="password" name="password" required></div>
                <button type="submit">Kirish</button>
            </form>
            <a href="/register" class="back-link">Ro'yxatdan o'tmaganmisiz?</a>
            <a href="/" class="back-link">← Orqaga</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    mai.run(host='0.0.0.0', port=8080)
