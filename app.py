from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20))


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=10)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    section = db.relationship('Section', backref='schedules')
    trainer = db.relationship('User', backref='schedules', passive_deletes=True)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Связь с клиентом
    client = db.relationship('User', backref='registrations')
    # Связь с расписанием
    schedule = db.relationship('Schedule', backref='registrations')



class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            add_test_data()


def add_test_data():
    # Тестовые пользователи
    test_users = [
        User(username='admin', password=generate_password_hash('admin123'), role='hr', phone='+79991112233'),
        User(username='manager', password=generate_password_hash('manager123'), role='crm', phone='+79994445566'),
        User(username='trainer1', password=generate_password_hash('trainer123'), role='trainer', phone='+79997778899'),
        User(username='trainer2', password=generate_password_hash('trainer123'), role='trainer', phone='+79998887766'),
        User(username='client1', password=generate_password_hash('client123'), role='client', phone='+79993334455'),
        User(username='client2', password=generate_password_hash('client123'), role='client', phone='+79992223344'),
        User(username='client3', password=generate_password_hash('client123'), role='client', phone='+79991112244'),
        User(username='client4', password=generate_password_hash('client123'), role='client', phone='+79994445577'),
        User(username='client5', password=generate_password_hash('client123'), role='client', phone='+79995556688'),
        User(username='client6', password=generate_password_hash('client123'), role='client', phone='+79996667799'),
        User(username='client7', password=generate_password_hash('client123'), role='client', phone='+79997778800'),
        User(username='client8', password=generate_password_hash('client123'), role='client', phone='+79998889911'),
        User(username='client9', password=generate_password_hash('client123'), role='client', phone='+79999990022'),
        User(username='client10', password=generate_password_hash('client123'), role='client', phone='+79991112255')
    ]

    # Тестовые секции
    test_sections = [
        Section(name='Йога', price=1500, capacity=15),
        Section(name='Фитнес', price=2000, capacity=20),
        Section(name='Плавание', price=2500, capacity=10),
        Section(name='Силовые тренировки', price=1800, capacity=12),
        Section(name='Аэробика', price=1600, capacity=25),
        Section(name='Танцы', price=1700, capacity=18),
        Section(name='Пилатес', price=1900, capacity=15),
        Section(name='Кроссфит', price=2200, capacity=10),
        Section(name='Спортивные игры', price=2000, capacity=30),
        Section(name='Бокс', price=2100, capacity=12),
        Section(name='Кикбоксинг', price=2300, capacity=10),
        Section(name='Тай-чи', price=1600, capacity=15)
    ]

    db.session.add_all(test_users + test_sections)
    db.session.commit()

    # Тестовое расписание с марта 2025 года
    test_schedules = [
        Schedule(section_id=1, trainer_id=3, datetime=datetime(2025, 3, 1, 18, 0), duration=60),
        Schedule(section_id=2, trainer_id=3, datetime=datetime(2025, 3, 2, 19, 0), duration=90),
        Schedule(section_id=3, trainer_id=4, datetime=datetime(2025, 3, 3, 10, 0), duration=45),
        Schedule(section_id=4, trainer_id=4, datetime=datetime(2025, 3, 4, 12, 0), duration=60),
        Schedule(section_id=5, trainer_id=3, datetime=datetime(2025, 3, 5, 14, 0), duration=30),
        Schedule(section_id=6, trainer_id=4, datetime=datetime(2025, 3, 6, 16, 0), duration=75),
        Schedule(section_id=7, trainer_id=3, datetime=datetime(2025, 3, 7, 9, 0), duration=60),
        Schedule(section_id=8, trainer_id=4, datetime=datetime(2025, 3, 8, 11, 0), duration=90),
        Schedule(section_id=9, trainer_id=3, datetime=datetime(2025, 3, 9, 13, 0), duration=60),
        Schedule(section_id=10, trainer_id=4, datetime=datetime(2025, 3, 10, 15, 0), duration=45),
        Schedule(section_id=11, trainer_id=3, datetime=datetime(2025, 3, 11, 17, 0), duration=30),
        Schedule(section_id=4, trainer_id=4, datetime=datetime(2025, 3, 12, 19, 0), duration=60),
        Schedule(section_id=5, trainer_id=3, datetime=datetime(2025, 3, 13, 20, 0), duration=60),
        Schedule(section_id=6, trainer_id=4, datetime=datetime(2025, 3, 14, 21, 0), duration=90),
        Schedule(section_id=7, trainer_id=3, datetime=datetime(2025, 3, 15, 22, 0), duration=45),
        Schedule(section_id=8, trainer_id=4, datetime=datetime(2025, 3, 16, 10, 0), duration=60),
        Schedule(section_id=9, trainer_id=3, datetime=datetime(2025, 3, 17, 11, 0), duration=30),
        Schedule(section_id=10, trainer_id=4, datetime=datetime(2025, 3, 18, 12, 0), duration=60),
        Schedule(section_id=11, trainer_id=3, datetime=datetime(2025, 3, 19, 13, 0), duration=45),
        Schedule(section_id=12, trainer_id=4, datetime=datetime(2025, 3, 20, 14, 0), duration=90)
    ]

    db.session.add_all(test_schedules)
    db.session.commit()


# Создаем таблицы при запуске
create_tables()


# Маршруты
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/prices')
def prices():
    sections = Section.query.all()
    return render_template('prices.html', sections=sections)


@app.route('/schedule')
def schedule():
    schedules = Schedule.query.order_by(Schedule.datetime).all()
    return render_template('schedule.html', schedules=schedules)


@app.route('/staff')
@login_required
def staff():
    trainers = User.query.filter_by(role='trainer').all()
    return render_template('staff.html', trainers=trainers)


@app.route('/add_trainer', methods=['GET', 'POST'])
@login_required
def add_trainer():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        phone = request.form['phone']
        new_trainer = User(username=username, password=password, role='trainer', phone=phone)
        db.session.add(new_trainer)
        db.session.commit()
        flash('Тренер успешно добавлен!', 'success')
        return redirect(url_for('staff'))
    return render_template('add_trainer.html')



@app.route('/edit_trainer/<int:trainer_id>', methods=['GET', 'POST'])
@login_required
def edit_trainer(trainer_id):
    trainer = User.query.get_or_404(trainer_id)
    if request.method == 'POST':
        trainer.username = request.form['username']
        trainer.phone = request.form['phone']
        db.session.commit()
        flash('Данные тренера обновлены!', 'success')
        return redirect(url_for('staff'))
    return render_template('edit_trainer.html', trainer=trainer)



@app.route('/delete_trainer/<int:trainer_id>', methods=['POST'])
@login_required
def delete_trainer(trainer_id):
    trainer = User.query.get_or_404(trainer_id)
    # Удаляем все расписания, связанные с тренером
    Schedule.query.filter_by(trainer_id=trainer.id).delete()
    db.session.delete(trainer)
    db.session.commit()
    flash('Тренер и его расписания удалены!', 'success')
    return redirect(url_for('staff'))


@app.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    if request.method == 'POST':
        client_id = request.form['client_id']
        schedule_id = request.form['schedule_id']

        # Создаем новую регистрацию
        new_registration = Registration(client_id=client_id, schedule_id=schedule_id)
        db.session.add(new_registration)
        db.session.commit()

        flash('Клиент успешно зарегистрирован на занятие!', 'success')
        return redirect(url_for('registration'))

    registrations = Registration.query.all()
    clients = User.query.filter_by(role='client').all()  # Получаем всех клиентов
    schedules = Schedule.query.all()  # Получаем все расписания
    return render_template('registration.html', registrations=registrations, clients=clients, schedules=schedules)


@app.route('/add_registration', methods=['GET', 'POST'])
@login_required
def add_registration():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            phone = request.form['phone']
            new_client = User(username=username, password=password, role='client', phone=phone)
            db.session.add(new_client)
            db.session.commit()
            flash('Новый клиент успешно зарегистрирован!', 'success')
            return redirect(url_for('registration'))
        except KeyError as e:
            flash(f'Ошибка: отсутствует поле {str(e)}', 'danger')
            return redirect(url_for('add_registration'))

    return render_template('add_registration.html')


@app.route('/delete_registration/<int:registration_id>', methods=['POST'])
@login_required
def delete_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    db.session.delete(registration)
    db.session.commit()
    flash('Регистрация удалена!', 'success')
    return redirect(url_for('registration'))


@app.route('/analytics')
@login_required
def analytics():
    # Общая сумма платежей
    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    # Количество клиентов
    total_clients = User.query.filter_by(role='client').count()

    # Получаем данные о популярности услуг и доходах
    section_data = db.session.query(
        Section.name,
        db.func.count(Registration.id).label('registration_count'),
        (db.func.count(Registration.id) * Section.price).label('total_income')
    ).outerjoin(Schedule, Section.id == Schedule.section_id) \
     .outerjoin(Registration, Schedule.id == Registration.schedule_id) \
     .group_by(Section.id).all()

    return render_template('analytics.html', total_payments=total_payments, total_clients=total_clients,
                           section_data=section_data)


@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if request.method == 'POST':
        try:
            schedule.section_id = request.form['section_id']
            schedule.trainer_id = request.form['trainer_id']
            schedule.datetime = datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')
            schedule.duration = int(request.form['duration'])  # Убедитесь, что это целое число
            db.session.commit()
            flash('Расписание обновлено!', 'success')
            return redirect(url_for('schedule'))
        except Exception as e:
            flash(f'Ошибка при обновлении расписания: {str(e)}', 'danger')

    sections = Section.query.all()
    trainers = User.query.filter_by(role='trainer').all()
    return render_template('edit_schedule.html', schedule=schedule, sections=sections, trainers=trainers)


@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Расписание удалено!', 'success')
    return redirect(url_for('schedule'))


if __name__ == '__main__':
    app.run(debug=True)
