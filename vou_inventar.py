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

   

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/cad/usuario")
def usuario():
    return render_template("cadastro-usuario.html", titulo="Cadastro de Usuário")

@app.route("/cad/caduser", methods=["POST"])
def caduser():
    usuario = Usuario(
        nome = request.form.get("user"), 
        email = request.form.get("email"), 
        senha = request.form.get("senha")
        )
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for("usuario"))

@app.route("/cad/anuncio")
def anuncio():
    return render_template("cadastro-anuncio.html", titulo="Cadastro de Anuncio")

@app.route("/cad/cadanuncio", methods=["POST"])
def cadanuncio():
    return request.form

@app.route("/anuncios/pergunta")
def pergunta():
    return render_template("pergunta.html")

@app.route("/anuncios/enviar_pergunta", methods=["POST"])
def enviar_pergunta():
    return request.form

@app.route("/anuncios/compra")
def compra():
    return render_template("compra.html", titulo="Finalizar Compra")

@app.route("/anuncios/finalizar_compra", methods=["POST"])
def finalizar_compra():
    print ("anuncio comprado")
    return "<h3> Compra realizada com sucesso!</h3>"

@app.route("/anuncio/favoritos")
def favoritos():
    print("favorito aqui ")
    return "<h4>COMPRADO!!</h4>"

@app.route("/config/categoria")
def categoria():
    return render_template(categoria.html)


@app.route("/relatorios/vendas")
def relVendas():
    return render_template("relVendas.html")

@app.route("/relatorios/compras")
def relCompras():
    return render_template("relCompras.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)  

