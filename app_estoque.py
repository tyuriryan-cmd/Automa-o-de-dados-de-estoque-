from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

ARQUIVO_ESTOQUE = "estoque_seu_joao.json"
ARQUIVO_HISTORICO = "historico_seu_joao.json"


# --- FUNÇÕES DE DADOS ---
def carregar_dados(arquivo, padrao):
  if os.path.exists(arquivo):
    with open(arquivo, "r", encoding="utf-8") as f:
      return json.load(f)
  return padrao


def salvar_dados(arquivo, dados):
  with open(arquivo, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)


# Carrega os dados existentes
estoque = carregar_dados(ARQUIVO_ESTOQUE, {})
historico = carregar_dados(ARQUIVO_HISTORICO, [])

# --- INTERFACE WEB (STREAMLIT) ---
st.set_page_config(
    page_title="Controle de Estoque - Seu João", page_icon="🛒", layout="wide"
)

st.title("🛒 Controle de Estoque - Seu João")
st.write("Gerencie seus produtos, visualize gráficos e acompanhe o histórico!")

# Menu lateral
menu = st.sidebar.selectbox(
    "Navegação",
    ["Painel Principal", "Cadastrar Produto", "Entrada/Saída", "Histórico"],
)

# 1. PAINEL PRINCIPAL
if menu == "Painel Principal":
  st.header("📊 Visão Geral do Estoque")

  if not estoque:
    st.info("Nenhum produto cadastrado ainda. Use a aba lateral para começar!")
  else:
    dados_tabela = []
    for prod, info in estoque.items():
      dados_tabela.append({
          "Produto": prod,
          "Quantidade": info["quantidade"],
          "Preço (R$)": info["preco"],
          "Valor Total (R$)": info["quantidade"] * info["preco"],
      })

    df = pd.DataFrame(dados_tabela)

    total_itens = df["Quantidade"].sum()
    valor_geral = df["Valor Total (R$)"].sum()

    col1, col2 = st.columns(2)
    col1.metric("📦 Total de Itens em Estoque", total_itens)
    col2.metric("💰 Valor Total Investido", f"R$ {valor_geral:.2f}")

    st.subheader("Tabela de Produtos")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Gráfico de Quantidade por Produto")
    st.bar_chart(df.set_index("Produto")["Quantidade"])

# 2. CADASTRAR PRODUTO
elif menu == "Cadastrar Produto":
  st.header("➕ Cadastrar Novo Produto")

  with st.form("form_cadastro"):
    nome = st.text_input("Nome do Produto").strip().capitalize()
    quantidade = st.number_input(
        "Quantidade Inicial", min_value=0, step=1, format="%d"
    )
    preco = st.number_input(
        "Preço Unitário (R$)", min_value=0.0, format="%.2f"
    )
    enviar = st.form_submit_button("Salvar Produto")

    if enviar:
      if not nome:
        st.warning("⚠️ O nome do produto não pode estar vazio.")
      elif nome in estoque:
        st.warning(f"⚠️ O produto '{nome}' já existe no estoque!")
      else:
        estoque[nome] = {"quantidade": int(quantidade), "preco": float(preco)}
        salvar_dados(ARQUIVO_ESTOQUE, estoque)

        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        historico.append({
            "Data": data_atual,
            "Produto": nome,
            "Movimentação": "Cadastro Inicial",
            "Quantidade": int(quantidade),
        })
        salvar_dados(ARQUIVO_HISTORICO, historico)

        st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")

# 3. ENTRADA E SAÍDA DE PRODUTOS
elif menu == "Entrada/Saída":
  st.header("🔄 Movimentação de Estoque")

  if not estoque:
    st.warning("Cadastre algum produto primeiro!")
  else:
    tipo_mov = st.selectbox(
        "Tipo de Movimentação", ["Entrada (Compra)", "Saída (Venda)"]
    )
    produto_escolhido = st.selectbox("Selecione o Produto", list(estoque.keys()))
    qtd_mov = st.number_input(
        "Quantidade", min_value=1, step=1, format="%d"
    )

    if st.button("Confirmar Movimentação"):
      data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

      if tipo_mov == "Entrada (Compra)":
        estoque[produto_escolhido]["quantidade"] += int(qtd_mov)
        historico.append({
            "Data": data_atual,
            "Produto": produto_escolhido,
            "Movimentação": "Entrada",
            "Quantidade": int(qtd_mov),
        })
        st.success(
            f"✅ Entrada registrada! Novo estoque de {produto_escolhido}:"
            f" {estoque[produto_escolhido]['quantidade']}"
        )
      else:
        estoque_atual = estoque[produto_escolhido]["quantidade"]
        if qtd_mov > estoque_atual:
          st.error(
              f"❌ Erro: Estoque insuficiente! Apenas {estoque_atual} unidades"
              " disponíveis."
          )
        else:
          estoque[produto_escolhido]["quantidade"] -= int(qtd_mov)
          historico.append({
              "Data": data_atual,
              "Produto": produto_escolhido,
              "Movimentação": "Saída (Venda)",
              "Quantidade": int(qtd_mov),
          })
          st.success(
              f"✅ Venda registrada! Novo estoque de {produto_escolhido}:"
              f" {estoque[produto_escolhido]['quantidade']}"
          )

      salvar_dados(ARQUIVO_ESTOQUE, estoque)
      salvar_dados(ARQUIVO_HISTORICO, historico)

# 4. HISTÓRICO COM DATAS
elif menu == "Histórico":
  st.header("📅 Histórico de Movimentações")

  if not historico:
    st.info("Nenhuma movimentação registrada ainda.")
  else:
    df_hist = pd.DataFrame(historico)
    st.dataframe(df_hist, use_container_width=True)
    
