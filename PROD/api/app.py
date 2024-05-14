from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import secrets
import folium
from wordcloud import WordCloud
import base64
from io import BytesIO
import random
import pymysql
import matplotlib
matplotlib.use('Agg')  # Define o backend como 'Agg'
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

app = Flask(__name__)

# Definir a chave secreta
app.secret_key = secrets.token_urlsafe(16)

#Inicializar pool
def open_conn():
    conn = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=30,
        cursorclass=pymysql.cursors.DictCursor,
        db=os.getenv('MYSQL_DB'),
        host=os.getenv('MYSQL_HOST'),
        password=os.getenv('MYSQL_PASSWORD'),
        read_timeout=30,
        port=11025,
        user=os.getenv('MYSQL_USER'),
        write_timeout=30,
    )
    return conn

def blue_red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(200, 80%%, %d%%)" % random.randint(40, 60)


# Função para calcular porcentagem e valor absoluto
def func(pct, allvals):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return f"{pct:.1f}%\n({absolute:d})" 

def gerar_dados_dashboard():
    try:
        conn=open_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT A.RUA, A.BAIRRO, A.TIPO_RECLAMACAO, A.COMENTARIO, A.CREATED_AT, B.LATITUDE, B.LONGITUDE 
                        FROM defaultdb.USERINPUT as A 
                        INNER JOIN defaultdb.LOCATIONS as B 
                        ON A.BAIRRO=B.BAIRRO and A.RUA=B.RUA WHERE A.RESOLVIDO IS NULL order by A.CREATED_AT DESC""")
        data = cursor.fetchall()

        # Mapa de calor
        latitudes = [row['LATITUDE'] for row in data]
        longitudes = [row['LONGITUDE'] for row in data]

        if len(latitudes)>0:
            sem_dados=False
            mapa = folium.Map(location=[sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)], zoom_start=10)
            for row in data:
                folium.Marker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    popup=f"Tipo: {row['TIPO_RECLAMACAO']}Comentário: {row['COMENTARIO']}",
                    tooltip=row['BAIRRO']
                ).add_to(mapa)

        
            # Wordcloud
            lista_Comentario=[]
            for comentario in data:
                lista_Comentario.append(comentario['COMENTARIO'])
            text = " ".join(lista_Comentario)
            wordcloud = WordCloud(background_color="white", width=500, height=300, color_func=blue_red_color_func).generate(text)
            # Converter a imagem para bytes
            image_bytes = BytesIO()
            wordcloud.to_image().save(image_bytes, format='PNG')
            image_bytes.seek(0)
            wordcloud_image = base64.b64encode(image_bytes.getvalue()).decode()

            # Tabela com os últimos 5 casos
            latest_cases = sorted(data, key=lambda x: x['CREATED_AT'], reverse=True)[:5]

            # Gráfico
            complaint_counts = {}
            for element in data:
                complaint_type=element['TIPO_RECLAMACAO']
                complaint_counts[complaint_type] = complaint_counts.get(complaint_type, 0) + 1

            # Ordena as contagens do maior para o menor
            sorted_counts = sorted(complaint_counts.items(), key=lambda item: item[1], reverse=True)
            complaint_types = [item[0] for item in sorted_counts]
            complaint_values = [item[1] for item in sorted_counts]

            
            # Cria o gráfico de pizza
            fig, ax = plt.subplots(figsize=(9, 4), subplot_kw=dict(aspect="equal"))
            wedges, texts, autotexts = ax.pie(complaint_values, autopct=lambda pct: func(pct, complaint_values),
                                            textprops=dict(color="w"))
            
                        # Define as cores para cada fatia do gráfico
            cores = ['#a9191b', '#b23032', '#ba4749', '#c35e5f', '#cb7576','#d48c8d','#dda3a4','#e5babb']
            for i, wedge in enumerate(wedges):
                wedge.set_facecolor(cores[i % len(cores)])  # Define a cor da fatia
            
                        # Cria a legenda
            ax.legend(wedges, complaint_types,
                    title="Tipos de Reclamação",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.setp(autotexts, size=8, weight="bold")

            # Converte o gráfico para bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', transparent=True)
            buffer.seek(0)
            plot_pie = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.clf()  # Limpa a figura para evitar sobreposição em chamadas futuras

            
        else:
            sem_dados=True
            mapa = folium.Map(location=[-22.7392383,-47.3355843], zoom_start=10)
            image_path = os.path.join(app.root_path, 'static', 'Nuvem_Vazia.jpg')
            image_path = os.path.abspath(image_path) # Torna o caminho absoluto
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            wordcloud_image = base64.b64encode(image_bytes).decode()
            latest_cases=None 
            plot_pie=None

        return mapa, wordcloud_image, latest_cases, plot_pie, sem_dados
    except Exception as e:
        raise ValueError('Could not execute function gerar_dados_dashboard - Error '+str(e))
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')


# Rota para buscar ruas de um bairro
@app.route('/buscar_ruas')
def buscar_ruas():
    try:
        conn=open_conn()
        cursor = conn.cursor()
        bairro = request.args.get('bairro')
        cursor.execute("SELECT DISTINCT RUA FROM defaultdb.LOCATIONS WHERE BAIRRO=%s ORDER BY RUA ASC", (bairro,))
        ruas = [row['RUA'] for row in cursor.fetchall()]
        return jsonify(ruas)
    except Exception as e:
        raise ValueError('Could not execute function buscar_ruas - Error '+str(e))
    finally:
        conn.close()



# Rota para o formulário de reclamação
@app.route('/formulario')
def formulario():
    try:
        conn=open_conn()
        cursor = conn.cursor()
        cursor.execute("Select distinct BAIRRO from defaultdb.LOCATIONS order by BAIRRO ASC;")
        bairros = [row['BAIRRO'] for row in cursor.fetchall()]
        return render_template('form.html', bairros=bairros)
    except Exception as e:
        raise ValueError('Could not execute function formulario - Error '+str(e))
    finally:
        conn.close()


# Rota para submeter a reclamação
@app.route('/submeter', methods=['POST'])
def submeter():
    try:
        conn=open_conn()
        cursor = conn.cursor()
        rua = request.form['rua']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        categoria = request.form['categoria']
        descricao = request.form['descricao']
        cursor.execute("INSERT INTO defaultdb.USERINPUT (RUA, BAIRRO, CIDADE, TIPO_RECLAMACAO, COMENTARIO) VALUES (%s, %s, %s, %s,%s)", (rua, bairro, cidade, categoria, descricao))
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id= cursor.fetchall()
        return jsonify({"mensagem": "Reclamação registrada com sucesso! - Seu Ticket # é "+str(last_inserted_id[0]['LAST_INSERT_ID()'])})
    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})
    finally:
        conn.close()

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    try:
        mapa, wordcloud_image, latest_cases, fig_bar,sem_dados = gerar_dados_dashboard()
        if sem_dados==False:
            return render_template('dashboard.html', 
                                mapa=mapa._repr_html_(),
                                wordcloud_image=wordcloud_image,
                                latest_cases=latest_cases,
                                plot_bar=fig_bar)
        else:
            return render_template('dashboard.html', 
                mapa=mapa._repr_html_(),
                wordcloud_image=wordcloud_image)
    except Exception as e:
        raise ValueError('Could not execute function dashboard - Error '+str(e))

# Rota para o encerrar reclamação
@app.route('/encerrar')
def encerrarTicket():
    return render_template('encerrar.html')


# Rota para encerrar ticket a reclamação
@app.route('/encerrarTicket', methods=['POST'])
def submeterEncerrarTicket():
    try:
        conn=open_conn()
        ticket = request.form['ticketReclamacao']
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM defaultdb.USERINPUT WHERE ID = %s AND RESOLVIDO is null" , (ticket,))
        IDs=cursor.fetchall()
        if len(IDs)!=0:
            cursor.execute("UPDATE defaultdb.USERINPUT SET RESOLVIDO=True WHERE ID = %s AND RESOLVIDO is null" , (ticket,))
            conn.commit()
            return jsonify({"mensagem": "Reclamação Encerrada com sucesso!"})
        else:
            return jsonify({"mensagem": "Esse Ticket Não existe no sistema ou já foi fechado! Por favor verifique"})    
    except Exception as e:
        return jsonify({"mensagem": "Há um problema com o servidor. Lamentamos! - Código do erro : "+str(e)})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)