from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/vou_inventar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column("usu_id", db.Integer, primary_key=True)
    nome = db.Column("usu_nome", db.String(256))
    email = db.Column("usu_email", db.String(256))
    senha = db.Column("usu_senha", db.String(256))

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


@app.route("/")
def index():
   return render_template("index.html")

#USUARIO
@app.route("/cad/usuario")
def usuario():
    return render_template("cadastro-usuario.html", usuarios = Usuario.query.all(), titulo="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criarusuario():
    usuario = Usuario(
        nome = request.form.get("user"), 
        email = request.form.get("email"), 
        senha = request.form.get("password")
        )
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/deletar/<int:id>")
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/usuario/editar/<int:id>")
def editarusuario(id):
    usuario_encontrado = Usuario.query.get(id)
    return render_template("editar-usuario.html", usuario=usuario_encontrado, titulo="Usuário")

@app.route("/usuario/atualizar/<int:id>", methods=["POST"])
def atualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.nome = request.form.get("user")
        usuario.email = request.form.get("email")
        usuario.senha = request.form.get("password")
        
        db.session.commit()     
    return redirect(url_for("usuario"))
 

#PERGUNTA
@app.route("/anuncios/pergunta")
def pergunta():
    return render_template("pergunta.html", perguntas = Pergunta.query.all(), titulo="Perguntas")

@app.route("/pergunta/enviar_pergunta", methods=["POST"])
def enviar_pergunta():
    texto = request.form.get("texto_pergunta")
    
    if texto:
        nova_pergunta = Pergunta(texto_pergunta=texto)
        db.session.add(nova_pergunta)
        db.session.commit()       
    return redirect(url_for("pergunta"))

@app.route("/pergunta/responder/<int:id>", methods=["POST"])
def responder_pergunta(id):
    pergunta = Pergunta.query.get_or_404(id)
    resposta = request.form.get("texto_resposta")

    if resposta:
        pergunta.texto_resposta = resposta  
        db.session.commit()                        
    return redirect(url_for("pergunta"))

#COMPRA
@app.route("/anuncios/compra")
def compra():
    return render_template("compra.html", compras = Compra.query.all(), titulo="Finalizar Compra")

@app.route("/compra/finalizar_compra", methods=["POST"])
def finalizar_compra():
    qtd = request.form.get("quantidade")
    total = request.form.get("valor_total")
    anuncio_id = request.form.get("anuncio_id")
    comprador_id = request.form.get("comprador_id")

    if qtd and total:
        nova_compra = Compra(
            quantidade=int(qtd),
            valor_total=float(total),
            anuncio_id=anuncio_id,
            comprador_id=comprador_id
        )
        db.session.add(nova_compra)
        db.session.commit()
    return redirect(url_for("compra"))

@app.route("/compras/relatorio")
def relCompras():
    lista_compras = Compra.query.all()
    return render_template("relCompras.html", compras=lista_compras, titulo="Relatório de Compras")

#VENDAS
@app.route("/vendas/relatorios")
def relVendas():
    lista_vendas = Compra.query.all()
    return render_template("relVendas.html", vendas = lista_vendas, titulo ="Relatório de vendas")

#ANUNCIO
@app.route("/anuncio")
def anuncio():
    return render_template("cadastro-anuncio.html", categorias= Categoria.query.all(), anuncios= Anuncio.query.all(), titulo="Cadastro de Anúncio")
        
@app.route("/anuncio/criar", methods=["POST"])
def cadanuncio():
    titulo = request.form.get("titulo")
    preco = request.form.get("preco")
    estoque = request.form.get("estoque") or 1
    categoria_id = request.form.get("categoria_id") or 1
    usuario_id = request.form.get("usuario_id") or 1

    if titulo and preco:
        novo_anuncio = Anuncio(
            titulo=titulo,
            preco=float(preco),
            quantidade=int(estoque),
            categoria_id=int(categoria_id),
            usuario_id=int(usuario_id)
        )
        db.session.add(novo_anuncio)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/anuncio/deletar/<int:id>")
def deletar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    if anuncio_encontrado:
        db.session.delete(anuncio_encontrado)
        db.session.commit()
    return redirect(url_for("anuncio"))


@app.route("/anuncio/editar/<int:id>")
def editar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    return render_template("editar-anuncio.html", anuncio=anuncio_encontrado, categorias=Categoria.query.all(), titulo="Anúncio")


@app.route("/anuncio/atualizar/<int:id>", methods=["POST"])
def atualizar_anuncio(id):
    anuncio_encontrado = Anuncio.query.get(id)
    if anuncio_encontrado:
        anuncio_encontrado.titulo = request.form.get("titulo")
        anuncio_encontrado.descricao = request.form.get("descricao")
        anuncio_encontrado.preco = float(request.form.get("preco"))
        anuncio_encontrado.quantidade = int(request.form.get("estoque") or 1)
        db.session.commit()
    return redirect(url_for("anuncio"))

#CATEGORIA
@app.route("/config/categoria")
def categoria():
    return render_template("categoria.html", categorias= Categoria.query.all(), titulo = "Categoria")

@app.route("/categoria/novo", methods=["POST"])
def novacategoria():
    categoria = Categoria(
        nome = request.form.get("nome"), 
        desc = request.form.get("desc")
    )
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for("categoria"))

@app.route("/categoria/deletar/<int:id>")
def deletar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    if categoria_encontrada:
        db.session.delete(categoria_encontrada)
        db.session.commit()
    return redirect(url_for("categoria"))

@app.route("/categoria/editar/<int:id>")
def editar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    return render_template("editar-categoria.html", categoria=categoria_encontrada, titulo="Categoria")


@app.route("/categoria/atualizar/<int:id>", methods=["POST"])
def atualizar_categoria(id):
    categoria_encontrada = Categoria.query.get(id)
    if categoria_encontrada:
        categoria_encontrada.nome = request.form.get("nome")
        categoria_encontrada.desc = request.form.get("desc")
        db.session.commit()
    return redirect(url_for("categoria"))

#FAVORITOS
@app.route("/favoritos")
def favoritos():
    lista_favoritos = Favorito.query.all()
    return render_template("favorito.html", favoritos=lista_favoritos, titulo="Meus Favoritos")

@app.route("/favorito/salvar", methods=["POST"])
def salvar_favorito():
    anuncio_id = request.form.get("anuncio_id")
    usuario_id = request.form.get("usuario_id") or 1

    if anuncio_id:
        novo_favorito = Favorito(
            usuario_id=int(usuario_id),
            anuncio_id=int(anuncio_id)
        )
        db.session.add(novo_favorito)
        db.session.commit()
    return redirect(url_for("favoritos"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)  

