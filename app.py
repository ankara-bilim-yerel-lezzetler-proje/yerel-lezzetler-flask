from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Merhaba, Flask çalışıyor!"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
