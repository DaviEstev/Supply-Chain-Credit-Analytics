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