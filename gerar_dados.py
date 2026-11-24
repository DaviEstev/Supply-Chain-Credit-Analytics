import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

from pathlib import Path

# Identificar a pasta do projeto
pasta_projeto = Path(__file__).resolve().parent

# Definir a pasta dos arquivos CSV
pasta_dados = pasta_projeto / "data"

# Criar a pasta caso ela não exista
pasta_dados.mkdir(exist_ok=True)

# Definir o arquivo de destino
src_transacoes = pasta_dados / "transacoes.csv"
src_pagamentos = pasta_dados / "pagamentos.csv"
src_analise_fornecedores = pasta_dados / "analise_fornecedores.csv"
src_estoque = pasta_dados / "estoque.csv"

np.random.seed(42)
random.seed(42)

empresas = pd.DataFrame({
    "id_empresa": range(1, 11),
    "empresa": [
        "AutoNova Componentes",
        "MetalSul",
        "TechParts",
        "Rodas Brasil",
        "Eletrônica Alpha",
        "LogiFast",
        "Mecânica Forte",
        "PlastiCar",
        "SulCabos",
        "Motorsupply"
    ],
    "tipo": [
        "Fornecedor",
        "Fornecedor",
        "Fornecedor",
        "Fornecedor",
        "Fornecedor",
        "Logística",
        "Fornecedor",
        "Fornecedor",
        "Fornecedor",
        "Fornecedor"
    ],
    "setor": [
        "Autopeças",
        "Metalurgia",
        "Eletrônica",
        "Componentes",
        "Eletrônica",
        "Logística",
        "Mecânica",
        "Plásticos",
        "Elétrica",
        "Motores"
    ]
})

empresas["Faturamento_anual"] = np.random.uniform(
    10_000_000,
    100_000_000,
    len(empresas)
)

empresas["Porte"] = np.select(
    [
        empresas["Faturamento_anual"] >= 70_000_000,
        empresas["Faturamento_anual"] >= 30_000_000
    ],
    [
        "Grande",
        "Médio"
    ],
    default="Pequena"
)

empresas["cliente_principal"] = "AutoNova Automotive"

quantidade_transacoes = 10000
transacoes = []
data_inicio = datetime(2024, 1, 1)
data_fim = datetime(2025, 12, 31)

dias_periodo = (data_fim - data_inicio).days

fornecedores = empresas[
    empresas["tipo"] == "Fornecedor"
]

for i in range(quantidade_transacoes):
    fornecedor = fornecedores.sample(
        n=1,
        random_state=None
    ).iloc[0]

    data_transacao = data_inicio + timedelta(
        days=random.randint(0, dias_periodo)
    )

    valor = round(
        random.uniform(5_000, 100_000),
        2
    )

    transacoes.append({
        "id_transacao": i + 1,
        "data": data_transacao.strftime("%d-%m-%Y"),
        "id_fornecedor": fornecedor["id_empresa"],
        "nome_fornecedor": fornecedor["empresa"],
        "setor": fornecedor["setor"],
        "valor": valor
    })

df_transacoes = pd.DataFrame(transacoes)

df_transacoes.to_csv(
    pasta_dados / "transacoes.csv",
    index=False,
    encoding="utf-8-sig"
)

data_referencia = data_fim

pagamentos = []

for _, transacao in df_transacoes.iterrows():
    prazo = random.choice([30, 45, 60])
    data_transacao = pd.to_datetime(transacao["data"], dayfirst=True)
    data_vencimento = data_transacao + timedelta(days=prazo)
    data_pagamento = pd.NaT

    if data_vencimento > data_referencia:
        status = "A vencer"

    else:
        pagamento_realizado = random.random() < 0.85

        if pagamento_realizado:
            atraso_maximo = min(30, (data_referencia - data_vencimento).days)

            dias_atraso = random.randint(0, atraso_maximo)
            data_pagamento = (data_vencimento + timedelta(days=dias_atraso))

            if dias_atraso == 0:
                status = "Pago em dia"
            else:
                status = "Pago em atraso"

    pagamentos.append({
        "id_transacao": transacao["id_transacao"],
        "prazo_dias": prazo,
        "data_vencimento": data_vencimento,
        "data_pagamento": data_pagamento,
        "status_pagamento": status
    })

df_pagamentos = pd.DataFrame(pagamentos)

df_pagamentos["dias_atraso"] = (
    df_pagamentos["data_pagamento"] - df_pagamentos["data_vencimento"]
).dt.days

df_pagamentos["dias_atraso"] = (
    df_pagamentos["dias_atraso"].fillna(0).astype(int)
)

print(df_pagamentos.head(10))
print(df_pagamentos["status_pagamento"].value_counts())

df_pagamentos.to_csv(
    pasta_dados / "pagamentos.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Quantidade de pagamentos realizados em dia:", 
      int(df_pagamentos["status_pagamento"].value_counts().get("Pago em dia", 0)))

print("Quantidade de pagamentos realizados em atraso:", 
      int(df_pagamentos["status_pagamento"].value_counts().get("Pago em atraso", 0)))

print(
    "Quantidade de pagamentos realizados em atraso:",
    df_pagamentos["status_pagamento"].value_counts().get("Pago em atraso", 0)
)

media_atraso = df_pagamentos.loc[
    df_pagamentos["status_pagamento"] == "Pago em atraso",
    "dias_atraso"
].mean()

print(
    "Média de dias de atraso:", round(media_atraso, 2)
)

df_consolidado = pd.merge(
    df_transacoes,
    df_pagamentos,
    on="id_transacao",
    how="inner"
)

print(df_consolidado.head(10))

print("Total de transações:", len(df_transacoes))
print("Total de pagamentos:", len(df_pagamentos))
print("Total consolidado:", len(df_consolidado))

print("Colunas disponíveis:")
print(df_consolidado.columns.tolist())

analise_fornecedores = (
    df_consolidado.groupby("nome_fornecedor").agg(
        total_transacionado = ("valor","sum"),
        quantidade_transacoes = ("id_transacao","count"),
        media_dias_atraso = ("dias_atraso","mean")
    )
    .reset_index()
)

print(analise_fornecedores)

valor_pago_em_atraso = (
    df_consolidado[
        df_consolidado["status_pagamento"] == "Pago em atraso"
    ].groupby("nome_fornecedor")["valor"].sum()
)

valor_em_atraso = (
        df_consolidado[
        df_consolidado["status_pagamento"] == "Em atraso"
        ].groupby("nome_fornecedor")["valor"].sum()
)

analise_fornecedores["valor_pago_em_atraso"] = (
    analise_fornecedores["nome_fornecedor"].map(valor_pago_em_atraso).fillna(0)
)

analise_fornecedores["valor_em_atraso"] = (
    analise_fornecedores["nome_fornecedor"].map(valor_em_atraso).fillna(0)
)

print(analise_fornecedores)


maior_valor_transacionado_fornecedor = analise_fornecedores.loc[
    analise_fornecedores["total_transacionado"].idxmax()
]

print(
    "Fornecedor com maior valor transacionado:",
    maior_valor_transacionado_fornecedor["nome_fornecedor"],
    "com valor total de R$",
    round(maior_valor_transacionado_fornecedor["total_transacionado"], 2)
)

maior_valor_em_atraso = analise_fornecedores.loc[
    analise_fornecedores["valor_em_atraso"].idxmax()
]

print(
    "Fornecedor com maior valor em atraso:",
    maior_valor_em_atraso["nome_fornecedor"],
    "com valor total de R$",
    round(maior_valor_em_atraso["valor_em_atraso"], 2)
)

df_primeira_analise_fornecedores = pd.DataFrame(analise_fornecedores)

fornecedor_ordenado_valor_transacionado = df_primeira_analise_fornecedores.sort_values(
    by="total_transacionado",
    ascending=False
)

df_primeira_analise_fornecedores.to_csv(
    pasta_dados / "primeira_analise_fornecedores.csv",
    index=False,
    encoding="utf-8-sig"
)


produtos = [
    "Motor",
    "Sensor automotivo",
    "Cabo elétrico",
    "Roda",
    "Componente metálico",
    "Painel eletrônico",
    "Sistema de freio",
    "Filtro automotivo",
    "Peça plástica",
    "Componente hidráulico"
]


quantidade_registros = 5000

estoque = []

fornecedores = empresas[empresas["tipo"] == "Fornecedor"]

for i in range(quantidade_registros):
    fornecedor = fornecedores.sample(n=1).iloc[0]
    produto = random.choice(produtos)
    quantidade = random.randint(10, 10000)
    custo_unitario = round(random.uniform(10, 5000), 2)
    valor_estoque = round(quantidade * custo_unitario, 2)
    dias_estoque = random.randint(1, 180)

    estoque.append({
        "id_estoque": i + 1,
        "id_fornecedor": fornecedor["id_empresa"],
        "nome_fornecedor": fornecedor["empresa"],
        "produto": produto,
        "quantidade": quantidade,
        "custo_unitario": custo_unitario,
        "valor_estoque": valor_estoque,
        "dias_estoque": dias_estoque
    })

df_estoque = pd.DataFrame(estoque)

df_estoque.to_csv(
    pasta_dados / "estoque.csv",
    index=False,
    encoding="utf-8-sig"
)

valor_total_estoque = df_estoque["valor_estoque"].sum()
print("Valor total do estoque:", round(valor_total_estoque, 2))


estoque_fornecedor =( df_estoque.groupby("nome_fornecedor").agg(
    valor_total_estoque = ("valor_estoque", "sum"),
    quantidade_produtos = ("produto", "count"),
    media_dias_estoque = ("dias_estoque", "mean")
).reset_index()
)

estoque_parado = df_estoque[df_estoque["dias_estoque"] > 90]

print("Quantidade de produtos em estoque parado (mais de 90 dias):", len(estoque_parado))
print("Valor total do estoque parado (mais de 90 dias):", round(estoque_parado["valor_estoque"].sum(), 2))

fornecedor_maior_valor = df_estoque.groupby("nome_fornecedor")["valor_estoque"].sum().idxmax()
maior_valor_estoque = df_estoque.groupby("nome_fornecedor")["valor_estoque"].sum().max()

print("Fornecedor com maior valor em estoque:", fornecedor_maior_valor)
print("Maior valor em estoque:", round(maior_valor_estoque, 2))

produto_maior_qtd_armazenada = df_estoque.groupby("produto")["quantidade"].sum().idxmax()
qtd_maior_produto_armazenado = df_estoque.groupby("produto")["quantidade"].sum().max()

print("Produto com maior quantidade armazenada:", produto_maior_qtd_armazenada)
print("Quantidade armazenada do produto:", qtd_maior_produto_armazenado)


percentual_estoque_parado = (len(estoque_parado) / len(df_estoque)) * 100
print("Percentual de produtos em estoque parado (mais de 90 dias):", round(percentual_estoque_parado, 2), "%")

percentual_valor_estoque_parado = (estoque_parado["valor_estoque"].sum() / valor_total_estoque) * 100
print("Percentual do valor do estoque parado (mais de 90 dias):", round(percentual_valor_estoque_parado, 2), "%")
