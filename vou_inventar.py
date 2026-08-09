from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask import render_template
from flask import request


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste.db'

db = SQLAlchemy(app)

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/cad/usuario")
def usuario():
    return render_template("cadastro-usuario.html", titulo="Cadastro de Usuário")

@app.route("/cad/caduser", methods=["POST"])
def caduser():
    return request.form

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
    app.run(debug=True)
    