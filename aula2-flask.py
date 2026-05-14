from flask import Flask, render_template_string

app = Flask(__name__)

# Dados extraídos do documento da Isabela
DADOS_CURRICULO = {
    "nome": "ISABELA PENA MOLINARI VIEIRA",
    "info": "16 ANOS | (31) 97143-0653 | bela.molinari8@gmail.com",
    "endereco": "Rua Paulista 801 Ap. 102 – Fernão Dias – BH/MG",
    "objetivos": [
        "Aprimorar o conhecimento na utilização do sistema operacional Windows",
        "Aperfeiçoar habilidades com aplicativos Windows",
        "Busco qualificação na área de informática para aperfeiçoamento do curso técnico"
    ],
    "formacao": [
        {"periodo": "2025 (Em andamento)", "desc": "COTEMIG - Técnico em Informática (2ª série)"},
        {"periodo": "2024", "desc": "COTEMIG - Técnico em Informática (1ª série)"},
        {"periodo": "2023", "desc": "COLÉGIO SANTA MARIA - Ensino Fundamental II"}
    ],
    "habilidades": [
        "Sistemas Windows e Plataformas Google",
        "Instalação e Configuração de Windows",
        "Pacote Office (Word, Excel e Power Point)"
    ],
    "qualificacoes": ["Inglês Intermediário", "Montagem e Configuração (MCC)", "Robótica"]
}

# Template HTML Integrado
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Currículo - {{ d.nome }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 20px; color: #333; background-color: #f4f4f9; }
        .cv-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { margin: 0; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .contato { color: #7f8c8d; margin-bottom: 20px; font-size: 0.9em; }
        h2 { color: #2980b9; font-size: 1.2em; text-transform: uppercase; margin-top: 30px; border-left: 4px solid #2980b9; padding-left: 10px; }
        ul { list-style-type: square; }
        li { margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="cv-card">
        <h1>{{ d.nome }}</h1>
        <div class="contato">
            <p>{{ d.info }}<br>{{ d.endereco }}</p>
        </div>

        <h2>Objetivos</h2>
        <ul>{% for obj in d.objetivos %}<li>{{ obj }}</li>{% endfor %}</ul>

        <h2>Formação</h2>
        {% for f in d.formacao %}<p><strong>{{ f.periodo }}:</strong> {{ f.desc }}</p>{% endfor %}

        <h2>Habilidades & Qualificações</h2>
        <ul>
            {% for h in d.habilidades %}<li>{{ h }}</li>{% endfor %}
            {% for q in d.qualificacoes %}<li>{{ q }}</li>{% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, d=DADOS_CURRICULO)

if __name__ == '__main__':
    # Rodar o comando 'pip install flask' antes de executar
    app.run(debug=True)
