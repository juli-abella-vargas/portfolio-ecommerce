from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import(current_user, LoginManager, 
                 login_user, logout_user,
                 login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/vou_inventar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = "uno, dos, tres"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Usuario(db.Model):
    id = db.Column("usu_id", db.Integer, primary_key=True)
    nome = db.Column("usu_nome", db.String(256))
    email = db.Column("usu_email", db.String(256))
    senha = db.Column("usu_senha", db.String(256))

    def __init__(self, nome, email, senha):
        self.nome= nome
        self.email = email
        self.senha = senha 

    
    def is_authenticated(self):
        return True

    
    def is_active(self):
        return True

   
    def is_anonymous(self):
        return False

    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    desc = db.Column(db.String(255))

class Pergunta(db.Model):
    __tablename__ = 'perguntas'
    id = db.Column(db.Integer, primary_key=True)
    texto_pergunta = db.Column(db.String(500), nullable=False)
    texto_resposta = db.Column(db.String(500), nullable=True)
    
    anuncio_id = db.Column(db.Integer, nullable=True)
    usuario_id = db.Column(db.Integer, nullable=True)

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    valor_total = db.Column(db.Float, nullable=False) 
    
    anuncio_id = db.Column(db.Integer, nullable=True)
    comprador_id = db.Column(db.Integer, nullable=True) 

class Anuncio(db.Model):
    __tablename__ = 'anuncios'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)  
    
    usuario_id = db.Column(db.Integer, nullable=True)    
    categoria_id = db.Column(db.Integer, nullable=True)

class Favorito(db.Model):
    __tablename__ = "favoritos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)  
    anuncio_id = db.Column(db.Integer, nullable=False)  


@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template("pagnaoencontrada.html")

def load_user(id):
    return Usuario.query.get(id)

#USUARIO
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        hash = hashlib.sha512(str(request.form.get("senha")).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=hash).first()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))       
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/")
@login_required
def index():
   return render_template("index.html")


@app.route("/cad/usuario")
@login_required
def usuario():
    return render_template("cadastro-usuario.html", usuarios = Usuario.query.all(), titulo="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criarusuario():
       
    nome = request.form.get("nome") 
    email = request.form.get("email")
    senha = request.form.get("senha") 
        
    senha_hash = hashlib.sha512(str(senha).encode("utf-8")).hexdigest()
    usuario = Usuario(nome, email, senha_hash)

    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/usuario/detalhar/<int:id>")
@login_required
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/deletar/<int:id>")
@login_required
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/usuario/editar/<int:id>")
@login_required
def editarusuario(id):
    usuario_encontrado = Usuario.query.get(id)
    return render_template("editar-usuario.html", usuario=usuario_encontrado, titulo="Usuário")

@app.route("/usuario/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
        nova_senha = request.form.get("senha")
        if nova_senha:
            usuario.senha = hashlib.sha512(str(nova_senha).encode("utf-8")).hexdigest()

        db.session.commit()     
    return redirect(url_for("usuario"))
 
#PERGUNTA
@app.route("/anuncios/pergunta")
def pergunta():
    return render_template("pergunta.html", perguntas = Pergunta.query.all(), titulo="Perguntas")

@app.route("/pergunta/enviar_pergunta", methods=["POST"])
@login_required
def enviar_pergunta():
    texto = request.form.get("texto_pergunta")
    
    if texto:
        nova_pergunta = Pergunta(texto_pergunta=texto)
        db.session.add(nova_pergunta)
        db.session.commit()       
    return redirect(url_for("pergunta"))

@app.route("/pergunta/responder/<int:id>", methods=["POST"])
@login_required
def responder_pergunta(id):
    pergunta = Pergunta.query.get_or_404(id)
    resposta = request.form.get("texto_resposta")

    if resposta:
        pergunta.texto_resposta = resposta  
        db.session.commit()                        
    return redirect(url_for("pergunta"))

#COMPRA
@app.route("/anuncios/compra")
@login_required
def compra():
    anuncio_id = request.args.get("anuncio_id")
    anuncio = None
    if anuncio_id:
        anuncio = Anuncio.query.get(anuncio_id)
        return render_template("compra.html", anuncio=anuncio, titulo="Finalizar Compra")
    todos_anuncios = Anuncio.query.all()
    return render_template("compra.html", todos_anuncios=todos_anuncios, titulo="Vitrine de Produtos")

@app.route("/compra/finalizar_compra", methods=["POST"])
@login_required
def finalizar_compra():
    qtd = request.form.get("quantidade")
    anuncio_id = request.form.get("anuncio_id")
    
    if qtd and anuncio_id:
        anuncio = Anuncio.query.get(anuncio_id)
        if anuncio:
            quantidade = int(qtd)
            valor_total = quantidade * anuncio.preco

        nova_compra = Compra(
            quantidade=int(quantidade),
            valor_total=float(valor_total),
            anuncio_id=anuncio_id,
            comprador_id=current_user.id
        )

        anuncio.quantidade -= quantidade

        db.session.add(nova_compra)
        db.session.commit()
        return redirect(url_for("relCompras"))
    return redirect(url_for("compra"))

@app.route("/compras/relatorio")
@login_required
def relCompras():
    lista_compras = Compra.query.all()
    return render_template("relCompras.html", compras=lista_compras, titulo="Relatório de Compras")

#VENDAS
@app.route("/vendas/relatorios")
@login_required
def relVendas():
    lista_vendas = Compra.query.all()
    return render_template("relVendas.html", vendas = lista_vendas, titulo ="Relatório de vendas")

#ANUNCIO
@app.route("/anuncio")
@login_required
def anuncio():
    lista_categorias = Categoria.query.all() 
    lista_anuncios = Anuncio.query.all()
    
    return render_template(
        "cadastro-anuncio.html",
        anuncios=lista_anuncios, 
        categorias=lista_categorias,  
        titulo="Cadastro de Anúncio"
    )
        
@app.route("/anuncio/criar", methods=["POST"])
@login_required
def cadanuncio():
    titulo = request.form.get("titulo")
    preco = request.form.get("preco")
    estoque = request.form.get("estoque") or 1
    categoria_id = request.form.get("categoria_id") or 1
    
    if titulo and preco:
        novo_anuncio = Anuncio(
            titulo=titulo,
            preco=float(preco),
            quantidade=int(estoque),
            categoria_id=int(categoria_id),
            usuario_id=current_user.id
        )
        db.session.add(novo_anuncio)
        db.session.commit()
        return redirect(url_for("anuncio"))
    return redirect(url_for("anuncio"))

@app.route("/anuncio/detalhar/<int:id>")
def detalhar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get_or_404(id)
    return render_template(
        "cadastro-anuncio.html", 
        categorias=Categoria.query.all(), 
        anuncios=Anuncio.query.all(), 
        anuncio_detalhe=anuncio_encontrado,
        titulo="Detalhes do Anúncio"
    )

@app.route("/anuncio/editar/<int:id>")
@login_required
def editar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    return render_template("editar-anuncio.html", anuncio=anuncio_encontrado, categorias=Categoria.query.all(), titulo="Anúncio")

@app.route("/anuncio/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    if anuncio_encontrado:
        anuncio_encontrado.titulo = request.form.get("titulo")
        anuncio_encontrado.preco = float(request.form.get("preco"))
        anuncio_encontrado.quantidade = int(request.form.get("estoque") or 1)
        cat_id = request.form.get("categoria_id")
        if cat_id:
            anuncio_encontrado.categoria_id = int(cat_id)
        db.session.commit()
    return redirect(url_for("anuncio"))

@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    if anuncio_encontrado:
        db.session.delete(anuncio_encontrado)
        db.session.commit()
    return redirect(url_for("anuncio"))

#CATEGORIA
@app.route("/config/categoria")
@login_required
def categoria():
    return render_template("categoria.html", categorias= Categoria.query.all(), titulo = "Categoria")

@app.route("/categoria/novo", methods=["POST"])
@login_required
def novacategoria():
    categoria = Categoria(
        nome = request.form.get("nome"), 
        desc = request.form.get("desc")
    )
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for("categoria"))

@app.route("/categoria/deletar/<int:id>")
@login_required
def deletar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    if categoria_encontrada:
        db.session.delete(categoria_encontrada)
        db.session.commit()
    return redirect(url_for("categoria"))

@app.route("/categoria/editar/<int:id>")
@login_required
def editar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    return render_template("editar-categoria.html", categoria=categoria_encontrada, titulo="Categoria")


@app.route("/categoria/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    if categoria_encontrada:
        categoria_encontrada.nome = request.form.get("nome")
        categoria_encontrada.desc = request.form.get("desc")
        db.session.commit()
    return redirect(url_for("categoria"))

#FAVORITOS
@app.route("/favoritos")
@login_required
def favoritos():
    lista_favoritos = Favorito.query.filter_by(usuario_id=current_user.id).all()
    return render_template("favorito.html", favoritos=lista_favoritos, titulo="Meus Favoritos")

@app.route("/favorito/salvar", methods=["POST"])
@login_required
def salvar_favorito():
    anuncio_id = request.form.get("anuncio_id")
    
    if anuncio_id:
        novo_favorito = Favorito(
            usuario_id=current_user.id,
            anuncio_id=int(anuncio_id)
        )
        db.session.add(novo_favorito)
        db.session.commit()
    return redirect(url_for("favoritos"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)  

