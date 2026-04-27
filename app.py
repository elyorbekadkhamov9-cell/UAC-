from flask import Flask

mai = Flask(__name__)

@mai.route('/')
def home():
    return "<h1>UAC Forum</h1><p>Ishlayapti!</p>"

@mai.route('/register')
def register():
    return '''
        <form method="post">
            <input name="username" placeholder="Login">
            <input type="password" name="password" placeholder="Parol">
            <button>Ro'yxatdan o'tish</button>
        </form>
    '''

if __name__ == '__main__':
    mai.run(host='0.0.0.0', port=8080)
