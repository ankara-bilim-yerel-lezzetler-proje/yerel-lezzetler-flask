from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yemekler.db'
db = SQLAlchemy(app)


# --- MODELLER ---

class Yemek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(500))
    yorumlar = db.relationship("Yorum", backref="yemek", cascade="all, delete")


class Yorum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yemek_id = db.Column(db.Integer, db.ForeignKey('yemek.id'))
    yorum = db.Column(db.Text, nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)


# --- ANA SAYFA (READ) ---
@app.route('/')
def index():
    yemekler = Yemek.query.all()
    return render_template('index.html', yemekler=yemekler)


# --- DETAY SAYFASI ---
@app.route('/yemek/<int:id>')
def yemek_detay(id):
    yemek = Yemek.query.get(id)
    return render_template('detay.html', yemek=yemek)


# --- YORUM EKLE ---
@app.route('/yorum-ekle/<int:id>', methods=['POST'])
def yorum_ekle(id):
    yorum_metni = request.form['yorum']
    yorum = Yorum(yemek_id=id, yorum=yorum_metni)
    db.session.add(yorum)
    db.session.commit()
    return redirect(f'/yemek/{id}')


# --- CREATE ---
@app.route('/ekle', methods=['GET', 'POST'])
def ekle():
    if request.method == 'POST':
        yeni = Yemek(
            ad=request.form['ad'],
            aciklama=request.form['aciklama'],
            foto=request.form['foto']
        )
        db.session.add(yeni)
        db.session.commit()
        return redirect('/')
    return render_template('ekle.html')


# --- UPDATE ---
@app.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    yemek = Yemek.query.get(id)
    if request.method == 'POST':
        yemek.ad = request.form['ad']
        yemek.aciklama = request.form['aciklama']
        yemek.foto = request.form['foto']
        db.session.commit()
        return redirect('/')
    return render_template('duzenle.html', yemek=yemek)


# --- DELETE ---
@app.route('/sil/<int:id>')
def sil(id):
    yemek = Yemek.query.get(id)
    db.session.delete(yemek)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
