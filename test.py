from flask import Flask, render_template, request, jsonify
from flask_db2 import DB2
from dotenv import load_dotenv
import os
import secrets
import folium
from wordcloud import WordCloud
import plotly.express as px
import pandas as pd
import base64
from io import BytesIO
import random

load_dotenv()

def blue_red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(200, 80%%, %d%%)" % random.randint(40, 60)

app = Flask(__name__)
# Definir a chave secreta
app.secret_key = secrets.token_urlsafe(16)

# Configuração do DB2
app.config['DB2_DATABASE'] = os.getenv('DB2_DATABASE')
app.config['DB2_HOSTNAME'] = os.getenv('DB2_HOST')
app.config['DB2_USERNAME'] = os.getenv('DB2_USER')
app.config['DB2_PASSWORD'] = os.getenv('DB2_PASSWORD')
db2 = DB2(app)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para buscar ruas de um bairro
@app.route('/buscar_ruas')
def buscar_ruas():
    bairro = request.args.get('bairro')
    query = "SELECT DISTINCT RUA FROM LOCATIONS WHERE BAIRRO=? ORDER BY RUA ASC"
    ruas = [row[0] for row in db2.connection.execute(query, (bairro,)).fetchall()]
    return jsonify(ruas)

# Rota para o formulário de reclamação
@app.route('/formulario')
def formulario():
    query = "SELECT DISTINCT BAIRRO FROM LOCATIONS ORDER BY BAIRRO ASC"
    bairros = [row[0] for row in db2.connection.execute(query).fetchall()]
    return render_template('form.html', bairros=bairros)

# Rota para submeter a reclamação
@app.route('/submeter', methods=['POST'])
def submeter():
    try:
        rua = request.form['rua']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        categoria = request.form['categoria']
        descricao = request.form['descricao']

        insert_query = "INSERT INTO USERINPUT (RUA, BAIRRO, CIDADE, TIPO_RECLAMACAO, COMENTARIO) VALUES (?, ?, ?, ?, ?)"
        db2.connection.execute(insert_query, (rua, bairro, cidade, categoria, descricao))
        db2.connection.commit()

        # DB2 não possui LAST_INSERT_ID()
        # Buscar o ID do último registro inserido
        select_last_id = "SELECT ID FROM USERINPUT ORDER BY ID DESC FETCH FIRST 1 ROWS ONLY"
        last_inserted_id = db2.connection.execute(select_last_id).fetchone()[0]

        return jsonify({"mensagem": "Reclamação registrada com sucesso! - Seu Ticket # é "+str(last_inserted_id)})

    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    query = """SELECT A.RUA, A.BAIRRO, A.TIPO_RECLAMACAO, A.COMENTARIO, A.CREATED_AT, B.LATITUDE, B.LONGITUDE
               FROM USERINPUT as A
               INNER JOIN LOCATIONS as B 
               ON A.BAIRRO=B.BAIRRO and A.RUA=B.RUA 
               WHERE A.RESOLVIDO is null"""
    data = db2.connection.execute(query).fetchall()

    # Mapa de calor
    df = pd.DataFrame(data, columns=['RUA', 'BAIRRO', 'TIPO_RECLAMACAO', 'COMENTARIO', 'CREATED_AT', 'LATITUDE', 'LONGITUDE'])
    mapa = folium.Map(location=[df['LATITUDE'].mean(), df['LONGITUDE'].mean()], zoom_start=10)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=f"Tipo: {row['TIPO_RECLAMACAO']}Comentário: {row['COMENTARIO']}",
            tooltip=row['BAIRRO']
        ).add_to(mapa)

    # Wordcloud
    text = " ".join(comentario for _, _, _, comentario, _, _, _ in data)
    wordcloud = WordCloud(background_color="white", width=500, height=300, color_func=blue_red_color_func).generate(text)

    # Converter a imagem para bytes
    image_bytes = BytesIO()
    wordcloud.to_image().save(image_bytes, format='PNG')
    image_bytes.seek(0)
    wordcloud_image = base64.b64encode(image_bytes.getvalue()).decode()

    # Tabela com os últimos 5 casos
    latest_cases = sorted(data, key=lambda x: x[4], reverse=True)[:5]

    # Gráfico de barras
    complaint_counts = {}
    for _, _, complaint_type, _, _, _, _ in data:
        complaint_counts[complaint_type] = complaint_counts.get(complaint_type, 0) + 1

    # Ordena as contagens do maior para o menor
    sorted_counts = sorted(complaint_counts.items(), key=lambda item: item[1], reverse=True)
    complaint_types = [item[0] for item in sorted_counts]
    complaint_values = [item[1] for item in sorted_counts]

    fig_bar = px.bar(x=complaint_types, y=complaint_values, text=complaint_values)
    fig_bar.update_layout(
        title_x=0.5,
        xaxis_title="",  # Remove o título do eixo x
        yaxis_title="",  # Remove o título do eixo y
        plot_bgcolor='white',  # Define o fundo do gráfico para branco
        xaxis_tickangle=-45,  # Rotaciona os labels do eixo x
        yaxis_tickvals=[]
    )
    fig_bar.update_traces(marker_color='#008CBA', textposition='auto', textfont_size=20, textfont_weight='bold')  # Estilo do texto

    return render_template('dashboard.html',
                           mapa=mapa._repr_html_(),
                           wordcloud_image=wordcloud_image,
                           latest_cases=latest_cases,
                           plot_bar=fig_bar.to_html(full_html=True))

# Rota para o encerrar reclamação
@app.route('/encerrar')
def encerrarTicket():
    return render_template('encerrar.html')

# Rota para encerrar ticket a reclamação
@app.route('/encerrarTicket', methods=['POST'])
def submeterEncerrarTicket():
    try:
        ticket = request.form['ticketReclamacao']
        
        select_query = "SELECT ID FROM USERINPUT WHERE ID = ? AND RESOLVIDO is null"
        IDs = db2.connection.execute(select_query, (ticket,)).fetchall()

        if len(IDs) != 0:
            update_query = "UPDATE USERINPUT SET RESOLVIDO=True WHERE ID = ? AND RESOLVIDO is null"
            db2.connection.execute(update_query, (ticket,))
            db2.connection.commit()
            return jsonify({"mensagem": "Reclamação Encerrada com sucesso!"})
        else:
            return jsonify({"mensagem": "Esse Ticket Não existe no sistema ou já foi fechado! Por favor verifique"})

    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})

if __name__ == '__main__':
    app.run(debug=True)