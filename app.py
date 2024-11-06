from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import base64
import matplotlib.pyplot as plt
import io
from sqlalchemy.sql import func
import matplotlib.ticker as ticker


# Configuración básica de la aplicación Flask
app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'clavedeprueba'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8')

# Configuración del LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Creación de la tabla IdUsuario
class IdUsuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    favoritas = db.relationship('PeliculaFavorita', backref='IdUsuario', lazy=True)

# Creación de la tabla Película
class Pelicula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String, nullable=False)
    nombre_img = db.Column(db.String, nullable=False)
    mimetype = db.Column(db.String, nullable=False)
    titulo = db.Column(db.String, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    favoritas = db.relationship('PeliculaFavorita', backref='Pelicula', lazy=True)
    vistas = db.relationship('PeliculaVista', backref='Pelicula', lazy=True)

# Creación de la tabla Serie
class Serie (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String, nullable=False)
    nombre_img = db.Column(db.String, nullable=False)
    mimetype = db.Column(db.String, nullable=False)
    titulo = db.Column(db.String, nullable=False)
    numero_capitulos = db.Column(db.Integer, nullable=False)
    duracion_capitulo = db.Column(db.Integer, nullable=False)
    numero_temporadas = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    favoritas = db.relationship('SerieFavorita', backref='Serie', lazy=True)
    vistas = db.relationship('SerieVista', backref='Serie', lazy=True)


# Creación de la tabla PeliculaFavorita
class PeliculaFavorita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario', db.Integer, db.ForeignKey('id_usuario.id'))
    id_pelicula = db.Column('id_pelicula', db.Integer, db.ForeignKey('pelicula.id'))

# Creación de la tabla SerieFavorita
class SerieFavorita(db.Model):
    id = db.Column (db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario',db.Integer, db.ForeignKey('id_usuario.id'))
    id_serie = db.Column('id_serie', db.Integer, db.ForeignKey('serie.id'))


# Creación de la tabla PeliculaVista
class PeliculaVista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario',db.Integer, db.ForeignKey('id_usuario.id'))
    id_pelicula = db.Column('id_pelicula', db.Integer, db.ForeignKey('pelicula.id'))

# Creación de la tabla SerieVista
class SerieVista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario', db.Integer, db.ForeignKey('id_usuario.id'))
    id_serie = db.Column('id_serie', db.Integer, db.ForeignKey('serie.id'))

# Función para cargar el usuario desde la base de datos
@login_manager.user_loader
def load_user(id_usuario):
    return IdUsuario.query.get(int(id_usuario))

# Ruta para registrar nuevos usuarios
@app.route('/register', methods= ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method = 'pbkdf2:sha256')
        nuevo_usuario = IdUsuario(username=username, password=hashed_password)
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Registro correcto', 'success')

        except Exception as e:
            db.session.rollback()
            flash('Nombre de usuario en uso. Por favor, elige otro', 'error')
    return render_template('register.html')

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = IdUsuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            if current_user.is_authenticated:
                return redirect(url_for('contents'))
        else:
            flash ('Comprueba el nombre de usuario y contraseña', 'error')
    return render_template('home.html')

# Ruta para el cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash ('Se ha cerrado la sesión')
    return redirect(url_for('home'))

# Ruta para la página de inicio
@app.route('/')
def home():
    return render_template('home.html')

# Ruta para la página principal con el contenido
@app.route('/contents')
@login_required
def contents():
    return render_template('contents.html')

# Ruta para la página del administrador
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash("Solo los administradores pueden acceder a esta página", "error")
        return redirect(url_for('contents'))

# Ruta para el catálogo de películas
@app.route('/catalogo_peliculas')
@login_required
def catalogo_peliculas():
    catalogo = Pelicula.query.all()
    return render_template('catalogo-peliculas.html', catalogo=catalogo)

# Ruta para el catálogo de series
@app.route('/catalogo_series')
@login_required
def catalogo_series():
    catalogo = Serie.query.all()
    return render_template('catalogo-series.html', catalogo=catalogo)

# Ruta para la gestión de películas
@app.route('/gestion_peliculas', methods=['POST', 'GET'])
@login_required
def gestion_peliculas():
    if request.method == 'POST':
        imagen = request.files['imagen']
        nombre_imagen = secure_filename(imagen.filename)
        mimetype = imagen.mimetype
        titulo = request.form['titulo']
        duracion = request.form ['duracion']
        genero = request.form ['genero']
        anio = request.form['anio']

        pelicula_nueva = Pelicula(img=imagen.read(), nombre_img= nombre_imagen, mimetype=mimetype, titulo= titulo,
                                  duracion= duracion, genero=genero, anio = anio)
        db.session.add(pelicula_nueva)
        db.session.commit()
        flash ("Película añadida", "success")

    peliculas = Pelicula.query.all()
    return render_template('gestion-peliculas.html', peliculas=peliculas)


# Ruta para editar películas
@app.route('/editar_peliculas/<int:id>', methods=['POST', 'GET'])
@login_required
def editar_peliculas(id):
    peliculas = db.session.query(Pelicula).all()
    pelicula = db.session.query(Pelicula).filter_by(id=int(id)).first()

    if request.method == 'POST':
        nueva_imagen = request.files['imagen']
        nuevo_titulo = request.form['titulo']
        nueva_duracion = request.form['duracion']
        nuevo_genero = request.form['genero']
        nuevo_anio = request.form['anio']

        if nueva_imagen:
                pelicula.img = nueva_imagen.read()
                pelicula.nombre_img = secure_filename(nueva_imagen.filename)
                pelicula.mimetype = nueva_imagen.mimetype

        if nuevo_titulo:
            pelicula.titulo = nuevo_titulo

        if nueva_duracion:
            pelicula.duracion = nueva_duracion

        if nuevo_genero:
            pelicula.genero = nuevo_genero

        if nuevo_anio:
            pelicula.anio = nuevo_anio

        db.session.commit()
        flash('Película editada correctamente', 'success')
        return redirect(url_for('gestion_peliculas'))

    return render_template('editar-peliculas.html', pelicula = pelicula, peliculas=peliculas)

# Ruta para editar series
@app.route('/editar_series/<int:id>', methods=['POST', 'GET'])
@login_required
def editar_series(id):
    series = db.session.query(Serie).all()
    serie = db.session.query(Serie).filter_by(id=int(id)).first()

    if request.method == 'POST':
        nueva_imagen = request.files['imagen']
        nuevo_titulo = request.form['titulo']
        nuevo_numero_capitulos = request.form['numero_capitulos']
        nueva_duracion_capitulo = request.form['duracion_capitulo']
        nuevo_numero_temporadas = request.form['numero_temporadas']
        nuevo_genero = request.form['genero']
        nuevo_anio = request.form['anio']

        if nueva_imagen:
            serie.img = nueva_imagen.read()
            serie.nombre_img = secure_filename(nueva_imagen.filename)
            serie.mimetype = nueva_imagen.mimetype

        if nuevo_titulo:
            serie.titulo = nuevo_titulo

        if nuevo_numero_capitulos:
            serie.numero_capitulos = nuevo_numero_capitulos

        if nueva_duracion_capitulo:
            serie.duracion_capitulo = nueva_duracion_capitulo

        if nuevo_numero_temporadas:
            serie.numero_temporadas = nuevo_numero_temporadas

        if nuevo_genero:
            serie.genero = nuevo_genero

        if nuevo_anio:
            serie.anio = nuevo_anio

        db.session.commit()
        flash('Serie editada correctamente', "success")
        return redirect(url_for('gestion_series'))

    return render_template('editar-series.html', serie=serie, series=series)


# Ruta para eliminar películas
@app.route('/eliminar_peliculas/<int:id>')
@login_required
def eliminar_pelicula(id):
    pelicula = Pelicula.query.get(id)
    if pelicula:
        db.session.delete(pelicula)
        db.session.commit()
        flash("Película eliminada", "success")
    return redirect(url_for('gestion_peliculas'))

# Ruta para eliminar series
@app.route('/eliminar_series/<int:id>')
@login_required
def eliminar_series(id):
    serie= Serie.query.get(id)
    if serie:
        db.session.delete(serie)
        db.session.commit()
        flash("Serie eliminada", "success")
    return redirect(url_for('gestion_series'))


# Ruta para la gestión de series
@app.route('/gestion_series', methods=['POST', 'GET'])
@login_required
def gestion_series():
    if request.method == 'POST':
        imagen = request.files['imagen']
        nombre_imagen = secure_filename(imagen.filename)
        mimetype = imagen.mimetype
        titulo = request.form['titulo']
        numero_capitulos = request.form['numero_capitulos']
        duracion_capitulo = request.form['duracion_capitulo']
        numero_temporadas = request.form['numero_temporadas']
        genero = request.form['genero']
        anio = request.form['anio']

        serie_nueva = Serie(img=imagen.read(), nombre_img=nombre_imagen, mimetype=mimetype,titulo=titulo,
                            numero_capitulos=numero_capitulos, duracion_capitulo=duracion_capitulo,
                            numero_temporadas=numero_temporadas, genero=genero, anio=anio)

        db.session.add(serie_nueva)
        db.session.commit()
        flash("Serie añadida", "success")

    series = Serie.query.all()
    return render_template('gestion-series.html', series=series)

# Ruta para marcar película como favorita
@app.route('/marcar_pelicula_favorita/<int:id>', methods=['POST','GET'])
@login_required
def marcar_pelicula_favorita(id):
    pelicula = Pelicula.query.get(id)
    usuario = current_user

    if pelicula:
        pelicula_favorita = PeliculaFavorita(id_usuario=usuario.id, id_pelicula=pelicula.id)
        db.session.add(pelicula_favorita)
        db.session.commit()
        flash('Película marcada como favorita', 'success')
    return redirect(request.referrer)

# Ruta para marcar película como vista
@app.route('/marcar_pelicula_vista/<int:id>', methods=['POST', 'GET'])
@login_required
def marcar_pelicula_vista(id):
    pelicula = Pelicula.query.get(id)
    usuario = current_user

    if pelicula:
        pelicula_vista = PeliculaVista(id_usuario=usuario.id, id_pelicula=pelicula.id)
        db.session.add(pelicula_vista)
        db.session.commit()
        flash('Película marcada como vista', 'success')
    return redirect(request.referrer)

# Ruta para marcar series como vistas
@app.route('/marcar_serie_vista/<int:id>', methods=['GET','POST'])
@login_required
def marcar_serie_vista(id):
    serie = Serie.query.get(id)
    usuario = current_user

    if serie:
        serie_vista = SerieVista(id_usuario=usuario.id, id_serie=serie.id)
        db.session.add(serie_vista)
        db.session.commit()
        flash('Serie marcada como vista', 'success')
    return redirect(request.referrer)

# Ruta para marcar series como favoritas
@app.route('/marcar_serie_favorita/<int:id>', methods= ['POST','GET'])
@login_required
def marcar_serie_favorita(id):
    serie = Serie.query.get(id)
    usuario = current_user

    if serie:
        serie_favorita = SerieFavorita(id_usuario=usuario.id, id_serie=serie.id)
        db.session.add(serie_favorita)
        db.session.commit()
        flash('Serie marcada como favorita', 'success')
    return redirect(request.referrer)


# Ruta para mostrar las películas y series favoritas
@app.route('/favoritas')
@login_required
def mostrar_favoritas():
    peliculas_favoritas = (db.session.query(Pelicula).join(PeliculaFavorita).
                           filter(PeliculaFavorita.id_usuario == current_user.id).all())
    series_favoritas = (db.session.query(Serie).join(SerieFavorita).
                        filter(SerieFavorita.id_usuario == current_user.id).all())
    return render_template('favoritas.html', peliculas_favoritas=peliculas_favoritas,
                           series_favoritas= series_favoritas)

# Ruta para mostrar las películas y series vistas
@app.route('/vistas')
@login_required
def mostrar_vistas():
    peliculas_vistas = (db.session.query(Pelicula).join(PeliculaVista).
                      filter(PeliculaVista.id_usuario == current_user.id).all())
    series_vistas = (db.session.query(Serie).join(SerieVista).
                     filter(SerieVista.id_usuario == current_user.id).all())

    return render_template('vistas.html', peliculas_vistas=peliculas_vistas,
                           series_vistas=series_vistas)

# Ruta para la gestión de usuarios
@app.route('/gestion_usuarios', methods=['POST', 'GET'])
@login_required
def crear_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        nuevo_usuario = IdUsuario(username=username, password=hashed_password)

        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario creado", "success")

    usuarios = IdUsuario.query.all()
    return render_template('gestion-usuarios.html', usuarios=usuarios)

# Ruta para eliminar usuarios
@app.route('/eliminar_usuarios/<int:id>')
@login_required
def eliminar_usuario(id):
    usuario = IdUsuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado", "success")
    return redirect(url_for('crear_usuario'))

# Ruta para modificar usuarios
@app.route('/editar_usuarios/<int:id>', methods=['POST', 'GET'])
@login_required
def editar_usuarios(id):
    usuarios = db.session.query(IdUsuario).all()
    usuario = db.session.query(IdUsuario).filter_by(id=int(id)).first()

    if request.method == 'POST':
        nuevo_username = request.form['username']
        nuevo_password = request.form['password']

        if nuevo_username:
            usuario.username = nuevo_username

        if nuevo_password:
            usuario.password = generate_password_hash(nuevo_password,method='pbkdf2:sha256')

        db.session.commit()
        flash("Usuario editado con éxito", 'success')
        return redirect(url_for('crear_usuario'))

    return render_template('editar-usuarios.html', usuario=usuario, usuarios=usuarios)


# Ruta para la búsqueda por título
@app.route('/busqueda', methods=['POST', 'GET'])
@login_required
def busqueda():
    busqueda_pelicula = []
    busqueda_serie= []

    if request.method == 'POST':
        busqueda = request.form.get('busqueda')
        if busqueda:
            busqueda_pelicula = Pelicula.query.filter(Pelicula.titulo.like(busqueda + '%')).all()
            busqueda_serie = Serie.query.filter(Serie.titulo.like(busqueda + '%')).all()

    return render_template('busqueda.html', busqueda_pelicula=busqueda_pelicula,
                           busqueda_serie=busqueda_serie)

# Ruta para las estadísticas del usuario
@app.route('/estadisticas')
@login_required
def estadisticas():
    total_peliculas = len(db.session.query(Pelicula).join(PeliculaVista).
                                filter(PeliculaVista.id_usuario == current_user.id).all())

    total_series = len(db.session.query(Serie).join(SerieVista).
                     filter(SerieVista.id_usuario == current_user.id).all())

    # Creación gráfica número visualizaciones
    datos = {'Películas': total_peliculas, 'Series':total_series}
    peliculas_series = list(datos.keys())
    valores = list(datos.values())

    fig = plt.figure(figsize= (10,5))

    plt.bar(peliculas_series, valores, color = 'blue', width =0.3)

    plt.ylabel("Número de visualizaciones ")
    plt.title("Tus estadísticas de visionado")

    y_axis = plt.gca().yaxis
    y_axis.set_major_locator(ticker.MultipleLocator(1))

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    graph_data = buf.getvalue()

    minutos_totales_peliculas = (db.session.query(func.sum(Pelicula.duracion)).join(PeliculaVista).
                        filter(PeliculaVista.id_usuario == current_user.id).all())

    minutos_totales_series = (db.session.query(func.sum(Serie.duracion_capitulo * Serie.numero_capitulos).
                                label('minutos_totales')).join(SerieVista).
                                filter(SerieVista.id_usuario == current_user.id).first())


    return render_template('estadisticas.html', total_peliculas=total_peliculas,
                           total_series=total_series, graph_data=graph_data,
                           minutos_totales_peliculas=minutos_totales_peliculas,
                           minutos_totales_series=minutos_totales_series)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

