from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
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


# Rota para buscar ruas de um bairro
@app.route('/buscar_ruas')
def buscar_ruas():
    bairro = request.args.get('bairro')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT RUA FROM sys.locations WHERE BAIRRO=%s ORDER BY RUA ASC", (bairro,))
    ruas = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return jsonify(ruas)


# Rota para o formulário de reclamação
@app.route('/formulario')
def formulario():
    cursor = mysql.connection.cursor()
    cursor.execute("Select distinct BAIRRO from sys.locations order by BAIRRO ASC;")
    bairros = [row[0] for row in cursor.fetchall()]
    cursor.close()
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
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO sys.userinput (RUA, BAIRRO, CIDADE, TIPO_RECLAMACAO, COMENTARIO) VALUES (%s, %s, %s, %s,%s)", (rua, bairro, cidade, categoria, descricao))
        mysql.connection.commit()

        # Get the last inserted ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = cursor.fetchone()[0]
        return jsonify({"mensagem": "Reclamação registrada com sucesso! - Seu Ticket # é "+str(last_inserted_id)})
    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})
    finally:
        cursor.close()

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT A.RUA, A.BAIRRO, A.TIPO_RECLAMACAO, A.COMENTARIO, A.CREATED_AT, B.LATITUDE, B.LONGITUDE 
                      FROM sys.userinput as A 
                      INNER JOIN sys.locations as B 
                      ON A.BAIRRO=B.BAIRRO and A.RUA=B.RUA WHERE A.RESOLVIDO is null """)
    data = cursor.fetchall()
    cursor.close()

    # Mapa de calor
    df = pd.DataFrame(data, columns=['RUA', 'BAIRRO', 'TIPO_RECLAMACAO', 'COMENTARIO', 'CREATED_AT', 'LATITUDE', 'LONGITUDE'])
    mapa = folium.Map(location=[df['LATITUDE'].mean(), df['LONGITUDE'].mean()], zoom_start=10)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=f"<center><b>Tipo:</b> {row['TIPO_RECLAMACAO']}<br><b>Comentário:</b> {row['COMENTARIO']}</center>",
            tooltip=row['BAIRRO']
        ).add_to(mapa)

    
    # Wordcloud
    text = " ".join(comentario for _, _, _, comentario, _, _, _ in data)

    wordcloud = WordCloud(background_color="white", width=500, height=300, color_func=blue_red_color_func).generate(text)

    #wordcloud = WordCloud(background_color="white",width=500, height=300).generate(text)
    
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

    
    fig_bar = px.bar(x=complaint_types, y=complaint_values,
                 text=complaint_values)

    fig_bar.update_layout(
    title_x=0.5,
    xaxis_title="",  # Remove o título do eixo x
    yaxis_title="",  # Remove o título do eixo y
    plot_bgcolor='white',  # Define o fundo do gráfico para branco
    xaxis_tickangle=-45,  # Rotaciona os labels do eixo x
    yaxis_tickvals=[]
    )

    fig_bar.update_traces(marker_color='#008CBA',textposition='auto', textfont_size=20, textfont_weight='bold')  # Estilo do texto

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
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT ID FROM sys.userinput WHERE ID = %s AND RESOLVIDO is null" , (ticket,))
        IDs=cursor.fetchall()
        if len(IDs)!=0:
            cursor.execute("UPDATE sys.userinput SET RESOLVIDO=True WHERE ID = %s AND RESOLVIDO is null" , (ticket,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"mensagem": "Reclamação Encerrada com sucesso!"})
        else:
            return jsonify({"mensagem": "Esse Ticket Não existe no sistema ou já foi fechado! Por favor verifique"})    
    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)