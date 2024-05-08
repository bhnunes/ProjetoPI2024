from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
import secrets


load_dotenv()

app = Flask(__name__)

# Definir a chave secreta
app.secret_key = secrets.token_urlsafe(16)

# Configuração do MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para o formulário de reclamação
@app.route('/formulario')
def formulario():
    return render_template('form.html')

# Rota para submeter a reclamação
@app.route('/submeter', methods=['POST'])
def submeter():
    rua = request.form['rua']
    bairro = request.form['bairro']
    cidade = request.form['cidade']
    categoria = request.form['categoria']
    descricao = request.form['descricao']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO sys.userinput (RUA, BAIRRO, CIDADE, TIPO_RECLAMACAO, COMENTARIO) VALUES (%s, %s, %s, %s,%s)", (rua, bairro, cidade, categoria, descricao))
    mysql.connection.commit()
    cursor.close()


    return jsonify({"mensagem": "Reclamação registrada com sucesso!"})

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    # Lógica para buscar dados do banco de dados e gerar gráficos
    # ...

    return render_template('dashboard.html') #, dados_para_grafico=dados)

if __name__ == '__main__':
    app.run(debug=True)