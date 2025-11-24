from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Veritabanı Ayarları (Proje klasörüne 'yemekler.db' adında bir dosya kurar)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'yemekler.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Veritabanı Modeli (Tablo Yapısı) ---
class Yemek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    resim = db.Column(db.String(255), nullable=True) # Resim linki veya yolu

# Veritabanını ilk çalışmada oluştur
with app.app_context():
    db.create_all()

# --- Rotalar (Sayfa Yönlendirmeleri) ---

# 1. Ana Sayfa (Listeleme)
@app.route('/')
def index():
    tum_yemekler = Yemek.query.all()
    return render_template('index.html', yemekler=tum_yemekler)

# 2. Ekleme Sayfası
@app.route('/ekle', methods=['GET', 'POST'])
def ekle():
    if request.method == 'POST':
        baslik = request.form['baslik']
        aciklama = request.form['aciklama']
        resim = request.form['resim']
        
        yeni_yemek = Yemek(baslik=baslik, aciklama=aciklama, resim=resim)
        db.session.add(yeni_yemek)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ekle.html')

# 3. Detay Sayfası
@app.route('/detay/<int:id>')
def detay(id):
    yemek = Yemek.query.get_or_404(id)
    return render_template('detay.html', yemek=yemek)

# 4. Düzenleme Sayfası
@app.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    yemek = Yemek.query.get_or_404(id)
    if request.method == 'POST':
        yemek.baslik = request.form['baslik']
        yemek.aciklama = request.form['aciklama']
        yemek.resim = request.form['resim']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('duzenle.html', yemek=yemek)

# 5. Silme İşlemi (Sayfası yok, butona basınca çalışır)
@app.route('/sil/<int:id>')
def sil(id):
    yemek = Yemek.query.get_or_404(id)
    db.session.delete(yemek)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)