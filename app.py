from flask import Flask, render_template, request, redirect, url_for, session, flash # session ve flash eklendi
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# DİKKAT: Şifreler kaynak kodda tutulmamalıdır, ancak bu proje için devam ediyoruz.
app.secret_key = "abu-ybs-sifre" 
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Ankarayerel-"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yemekler.db'
db = SQLAlchemy(app)


# --- MODELLER ---

class Yemek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(500))
    # Yorumlar silindiğinde bağlı olduğu yorumları da siler (cascade)
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
    # index.html'e session bilgisi gönderildi
    return render_template('index.html', yemekler=yemekler, logged_in=session.get('logged_in')) 

# --- GİRİŞ SAYFASI --- 
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    hata = None
    if request.method == 'POST':
        kullanici = request.form['kullanici']
        sifre = request.form['sifre']
        if kullanici == ADMIN_USERNAME and sifre == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Başarıyla giriş yapıldı.', 'success')
            return redirect(url_for('ekle'))  
        else:
            hata = "Kullanıcı adı veya şifre hatalı."
            flash(hata, 'danger')
    return render_template('giris.html', hata=hata)

@app.route('/cikis')
def cikis():
    session.pop('logged_in', None)
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('index'))


# --- DETAY SAYFASI ---
@app.route('/yemek/<int:id>')
def yemek_detay(id):
    yemek = Yemek.query.get_or_404(id) # Yemek bulunamazsa 404 döndür
    return render_template('detay.html', yemek=yemek, logged_in=session.get('logged_in'))


# --- YORUM EKLE ---
@app.route('/yorum-ekle/<int:id>', methods=['POST'])
def yorum_ekle(id):
    if not request.form['yorum']:
        flash('Yorum alanı boş bırakılamaz.', 'danger')
        return redirect(f'/yemek/{id}')

    yorum_metni = request.form['yorum']
    yorum = Yorum(yemek_id=id, yorum=yorum_metni)
    db.session.add(yorum)
    db.session.commit()
    flash('Yorumunuz başarıyla eklendi.', 'success')
    return redirect(f'/yemek/{id}')


# --- CREATE (Yemek Ekle) ---
@app.route('/ekle', methods=['GET', 'POST'])
def ekle():
    if not session.get('logged_in'): # <<< GÜVENLİK KONTROLÜ EKLENDİ
        flash('Bu sayfaya erişmek için yönetici girişi yapmalısınız.', 'warning')
        return redirect(url_for('giris'))
        
    if request.method == 'POST':
        if not request.form['ad'] or not request.form['aciklama']:
            flash('Ad ve Açıklama alanları zorunludur.', 'danger')
            return render_template('ekle.html')

        yeni = Yemek(
            ad=request.form['ad'],
            aciklama=request.form['aciklama'],
            foto=request.form['foto']
        )
        db.session.add(yeni)
        db.session.commit()
        flash(f"'{yeni.ad}' başarıyla eklendi.", 'success')
        return redirect('/')
    return render_template('ekle.html', logged_in=True)


# --- UPDATE (Yemek Düzenle) ---
@app.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    if not session.get('logged_in'): # <<< GÜVENLİK KONTROLÜ EKLENDİ
        flash('Bu sayfaya erişmek için yönetici girişi yapmalısınız.', 'warning')
        return redirect(url_for('giris'))
        
    yemek = Yemek.query.get_or_404(id)
    if request.method == 'POST':
        yemek.ad = request.form['ad']
        yemek.aciklama = request.form['aciklama']
        yemek.foto = request.form['foto']
        db.session.commit()
        flash(f"'{yemek.ad}' başarıyla güncellendi.", 'success')
        return redirect('/')
    return render_template('duzenle.html', yemek=yemek, logged_in=True)


# --- DELETE (Yemek Sil) ---
@app.route('/sil/<int:id>')
def sil(id):
    if not session.get('logged_in'): # <<< GÜVENLİK KONTROLÜ EKLENDİ
        flash('Bu işlemi yapmak için yönetici girişi yapmalısınız.', 'warning')
        return redirect(url_for('giris'))
        
    yemek = Yemek.query.get_or_404(id)
    db.session.delete(yemek)
    db.session.commit()
    flash(f"'{yemek.ad}' başarıyla silindi.", 'success')
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)