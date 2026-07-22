"""
fetch_data.py ÃÂ¢ÃÂÃÂ versÃÂÃÂ£o multi-ano (2025 + 2026 + YoY)
ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
Baixa a planilha, separa por ANO, calcula todas as combinaÃÂÃÂ§ÃÂÃÂµes
de filtro por ano, e gera comparativo YoY (year-over-year).

Estrutura de saÃÂÃÂ­da do DATA:
  DATA["2026"]         ÃÂ¢ÃÂÃÂ dados 2026 (all, jan, fev, mar, vendedores...)
  DATA["2025"]         ÃÂ¢ÃÂÃÂ dados 2025 (all, jan..dez, vendedores...)
  DATA["compare"]      ÃÂ¢ÃÂÃÂ comparativos YoY por mÃÂÃÂªs e por vendedor
  DATA["meta"]         ÃÂ¢ÃÂÃÂ metadados: anos disponÃÂÃÂ­veis, meses, etc.

VARIÃÂÃÂVEIS DE AMBIENTE:
  SHEET_URL   ÃÂ¢ÃÂÃÂ link de download da planilha (.xlsx)
  SHEET_TYPE  ÃÂ¢ÃÂÃÂ "onedrive" | "google" | "url"
ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
"""

import os
import re
import json
import unicodedata
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ CONFIGURAÃÂÃÂÃÂÃÂO ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
SHEET_URL   = os.getenv("SHEET_URL", "")
SHEET_TYPE  = os.getenv("SHEET_TYPE", "google")
HISTORY_DIR = Path(__file__).parent.parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ NOMES EXATOS DAS COLUNAS (confirmados na planilha em 02/04/2026) ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
# Estrutura do arquivo: header na LINHA 6 (header=5 em pandas, 0-indexed)
# Abas: "CONTROLE DE VENDAS (2025)" e "CONTROLE DE VENDAS (2026)"
# Colunas: DATA DA VENDA | PACIENTE | TIPO | MODALIDADE | CONSULTA ONLINE |
#           ADICIONAL | VALOR | VENDEDOR | R$ COMISSÃÂÃÂO VENDEDOR | R$ COMISSÃÂÃÂO TREINO |
#           CÃÂÃÂD. INDICAÃÂÃÂÃÂÃÂO | HISTÃÂÃÂRICO
HEADER_ROW   = 0        # Google Sheets: header na linha 1 (index 0)
SHEET_NAMES  = [
    "Vendas",                       # Google Sheets (nova fonte)
    "CONTROLE DE VENDAS (2025)",    # Excel OneDrive (legado)
    "CONTROLE DE VENDAS (2026)",    # Excel OneDrive (legado)
]

COL_MAP = {
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Data ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "data da venda":           "data",
    "data":                    "data",
    "dt":                      "data",
    "data venda":              "data",
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Vendedor ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "vendedor":                "vendedor",
    "vend":                    "vendedor",
    "nome vendedor":           "vendedor",
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Modalidade ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "modalidade":              "modalidade",
    "plano":                   "modalidade",
    "tipo de plano":           "modalidade",
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Valor ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "valor":                   "valor",
    "valor pago":              "valor",
    "receita":                 "valor",
    "valor total":             "valor",
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ ComissÃÂÃÂ£o Vendedor (com e sem "R$") ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "r$ comissÃÂÃÂ£o vendedor":    "com_vend",   # ÃÂ¢ÃÂÃÂ nome exato da planilha
    "r$ comissao vendedor":    "com_vend",
    "comissÃÂÃÂ£o vendedor":       "com_vend",
    "comissao vendedor":       "com_vend",
    "com. vendedor":           "com_vend",
    # ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ ComissÃÂÃÂ£o Treino (com e sem "R$") ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    "r$ comissÃÂÃÂ£o treino":      "com_treino", # ÃÂ¢ÃÂÃÂ nome exato da planilha
    "r$ comissao treino":      "com_treino",
    "comissÃÂÃÂ£o treino":         "com_treino",
    "comissao treino":         "com_treino",
    "custo personal":          "com_treino",
    "com. treino":             "com_treino",
    "personal":                "com_treino",
    "adicional":               "adicional",
    # Google Sheets: colunas com sufixo "(R$)"
    "valor (r$)":              "valor",
    "comissao vendedor (r$)":  "com_vend",
    "comissao treino (r$)":    "com_treino",
}

MES_MAP   = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",
             7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
MES_LABEL = {"jan":"Janeiro","fev":"Fevereiro","mar":"MarÃÂÃÂ§o","abr":"Abril",
             "mai":"Maio","jun":"Junho","jul":"Julho","ago":"Agosto",
             "set":"Setembro","out":"Outubro","nov":"Novembro","dez":"Dezembro"}
MES_ORDER = list(MES_MAP.values())

# Vendedores detectados dinamicamente na planilha ÃÂ¢ÃÂÃÂ nÃÂÃÂ£o mais hardcoded
# Os nomes abaixo sÃÂÃÂ£o usados como fallback para ordenaÃÂÃÂ§ÃÂÃÂ£o nos grÃÂÃÂ¡ficos
VENDORS_DISPLAY_ORDER = ["RAFAEL", "BIA", "SUPORTE", "VENDEDORES ANTIGOS"]

# Junio, Duda e Raquel sairam da equipe (jul/2026): o historico deles
# aparece unificado no dashboard como "VENDEDORES ANTIGOS"
VENDORS_QUE_SAIRAM = {"JUNIO", "DUDA", "RAQUEL"}
VENDORS_EXPECTED      = VENDORS_DISPLAY_ORDER  # serÃÂÃÂ¡ atualizado dinamicamente em build_data_object()
MODAIS_EXPECTED  = ["MENSAL", "TRIMESTRAL", "SEMESTRAL", "ANUAL", "BÃÂÃÂSICO", "DESAFIO", "VIP", "PREMIUM", "BASICO"]
MODAIS_EXPECTED  = [m for m in MODAIS_EXPECTED if m.isascii()]


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ DOWNLOAD ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def build_download_url(url: str, sheet_type: str) -> str:
    """
    Converte URL de compartilhamento para download direto.
    - OneDrive/SharePoint: adiciona ?download=1
    - Google Sheets (edit/view/sharing): extrai ID e gera URL de export XLSX
    """
    import re
    # Para links OneDrive/1drv.ms/SharePoint
    if any(x in url for x in ['1drv.ms', 'onedrive.live.com', 'sharepoint.com', 'my.sharepoint']):
        sep = '&' if '?' in url else '?'
        return url + sep + 'download=1'
    # Para links Google Sheets (edit, view, sharing)
    if 'docs.google.com/spreadsheets' in url:
        m = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
        if m:
            return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=xlsx"
    return url


def download_sheet(url: str, sheet_type: str) -> pd.DataFrame:
    """
    Baixa o XLSX e lÃÂÃÂª APENAS as abas de vendas (2025 e 2026),
    com header na linha 6 (header=5, 0-indexed) conforme estrutura da planilha.
    """
    download_url = build_download_url(url, sheet_type)
    print(f"[fetch] Baixando de: {download_url[:80]}...")

    resp = requests.get(download_url,
                        headers={"User-Agent": "DashboardBot/2.0"},
                        timeout=60, allow_redirects=True)
    resp.raise_for_status()

    tmp = HISTORY_DIR / "temp_sheet.xlsx"
    tmp.write_bytes(resp.content)
    print(f"[fetch] Baixado: {len(resp.content)/1024:.1f} KB")

    xl = pd.ExcelFile(tmp, engine="openpyxl")
    print(f"[fetch] Abas disponÃÂÃÂ­veis: {xl.sheet_names}")

    frames = []

    # 1ÃÂÃÂª tentativa: abas com nomes exatos confirmados na planilha
    for sheet_name in SHEET_NAMES:
        if sheet_name in xl.sheet_names:
            try:
                df = xl.parse(sheet_name, header=HEADER_ROW)
                df = df.dropna(how="all")
                if len(df) > 5:
                    frames.append(df)
                    print(f"[fetch]   ÃÂ¢ÃÂÃÂ Aba '{sheet_name}': {len(df)} linhas")
            except Exception as e:
                print(f"[fetch]   ÃÂ¢ÃÂÃÂ Aba '{sheet_name}': {e}")

    # 2ÃÂÃÂª tentativa: heurÃÂÃÂ­stica por nome (qualquer aba com "VENDAS" no nome)
    if not frames:
        print("[fetch] Nomes exatos nÃÂÃÂ£o encontrados ÃÂ¢ÃÂÃÂ tentando heurÃÂÃÂ­stica...")
        for sheet in xl.sheet_names:
            if any(k in sheet.upper() for k in ["VENDAS", "VENDA", "SALES"]):
                try:
                    df = xl.parse(sheet, header=HEADER_ROW)
                    df = df.dropna(how="all")
                    if len(df) > 5:
                        frames.append(df)
                        print(f"[fetch]   ÃÂ¢ÃÂÃÂ '{sheet}' (heurÃÂÃÂ­stica): {len(df)} linhas")
                except Exception:
                    pass

    # 3ÃÂÃÂº fallback: primeira aba com header=5
    if not frames:
        print("[fetch] Fallback: lendo primeira aba com header=5...")
        df = xl.parse(0, header=HEADER_ROW)
        df = df.dropna(how="all")
        frames.append(df)
        print(f"[fetch]   ÃÂ¢ÃÂÃÂ Aba 0 (fallback): {len(df)} linhas")

    if not frames:
        raise RuntimeError("Nenhuma aba vÃÂÃÂ¡lida encontrada na planilha.")

    combined = pd.concat(frames, ignore_index=True)
    print(f"[fetch] Total: {len(combined)} linhas de {len(frames)} aba(s)")
    return combined


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ NORMALIZAÃÂÃÂÃÂÃÂO ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def parse_valor_flex(x):
    """
    Converte valor em numero. Aceita float/int nativos e tambem texto
    digitado errado na planilha, tipo "R$1858,75" ou "R$ 1.197,00".
    Celula vazia vira 0. Texto ilegivel vira NaN (para gerar alerta).
    """
    if isinstance(x, (int, float)):
        return float(x) if not pd.isna(x) else 0.0
    s = str(x).strip()
    if not s or s.lower() in ("nan", "none", "-"):
        return 0.0
    s = re.sub(r"(?i)[r$\s ]", "", s)
    if "," in s:
        # formato brasileiro: ponto de milhar, virgula decimal
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        # so pontos de milhar, sem decimais: "1.197" significa 1197
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def parse_data_flex(x):
    """
    Converte data. Aceita datetime nativo, serial do Excel e texto,
    inclusive digitacao quebrada tipo "19/052026" (sem uma das barras).
    Ilegivel vira NaT (para gerar alerta).
    """
    if isinstance(x, (pd.Timestamp, datetime)):
        return pd.Timestamp(x)
    if isinstance(x, (int, float)):
        if pd.isna(x):
            return pd.NaT
        try:
            return pd.Timestamp("1899-12-30") + pd.Timedelta(days=float(x))
        except Exception:
            return pd.NaT
    s = str(x).strip()
    if not s or s.lower() == "nan":
        return pd.NaT
    d = pd.to_datetime(s, dayfirst=True, errors="coerce")
    if pd.isna(d):
        digitos = re.sub(r"\D", "", s)
        if len(digitos) == 8:
            d = pd.to_datetime(digitos, format="%d%m%Y", errors="coerce")
    return d


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [unicodedata.normalize('NFKD',str(c)).encode('ascii','ignore').decode('ascii').lower().strip() for c in df.columns]
    _cmap = {unicodedata.normalize('NFKD',k).encode('ascii','ignore').decode('ascii').lower().strip():v for k,v in COL_MAP.items()}
    rename = {c: _cmap[c] for c in df.columns if c in _cmap}
    df = df.rename(columns=rename)

    # Coluna de data sumiu pelo nome? Acontece quando mexem na tabela do Sheets
    # e o cabecalho vira "Coluna 1". Detecta automaticamente: coluna nao mapeada
    # em que a maioria dos valores vira data valida entre 2020 e 2035.
    if "data" not in df.columns:
        ja_mapeadas = set(rename.values())
        melhor, melhor_taxa = None, 0.0
        for c in df.columns:
            if c in ja_mapeadas:
                continue
            amostra = df[c].dropna().head(100)
            if len(amostra) < 5:
                continue
            conv = amostra.map(parse_data_flex)
            taxa = conv.map(lambda d: (not pd.isna(d)) and 2020 <= d.year <= 2035).mean()
            if taxa > melhor_taxa:
                melhor, melhor_taxa = c, taxa
        if melhor is not None and melhor_taxa >= 0.8:
            print(f"[fetch] AVISO: coluna de data nao encontrada pelo nome; "
                  f"usando '{melhor}' ({melhor_taxa:.0%} de datas validas). "
                  f"Renomear o cabecalho para 'Data' na planilha.")
            df = df.rename(columns={melhor: "data"})

    # Checa colunas obrigatÃÂÃÂ³rias
    required = {"data", "vendedor", "modalidade", "valor"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas nÃÂÃÂ£o encontradas: {missing}\n"
            f"Colunas disponÃÂÃÂ­veis: {list(df.columns)}\n"
            f"Ajuste COL_MAP em fetch_data.py."
        )

    if "com_vend"   not in df.columns: df["com_vend"]   = 0.0
    if "com_treino" not in df.columns: df["com_treino"] = 0.0
    if "adicional"  not in df.columns: df["adicional"]  = ""

    # Converte datas: aceita datetime nativo, strings ou seriais numéricos do Excel
    df["data"]       = pd.to_datetime(df["data"].map(parse_data_flex), errors="coerce")
    df["valor"]      = df["valor"].map(parse_valor_flex)
    df["com_vend"]   = df["com_vend"].map(parse_valor_flex).fillna(0)
    df["com_treino"] = df["com_treino"].map(parse_valor_flex).fillna(0)
    df["vendedor"]   = df["vendedor"].astype(str).str.upper().str.strip()
    df["vendedor"]   = df["vendedor"].map(lambda v: "VENDEDORES ANTIGOS" if v in VENDORS_QUE_SAIRAM else v)
    df["modalidade"] = df["modalidade"].astype(str).str.upper().str.strip().apply(lambda s: unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii'))

    # Linhas que serao descartadas por erro de digitacao: alertar em vez de sumir em silencio.
    # Valor 0 e legitimo (planos Wellts), por isso nao entra no alerta.
    _sem_data  = df["data"].isna()
    _sem_valor = df["valor"].isna()
    problemas = []
    for idx, row in df[_sem_data | _sem_valor].iterrows():
        paciente = str(row.get("paciente", "")).strip() or "(sem nome)"
        motivo   = "data ilegivel" if _sem_data.loc[idx] else "valor ilegivel"
        problemas.append(f"linha {idx + 2}: {paciente}, {motivo}")
    if problemas:
        print(f"[fetch] ATENCAO: {len(problemas)} linha(s) da planilha descartada(s) por erro de digitacao:")
        for p in problemas:
            print(f"[fetch]    - {p}")
    df["valor"] = df["valor"].fillna(0)

    df = df.dropna(subset=["data"]).query("valor > 0").copy()
    df.attrs["problemas"] = problemas

    df["ano"]     = df["data"].dt.year.astype(str)
    df["mes_num"] = df["data"].dt.month
    df["mes"]     = df["mes_num"].map(MES_MAP)

    anos = sorted(df["ano"].unique())
    print(f"[fetch] Anos encontrados: {anos}")
    print(f"[fetch] {len(df)} registros vÃÂÃÂ¡lidos")
    return df


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ CÃÂÃÂLCULO POR BLOCO ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def calc_block(sub: pd.DataFrame, ref_df: pd.DataFrame) -> dict:
    """Calcula KPIs e distribuiÃÂÃÂ§ÃÂÃÂµes para um subconjunto de dados."""
    if sub.empty:
        return {
            "n": 0, "fat": 0, "tkt": 0, "cvend": 0, "ctreino": 0,
            "modal": {m: {"c":0,"v":0} for m in MODAIS_EXPECTED},
            "vend":  {v: {"c":0,"v":0,"tkt":0,"cv":0,"ct":0} for v in VENDORS_EXPECTED},
            "mes":   {m: {"c":0,"v":0} for m in MES_ORDER},
        }

    n       = len(sub)
    fat     = round(sub["valor"].sum())
    tkt     = round(fat / n) if n > 0 else 0
    cvend   = round(sub["com_vend"].sum())
    # Custo Personal: 15% sobre planos com Adicional=Treino, EXCETO Plano Gustavo
    # (Plano Gustavo eh produto do parceiro, ele paga comissao pro Rafael, nao o contrario)
    _treino_mask = (
        (sub["adicional"].astype(str).str.upper().str.strip() == "TREINO") &
        (sub["tipo"].astype(str).str.strip().str.lower() != "plano gustavo")
    )
    ctreino = round(sub[_treino_mask]["com_treino"].sum())

    modal = {}
    for m in MODAIS_EXPECTED:
        s = sub[sub["modalidade"] == m]
        modal[m] = {"c": len(s), "v": round(s["valor"].sum())}

    vend = {}
    for v in VENDORS_EXPECTED:
        s  = sub[sub["vendedor"] == v]
        sv = round(s["valor"].sum())
        sc = len(s)
        # ct (com.treino do vendedor): mesma regra — exclui Plano Gustavo
        _ct_mask = (
            (s["adicional"].astype(str).str.upper().str.strip() == "TREINO") &
            (s["tipo"].astype(str).str.strip().str.lower() != "plano gustavo")
        )
        vend[v] = {"c":sc,"v":sv,"tkt":round(sv/sc) if sc>0 else 0,
                   "cv":round(s["com_vend"].sum()),"ct":round(s[_ct_mask]["com_treino"].sum())}

    mes = {}
    for m in MES_ORDER:
        s = sub[sub["mes"] == m]
        mes[m] = {"c": len(s), "v": round(s["valor"].sum())}

    return {"n":n,"fat":fat,"tkt":tkt,"cvend":cvend,"ctreino":ctreino,
            "modal":modal,"vend":vend,"mes":mes}


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ COMPARATIVO YoY ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def calc_yoy(data_2025: dict, data_2026: dict) -> dict:
    """
    Gera comparativo year-over-year para cada mÃÂÃÂªs e para totais.
    Para cada mÃÂÃÂ©trica: valor 2025, valor 2026, variaÃÂÃÂ§ÃÂÃÂ£o % e absoluta.
    """
    def diff(v26, v25):
        pct = round(((v26 - v25) / v25 * 100)) if v25 > 0 else None
        return {"v25": v25, "v26": v26, "delta": v26 - v25, "pct": pct}

    compare = {"mensal": {}, "total": {}}

    # Total geral
    d25 = data_2025.get("all", {})
    d26 = data_2026.get("all", {})
    compare["total"] = {
        "fat":     diff(d26.get("fat",0),     d25.get("fat",0)),
        "n":       diff(d26.get("n",0),       d25.get("n",0)),
        "tkt":     diff(d26.get("tkt",0),     d25.get("tkt",0)),
        "cvend":   diff(d26.get("cvend",0),   d25.get("cvend",0)),
        "ctreino": diff(d26.get("ctreino",0), d25.get("ctreino",0)),
    }

    # Por mÃÂÃÂªs
    for m in MES_ORDER:
        m25 = data_2025.get(m, {})
        m26 = data_2026.get(m, {})
        if m25.get("fat",0) == 0 and m26.get("fat",0) == 0:
            continue
        compare["mensal"][m] = {
            "fat": diff(m26.get("fat",0), m25.get("fat",0)),
            "n":   diff(m26.get("n",0),   m25.get("n",0)),
            "tkt": diff(m26.get("tkt",0), m25.get("tkt",0)),
        }

    # Por vendedor
    compare["vend"] = {}
    for v in VENDORS_EXPECTED:
        v25 = data_2025.get("all",{}).get("vend",{}).get(v,{})
        v26 = data_2026.get("all",{}).get("vend",{}).get(v,{})
        if v25.get("v",0) == 0 and v26.get("v",0) == 0:
            continue
        compare["vend"][v] = {
            "fat": diff(v26.get("v",0), v25.get("v",0)),
            "n":   diff(v26.get("c",0), v25.get("c",0)),
            "tkt": diff(v26.get("tkt",0), v25.get("tkt",0)),
        }

    return compare


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ BUILD COMPLETO ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def build_data_object(df: pd.DataFrame) -> dict:
    """
    ConstrÃÂÃÂ³i DATA completo com todos os anos, combinaÃÂÃÂ§ÃÂÃÂµes e YoY.
    """
    global VENDORS_EXPECTED
    # Detecta vendedores presentes na planilha (pode incluir DUDA, novos, etc.)
    vendors_na_planilha = sorted(df["vendedor"].dropna().unique().tolist())
    # MantÃÂÃÂ©m ordem preferencial p/ grÃÂÃÂ¡ficos, depois adiciona novos ao final
    VENDORS_EXPECTED = [v for v in VENDORS_DISPLAY_ORDER if v in vendors_na_planilha] + \
                       [v for v in vendors_na_planilha if v not in VENDORS_DISPLAY_ORDER]
    print(f"[fetch] Vendedores detectados: {VENDORS_EXPECTED}")

    anos = sorted(df["ano"].unique())
    data = {"meta": {"anos": anos, "meses_label": MES_LABEL, "vendors": VENDORS_EXPECTED}}

    for ano in anos:
        df_ano = df[df["ano"] == ano]
        ano_data = {}

        # Total do ano
        ano_data["all"] = calc_block(df_ano, df_ano)

        # Por mÃÂÃÂªs
        for m in MES_ORDER:
            sub = df_ano[df_ano["mes"] == m]
            ano_data[m] = calc_block(sub, df_ano)

        # Por vendedor
        for v in VENDORS_EXPECTED:
            vk  = v.lower()
            sub = df_ano[df_ano["vendedor"] == v]
            ano_data[vk] = calc_block(sub, df_ano)

        # Vendedor ÃÂÃÂ MÃÂÃÂªs
        for v in VENDORS_EXPECTED:
            for m in MES_ORDER:
                key = f"{v.lower()}_{m}"
                sub = df_ano[(df_ano["vendedor"]==v) & (df_ano["mes"]==m)]
                ano_data[key] = calc_block(sub, df_ano)

        data[ano] = ano_data
        print(f"[fetch] Ano {ano}: {len(df_ano)} registros ÃÂÃÂ· {len(ano_data)} combinaÃÂÃÂ§ÃÂÃÂµes")

    # Comparativo YoY (se hÃÂÃÂ¡ 2025 e 2026)
    if "2025" in data and "2026" in data:
        data["compare"] = calc_yoy(data["2025"], data["2026"])
        print(f"[fetch] Comparativo YoY calculado.")

    # Compat: mantÃÂÃÂ©m "all" no nÃÂÃÂ­vel raiz apontando para o ano mais recente
    latest = anos[-1]
    data["all"] = data[latest]["all"]

    return data


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ HISTÃÂÃÂRICO ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def save_history(data: dict, df: pd.DataFrame) -> dict:
    anos = sorted(df["ano"].unique())
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "records":   len(df),
        "anos":      anos,
        "fat_total": data["all"]["fat"],
        "data":      data,
    }
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = HISTORY_DIR / f"snapshot_{ts}.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    # MantÃÂÃÂ©m os ÃÂÃÂºltimos 72 snapshots
    for old in sorted(HISTORY_DIR.glob("snapshot_*.json"))[:-72]:
        old.unlink()

    print(f"[fetch] HistÃÂÃÂ³rico salvo: {out.name}")
    return snapshot


# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ MAIN ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ

def main() -> dict:
    if not SHEET_URL:
        raise EnvironmentError("SHEET_URL nÃÂÃÂ£o configurado!")

    df   = download_sheet(SHEET_URL, SHEET_TYPE)
    df   = normalize_df(df)
    data = build_data_object(df)
    snap = save_history(data, df)

    return {
        "data":      data,
        "records":   len(df),
        "timestamp": snap["timestamp"],
        "anos":      snap["anos"],
        "fat_total": snap["fat_total"],
        "problemas": df.attrs.get("problemas", []),
    }


if __name__ == "__main__":
    r = main()
    print(f"\nÃÂ¢ÃÂÃÂ Processado: {r['records']} registros ÃÂÃÂ· anos: {r['anos']} ÃÂÃÂ· fat: R$ {r['fat_total']:,.0f}")
