import sqlite3
import locale
import calendar
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

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
                      data_implantacao TEXT, 
                      quantidade_vidas INTEGER,
                      valor_proposta REAL,
                      cpf_titular TEXT,
                      nome_corretor TEXT)''')
    conn.commit()
    conn.close()

def insert_proposta(nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor):
    conn = connect_db()
    cursor = conn.cursor()

    if data_implantacao:
        data_implantacao = datetime.strptime(data_implantacao, "%Y-%m-%d").strftime("%Y-%m-%d")
    else:
        # Caso o campo esteja vazio, atribuímos None para a data_implantacao
        data_implantacao = None

    cursor.execute('''INSERT INTO propostas (nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (nome_empresa, cnpj, operadora_plano, data_implantacao, quantidade_vidas, valor_proposta, cpf_titular, nome_corretor))

    conn.commit()
    conn.close()

def limpar_tabela():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM propostas')
    conn.commit()
    conn.close()

def get_propostas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM propostas')
    propostas = cursor.fetchall()
    conn.close()
    return propostas

def get_comissoes():
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT nome_corretor, strftime("%Y-%m", data_implantacao) as mes, SUM(valor_proposta) FROM propostas GROUP BY nome_corretor, mes')
    comissoes = cursor.fetchall()

    # Converter a coluna "mes" em objetos datetime e obtenher o nome do mês em português
    comissoes = [(corretor, datetime.strptime(mes, "%Y-%m"), calendar.month_name[datetime.strptime(mes, "%Y-%m").month], total) for corretor, mes, total in comissoes]

    conn.close()
    return comissoes


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar_proposta():
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
def visualizar_comissoes():
    comissoes = get_comissoes()

    print("Dados de comissões:")
    for comissao in comissoes:
        print(comissao)

    return render_template('visualizar_comissoes.html', comissoes=comissoes)

@app.route('/detalhes_propostas/<string:nome_corretor>/<string:mes>')
def detalhes_propostas(nome_corretor, mes):
    # Converter a string de data em um objeto datetime
    mes_datetime = datetime.strptime(mes, "%Y-%m")

    # Obtenher o nome do mês em português
    mes_portugues = calendar.month_name[mes_datetime.month]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM propostas WHERE nome_corretor = ? AND strftime("%Y-%m", data_implantacao) = ?', (nome_corretor, mes))
    propostas = cursor.fetchall()
    conn.close()

    return render_template('detalhes_propostas.html', propostas=propostas, nome_corretor=nome_corretor, mes=mes_datetime, mes_portugues=mes_portugues)

@app.route('/limpar_tabela', methods=['POST'])
def limpar_tabela_view():
    limpar_tabela()
    return redirect(url_for('index'))


if __name__ == '__main__':
    create_table()

    # Adicione a opção 'host' para que o servidor seja acessível em outras máquinas na rede local
    app.run(debug=True, host='0.0.0.0')
