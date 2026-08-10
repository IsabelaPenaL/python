# ==============================================================
# APP.PY - Painel de Controle de Tarefas (versão simples)
# ==============================================================
# Este é um projeto Flask básico com:
# - Login / Registro / Logout
# - CRUD de tarefas (Criar, Ler, Editar, Excluir)
# - Banco de dados SQLite
# - Bootstrap 5 para o visual
# - Modo escuro simples
# ==============================================================

# ---- 1. IMPORTAÇÕES ----
# Aqui trazemos as ferramentas que vamos usar no projeto.
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---- 2. CONFIGURAÇÃO DO APP ----
app = Flask(__name__)

# A SECRET_KEY é usada pelo Flask para proteger a sessão do usuário
# (ela criptografa o "cookie" que guarda se o usuário está logado).
# Em um projeto real, isso ficaria escondido (variável de ambiente),
# mas aqui deixamos simples para fins didáticos.
app.secret_key = "chave-secreta-para-aprender-flask"

# Nome do arquivo do banco de dados SQLite
NOME_BANCO = "banco.db"


# ---- 3. FUNÇÃO PARA CONECTAR AO BANCO ----
def conectar_banco():
    """
    Abre uma conexão com o banco de dados SQLite.
    row_factory faz com que os resultados venham como um "dicionário",
    assim conseguimos acessar os dados pelo nome da coluna (ex: tarefa["titulo"]).
    """
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


# ---- 4. FUNÇÃO PARA CRIAR AS TABELAS (SE AINDA NÃO EXISTIREM) ----
def criar_tabelas():
    """
    Cria as tabelas 'usuarios' e 'tarefas' no banco, caso elas não existam.
    Rodamos essa função uma vez, sempre que o app inicia.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Tabela de usuários: id, nome, email, senha (criptografada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)

    # Tabela de tarefas: id, titulo, descricao, status, usuario_id (dono da tarefa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conexao.commit()
    conexao.close()


# ---- 5. FUNÇÃO "GUARDA" PARA PROTEGER ROTAS ----
def usuario_esta_logado():
    """
    Verifica se existe um usuario_id guardado na sessão.
    Se existir, quer dizer que o usuário já fez login.
    """
    return "usuario_id" in session


# ==============================================================
# ROTAS DE AUTENTICAÇÃO (REGISTRO, LOGIN, LOGOUT)
# ==============================================================

@app.route("/")
def index():
    """
    Página inicial. Se o usuário já estiver logado, manda para o dashboard.
    Se não, manda para a tela de login.
    """
    if usuario_esta_logado():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    """
    GET  -> mostra o formulário de cadastro
    POST -> recebe os dados do formulário e cria o usuário no banco
    """
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        # Nunca guardamos a senha "pura" no banco.
        # generate_password_hash transforma a senha em um código seguro.
        senha_criptografada = generate_password_hash(senha)

        conexao = conectar_banco()
        try:
            conexao.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_criptografada)
            )
            conexao.commit()
            flash("Conta criada com sucesso! Faça login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            # Isso acontece se o e-mail já existir (por causa do UNIQUE)
            flash("Esse e-mail já está cadastrado.", "danger")
        finally:
            conexao.close()

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  -> mostra o formulário de login
    POST -> confere email e senha e, se estiver certo, loga o usuário
    """
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar_banco()
        usuario = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conexao.close()

        # check_password_hash compara a senha digitada com a senha criptografada
        if usuario and check_password_hash(usuario["senha"], senha):
            # Guardamos o id e o nome do usuário na sessão (cookie seguro)
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            flash(f"Bem-vindo(a), {usuario['nome']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("E-mail ou senha incorretos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Remove os dados da sessão, "deslogando" o usuário.
    """
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))


# ==============================================================
# ROTAS DO CRUD DE TAREFAS
# ==============================================================

@app.route("/dashboard")
def dashboard():
    """
    Página principal, mostra todas as tarefas do usuário logado.
    """
    if not usuario_esta_logado():
        flash("Faça login para continuar.", "warning")
        return redirect(url_for("login"))

    conexao = conectar_banco()
    tarefas = conexao.execute(
        "SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC",
        (session["usuario_id"],)
    ).fetchall()
    conexao.close()

    # Contamos quantas tarefas existem de cada status, para mostrar um resumo simples
    total = len(tarefas)
    pendentes = len([t for t in tarefas if t["status"] == "pendente"])
    andamento = len([t for t in tarefas if t["status"] == "andamento"])
    concluidas = len([t for t in tarefas if t["status"] == "concluida"])

    return render_template(
        "dashboard.html",
        tarefas=tarefas,
        total=total,
        pendentes=pendentes,
        andamento=andamento,
        concluidas=concluidas
    )


@app.route("/nova_tarefa", methods=["GET", "POST"])
def nova_tarefa():
    """
    GET  -> mostra o formulário de nova tarefa
    POST -> salva a nova tarefa no banco
    """
    if not usuario_esta_logado():
        return redirect(url_for("login"))

    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        status = request.form["status"]

        conexao = conectar_banco()
        conexao.execute(
            "INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)",
            (titulo, descricao, status, session["usuario_id"])
        )
        conexao.commit()
        conexao.close()

        flash("Tarefa criada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    return render_template("nova_tarefa.html")


@app.route("/editar/<int:id_tarefa>", methods=["GET", "POST"])
def editar(id_tarefa):
    """
    GET  -> mostra o formulário já preenchido com os dados da tarefa
    POST -> atualiza a tarefa no banco
    """
    if not usuario_esta_logado():
        return redirect(url_for("login"))

    conexao = conectar_banco()

    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        status = request.form["status"]

        # O "AND usuario_id = ?" garante que um usuário só edite as PRÓPRIAS tarefas
        conexao.execute(
            """UPDATE tarefas SET titulo = ?, descricao = ?, status = ?
               WHERE id = ? AND usuario_id = ?""",
            (titulo, descricao, status, id_tarefa, session["usuario_id"])
        )
        conexao.commit()
        conexao.close()

        flash("Tarefa atualizada!", "success")
        return redirect(url_for("dashboard"))

    # Se for GET, buscamos a tarefa para preencher o formulário
    tarefa = conexao.execute(
        "SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id_tarefa, session["usuario_id"])
    ).fetchone()
    conexao.close()

    if tarefa is None:
        flash("Tarefa não encontrada.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("editar_tarefa.html", tarefa=tarefa)


@app.route("/excluir/<int:id_tarefa>")
def excluir(id_tarefa):
    """
    Remove a tarefa do banco de dados.
    Usamos GET aqui (via link/botão) para manter simples,
    mas o ideal em projetos maiores seria usar POST.
    """
    if not usuario_esta_logado():
        return redirect(url_for("login"))

    conexao = conectar_banco()
    conexao.execute(
        "DELETE FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id_tarefa, session["usuario_id"])
    )
    conexao.commit()
    conexao.close()

    flash("Tarefa excluída.", "info")
    return redirect(url_for("dashboard"))


# ==============================================================
# INICIANDO O APP
# ==============================================================
if __name__ == "__main__":
    # Só cria as tabelas se o arquivo do banco ainda não existir
    if not os.path.exists(NOME_BANCO):
        criar_tabelas()
    app.run(debug=True)
