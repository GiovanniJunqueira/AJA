import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_NAME = "nome_do_banco.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS propostas (
                      id INTEGER PRIMARY KEY,
                      nome_empresa TEXT,
                      cnpj TEXT,
                      operadora_plano TEXT,
                      data_implantacao DATE,
                      quantidade_vidas INTEGER,
                      valor_proposta REAL,
                      cpf_titular TEXT,
                      nome_corretor TEXT)''')
    conn.commit()
    conn.close()

def insert_proposta(nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO propostas (nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor))
    conn.commit()
    conn.close()

def get_propostas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM propostas')
    propostas = cursor.fetchall()
    conn.close()
    return propostas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cnpj = request.form['cnpj']
        operadora_plano = request.form['operadora_plano']
        data_implantacao = request.form['data_implantacao']
        quantidade_vidas = int(request.form['quantidade_vidas'])
        valor_proposta = float(request.form['valor_proposta'])
        cpf_titular = request.form['cpf_titular']
        nome_corretor = request.form['nome_corretor']

        insert_proposta(nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor)

        return redirect(url_for('index'))

    return render_template('registrar_proposta.html')

@app.route('/visualizar')
def visualizar():
    propostas = get_propostas()
    return render_template('visualizar_comissoes.html', propostas=propostas)

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
