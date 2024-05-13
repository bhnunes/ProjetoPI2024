import pymysql
import pandas as pd

file_path = r"D:\Usuario\Desktop\Projeto AVA\PI_2024\ProjetoPI2024\Research\Mapeamento_Americana.xlsx"
sheet_name = "MAPA_FINAL"
df = pd.read_excel(file_path, sheet_name=sheet_name)

timeout = 10
connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="mysql-pi2024-bruno-bc2b.j.aivencloud.com",
    password="AVNS_97Zi5DOuTtCkLgSB61k",
    read_timeout=timeout,
    port=11025,
    user="avnadmin",
    write_timeout=timeout,
)
cursor = connection.cursor()

try:
    batch_size = 1000  # Define o tamanho do lote
    rows_inserted = 0
    for index, row in df.iterrows():
        rua = str(row['Rua']).strip()
        bairro = str(row['Bairro']).strip()
        cidade = str(row['Cidade']).strip()
        cep = str(row['CEP']).strip()
        latitude = str(row['Latitude']).strip()
        longitude = str(row['Longitude']).strip()

        query = f"INSERT INTO LOCATIONS(RUA,BAIRRO,CIDADE,CEP,LATITUDE,LONGITUDE) VALUES ('{rua}', '{bairro}', '{cidade}', '{cep}', {latitude}, {longitude})"
        cursor.execute(query)

        rows_inserted += 1
        if rows_inserted % batch_size == 0:
            connection.commit()
            print(f"Committed {rows_inserted} rows.")

    # Commit any remaining rows
    if rows_inserted % batch_size != 0:
        connection.commit()
        print(f"Committed {rows_inserted} rows.")

    print("All rows inserted successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    connection.close()