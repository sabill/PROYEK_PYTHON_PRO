#Library dan Framework
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

# --- INISIALISASI APLIKASI ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci_rahasia_sabila_123' # Ganti dengan kunci acak
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#--- DATABASE SETUP ---
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS [cite: 6] ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # Login
    nickname = db.Column(db.String(150), unique=True, nullable=False) # Nama Panggilan
    password = db.Column(db.String(150), nullable=False)
    total_score = db.Column(db.Integer, default=0) # Skor total 

#--- USER LOADER UNTUK FLASK-LOGIN ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE SOAL NLP (Topik: NLP) [cite: 10] ---
QUESTIONS = [
    {"q": "Apa kepanjangan dari NLP?", "opts": ["Natural Language Processing", "Neural Language Program", "New Language Protocol", "Net Link Process"], "a": "Natural Language Processing"},
    {"q": "Proses memecah teks menjadi kata per kata disebut?", "opts": ["Tokenization", "Parsing", "Stemming", "Looping"], "a": "Tokenization"},
    {"q": "Manakah library Python populer untuk NLP?", "opts": ["NLTK", "Pandas", "Matplotlib", "Django"], "a": "NLTK"},
    {"q": "Apa itu 'Stop Words' dalam NLP?", "opts": ["Kata umum (dan, yang, di) yang sering dihapus", "Kata kasar", "Kata sandi", "Kata terakhir kalimat"], "a": "Kata umum (dan, yang, di) yang sering dihapus"},
    {"q": "Teknologi di balik Google Translate adalah?", "opts": ["Machine Translation", "Image Processing", "Blockchain", "IoT"], "a": "Machine Translation"},
    {"q": "ChatGPT adalah contoh dari?", "opts": ["Large Language Model (LLM)", "Database SQL", "Operating System", "Antivirus"], "a": "Large Language Model (LLM)"},
    {"q": "Analisis Sentimen digunakan untuk?", "opts": ["Mengetahui emosi teks (positif/negatif)", "Memperbaiki grammar", "Menerjemahkan bahasa", "Mengubah suara ke teks"], "a": "Mengetahui emosi teks (positif/negatif)"},
    {"q": "Siapa pencipta tes untuk kecerdasan mesin (Turing Test)?", "opts": ["Alan Turing", "Elon Musk", "Bill Gates", "Guido van Rossum"], "a": "Alan Turing"},
]

# --- FUNGSI MOCK CUACA (Simulasi API) ---
# [cite: 24, 25] Harus menampilkan 3 hari, suhu siang & malam
def get_weather_data(city):
    data = []
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    today = datetime.now()
    
    for i in range(3):
        date = today + timedelta(days=i)
        day_name = days[date.weekday()]
        # Random suhu untuk simulasi
        temp_day = random.randint(28, 35)
        temp_night = random.randint(22, 27)
        condition = random.choice(["Cerah", "Berawan", "Hujan Ringan", "Mendung"])
        
        data.append({
            "date": date.strftime("%d-%m-%Y"),
            "day_name": day_name,
            "temp_day": temp_day,
            "temp_night": temp_night,
            "condition": condition
        })
    return {"city": city, "forecast": data}

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    if request.method == 'POST':
        city = request.form.get('city') # [cite: 23]
        if city:
            weather = get_weather_data(city)
    return render_template('index.html', weather=weather)

@app.route('/register', methods=['GET', 'POST']) # 
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Cek Password Match [cite: 29]
        if password != confirm_password:
            flash('Password konfirmasi tidak cocok!', 'danger')
            return redirect(url_for('register'))

        # Cek Unik [cite: 27, 30]
        if User.query.filter_by(username=username).first():
            flash('Login/Username sudah dipakai!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(nickname=nickname).first():
            flash('Nickname sudah dipakai!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, nickname=nickname, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST']) # 
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('quiz'))
        else:
            flash('Login atau Password salah.', 'danger')
            
    return render_template('login.html')

@app.route('/logout') # [cite: 45]
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST']) # 
@login_required
def quiz():
    # Logika Menjawab
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = request.form.get('correct_answer')
        
        if user_answer == correct_answer:
            current_user.total_score += 100 # Tambah poin
            db.session.commit()
            flash('Benar! +100 Poin', 'success')
        else:
            flash(f'Salah! Jawaban yang benar: {correct_answer}', 'danger')
        
        return redirect(url_for('quiz')) # Reload untuk pertanyaan baru [cite: 38]

    # Pilih pertanyaan acak (Tanpa batas) [cite: 38]
    question = random.choice(QUESTIONS)
    # Acak urutan opsi jawaban
    options = question['opts'].copy()
    random.shuffle(options)
    
    return render_template('quiz.html', q=question, options=options)

@app.route('/leaderboard') # 
def leaderboard():
    # Urutkan user berdasarkan skor tertinggi
    users = User.query.order_by(User.total_score.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Buat tabel database saat pertama kali jalan
    app.run(debug=True)