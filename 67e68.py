
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

np.random.seed(42)
n = 200

lojas = ['Loja Centro', 'Loja Norte', 'Loja Sul', 'Loja Shopping']
regioes_das_lojas = {'Loja Centro': 'Sudeste', 'Loja Norte': 'Norte',
                     'Loja Sul': 'Sul', 'Loja Shopping': 'Nordeste'}
produtos = ['Camiseta', 'Calça', 'Tênis', 'Bolsa', 'Boné', 'Jaqueta']
categorias_dos_produtos = {'Camiseta': 'Roupas', 'Calça': 'Roupas', 'Jaqueta': 'Roupas',
                           'Tênis': 'Calçados', 'Bolsa': 'Acessórios', 'Boné': 'Acessórios'}
precos = {'Camiseta': 40, 'Calça': 120, 'Tênis': 250, 'Bolsa': 180, 'Boné': 35, 'Jaqueta': 300}

datas = pd.date_range('2024-01-01', '2024-12-31')
lista_datas = np.random.choice(datas, n)
lista_lojas = np.random.choice(lojas, n)
lista_produtos = np.random.choice(produtos, n)
lista_quantidades = np.random.randint(1, 10, n)

dados = pd.DataFrame({
    'data': lista_datas,
    'loja': lista_lojas,
    'regiao': [regioes_das_lojas[l] for l in lista_lojas],
    'produto': lista_produtos,
    'categoria': [categorias_dos_produtos[p] for p in lista_produtos],
    'quantidade': lista_quantidades,
    'preco_unitario': [precos[p] + np.random.randint(-10, 10) for p in lista_produtos]
})

dados.loc[[5, 20, 50, 80], 'quantidade'] = np.nan
dados.loc[[10, 33, 90], 'preco_unitario'] = np.nan

dados.to_csv('vendas.csv', index=False)
df = pd.read_csv('vendas.csv')

df['data'] = pd.to_datetime(df['data'])

print('Primeiras linhas:')
print(df.head())

df['faturamento'] = df['quantidade'] * df['preco_unitario']

print('\n--- INFO ---')
print(df.info())

print('\n--- VALORES AUSENTES ---')
print(df.isnull().sum())

print('\n--- RESUMO ESTATÍSTICO ---')
print(df.describe())

media_preco = df['preco_unitario'].mean()
media_quantidade = df['quantidade'].mean()

df['preco_unitario'] = df['preco_unitario'].fillna(media_preco)
df['quantidade'] = df['quantidade'].fillna(media_quantidade)

df['faturamento'] = df['quantidade'] * df['preco_unitario']

print('\nValores nulos depois do tratamento:')
print(df.isnull().sum())

fat_loja = df.groupby('loja')['faturamento'].sum()
fat_loja = fat_loja.sort_values(ascending=False)
print('\n--- FATURAMENTO POR LOJA ---')
print(fat_loja)

num_vendas = df.groupby('loja')['faturamento'].count()
ticket_medio = fat_loja / num_vendas
print('\n--- TICKET MÉDIO POR LOJA ---')
print(ticket_medio)

top5 = df.groupby('produto')['quantidade'].sum()
top5 = top5.sort_values(ascending=False).head(5)
print('\n--- TOP 5 PRODUTOS MAIS VENDIDOS ---')
print(top5)

df['periodo'] = df['data'].dt.to_period('M')
fat_mensal = df.groupby('periodo')['faturamento'].sum()

mes_maior = fat_mensal.idxmax()
mes_menor = fat_mensal.idxmin()

print('\n--- MESES ---')
print('Maior faturamento:', mes_maior.strftime('%m/%Y'), '-', round(fat_mensal.max(), 2))
print('Menor faturamento:', mes_menor.strftime('%m/%Y'), '-', round(fat_mensal.min(), 2))

df['mes'] = df['data'].dt.month

sns.set_style('whitegrid')
sns.set_palette(sns.color_palette('deep'))

os.makedirs('graficos', exist_ok=True)

plt.figure(figsize=(8, 5))
plt.bar(fat_loja.index, fat_loja.values, color=['blue', 'green', 'orange', 'red'])
plt.title('Faturamento Total por Loja')
plt.xlabel('Loja')
plt.ylabel('Faturamento (R$)')
plt.savefig('faturamento_por_loja.png')
plt.savefig('graficos/faturamento_por_loja.png')
plt.show()

plt.figure(figsize=(10, 5))
meses = fat_mensal.index.strftime('%m/%Y')
plt.plot(meses, fat_mensal.values, marker='o', color='purple')

for i in range(len(meses)):
    plt.text(i, fat_mensal.values[i], str(int(fat_mensal.values[i])), ha='center', va='bottom', fontsize=8)

plt.title('Evolução Mensal do Faturamento em 2024')
plt.xlabel('Mês/Ano')
plt.ylabel('Faturamento (R$)')
plt.xticks(rotation=45)
plt.savefig('graficos/evolucao_mensal.png')
plt.show()

fat_regiao = df.groupby('regiao')['faturamento'].sum()

plt.figure(figsize=(7, 7))
plt.pie(fat_regiao.values, labels=fat_regiao.index, autopct='%1.1f%%',
        colors=['gold', 'lightcoral', 'skyblue', 'lightgreen'])
plt.title('Distribuição do Faturamento por Região')
plt.savefig('graficos/pizza_regiao.png')
plt.show()

plt.figure(figsize=(8, 5))
sns.scatterplot(x='quantidade', y='faturamento', data=df)
plt.title('Relação entre Quantidade Vendida e Faturamento')
plt.xlabel('Quantidade de itens')
plt.ylabel('Faturamento (R$)')
plt.savefig('graficos/dispersao_qtd_faturamento.png')
plt.show()

plt.figure(figsize=(8, 5))
sns.boxplot(x='categoria', y='preco_unitario', hue='categoria', data=df, legend=False)
plt.title('Distribuição dos Preços Unitários por Categoria')
plt.xlabel('Categoria do produto')
plt.ylabel('Preço unitário (R$)')
plt.savefig('graficos/boxplot_preco_categoria.png')
plt.show()

colunas_numericas = df[['quantidade', 'preco_unitario', 'faturamento', 'mes']]
correlacao = colunas_numericas.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlacao, annot=True, cmap='coolwarm')
plt.title('Correlação entre as Variáveis Numéricas')
plt.savefig('graficos/heatmap_correlacao.png')
plt.show()

plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.bar(fat_loja.index, fat_loja.values, color='steelblue')
plt.title('Faturamento por Loja')
plt.xlabel('Loja')
plt.ylabel('Faturamento (R$)')
plt.xticks(rotation=30)

plt.subplot(1, 2, 2)
plt.bar(fat_regiao.index, fat_regiao.values, color='seagreen')
plt.title('Faturamento por Região')
plt.xlabel('Região')
plt.ylabel('Faturamento (R$)')

plt.tight_layout()
plt.savefig('graficos/comparacao_loja_regiao.png')
plt.show()

resumo = pd.DataFrame({
    'faturamento_total': fat_loja,
    'ticket_medio': ticket_medio
})
resumo.to_csv('resumo_analitico.csv')
print('\n--- RESUMO ANALÍTICO ---')
print(resumo)

print('\nPronto! Gráficos salvos na pasta graficos/')
