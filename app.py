from flask import Flask, render_template_string, request

app = Flask(__name__)

usuarios = {
    "juan": "22401105",  
    "dolga": "cotemig2026",
    "janaina": "cotemig2026",
    "antonio": "cotemig2026"
}


html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
    <h2>Sistema de Login</h2>

    <form method="POST">
        <label>Usuário:</label><br>
        <input type="text" name="usuario"><br><br>

        <label>Senha:</label><br>
        <input type="password" name="senha"><br><br>

        <button type="submit">Entrar</button>
    </form>

    <h3>{{ mensagem }}</h3>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    mensagem = ""

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        acesso_liberado = False

        for nome, senha_correta in usuarios.items():
            if usuario == nome and senha == senha_correta:
                acesso_liberado = True
                break

        if acesso_liberado:
            mensagem = " Acesso permitido!"
        else:
            mensagem = " Usuário ou senha incorretos."

    return render_template_string(html, mensagem=mensagem)

if __name__ == "__main__":
    app.run(debug=True)