"""
fetch_data.py Ã¢ÂÂ versÃÂ£o multi-ano (2025 + 2026 + YoY)
Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
Baixa a planilha, separa por ANO, calcula todas as combinaÃÂ§ÃÂµes
de filtro por ano, e gera comparativo YoY (year-over-year).

Estrutura de saÃÂ­da do DATA:
  DATA["2026"]         Ã¢ÂÂ dados 2026 (all, jan, fev, mar, vendedores...)
  DATA["2025"]         Ã¢ÂÂ dados 2025 (all, jan..dez, vendedores...)
  DATA["compare"]      Ã¢ÂÂ comparativos YoY por mÃÂªs e por vendedor
  DATA["meta"]         Ã¢ÂÂ metadados: anos disponÃÂ­veis, meses, etc.

VARIÃÂVEIS DE AMBIENTE:
  SHEET_URL   Ã¢ÂÂ link de download da planilha (.xlsx)
  SHEET_TYPE  Ã¢ÂÂ "onedrive" | "google" | "url"
Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Ã¢ÂÂÃ¢ÂÂ CONFIGURAÃÂÃÂO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
SHEET_URL   = os.getenv("SHEET_URL", "")
SHEET_TYPE  = os.getenv("SHEET_TYPE", "onedrive")
HISTORY_DIR = Path(__file__).parent.parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)

# Ã¢ÂÂÃ¢ÂÂ NOMES EXATOS DAS COLUNAS (confirmados na planilha em 02/04/2026) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# Estrutura do arquivo: header na LINHA 6 (header=5 em pandas, 0-indexed)
# Abas: "CONTROLE DE VENDAS (2025)" e "CONTROLE DE VENDAS (2026)"
# Colunas: DATA DA VENDA | PACIENTE | TIPO | MODALIDADE | CONSULTA ONLINE |
#           ADICIONAL | VALOR | VENDEDOR | R$ COMISSÃÂO VENDEDOR | R$ COMISSÃÂO TREINO |
#           CÃÂD. INDICAÃÂÃÂO | HISTÃÂRICO
HEADER_ROW   = 5        # linha 6 da planilha = ÃÂ­ndice 5 em pandas (0-based)
SHEET_NAMES  = [
    "CONTROLE DE VENDAS (2025)",
    "CONTROLE DE VENDAS (2026)",
]

COL_MAP = {
    # Ã¢ÂÂÃ¢ÂÂ Data Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "data da venda":           "data",
    "data":                    "data",
    "dt":                      "data",
    "data venda":              "data",
    # Ã¢ÂÂÃ¢ÂÂ Vendedor Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "vendedor":                "vendedor",
    "vend":                    "vendedor",
    "nome vendedor":           "vendedor",
    # Ã¢ÂÂÃ¢ÂÂ Modalidade Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "modalidade":              "modalidade",
    "plano":                   "modalidade",
    "tipo de plano":           "modalidade",
    # Ã¢ÂÂÃ¢ÂÂ Valor Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "valor":                   "valor",
    "valor pago":              "valor",
    "receita":                 "valor",
    "valor total":             "valor",
    # Ã¢ÂÂÃ¢ÂÂ ComissÃÂ£o Vendedor (com e sem "R$") Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "r$ comissÃÂ£o vendedor":    "com_vend",   # Ã¢ÂÂ nome exato da planilha
    "r$ comissao vendedor":    "com_vend",
    "comissÃÂ£o vendedor":       "com_vend",
    "comissao vendedor":       "com_vend",
    "com. vendedor":           "com_vend",
    # Ã¢ÂÂÃ¢ÂÂ ComissÃÂ£o Treino (com e sem "R$") Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    "r$ comissÃÂ£o treino":      "com_treino", # Ã¢ÂÂ nome exato da planilha
    "r$ comissao treino":      "com_treino",
    "comissÃÂ£o treino":         "com_treino",
    "comissao treino":         "com_treino",
    "custo personal":          "com_treino",
    "com. treino":             "com_treino",
    "personal":                "com_treino",
}

MES_MAP   = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",
             7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
MES_LABEL = {"jan":"Janeiro","fev":"Fevereiro","mar":"MarÃÂ§o","abr":"Abril",
             "mai":"Maio","jun":"Junho","jul":"Julho","ago":"Agosto",
             "set":"Setembro","out":"Outubro","nov":"Novembro","dez":"Dezembro"}
MES_ORDER = list(MES_MAP.values())

# Vendedores detectados dinamicamente na planilha Ã¢ÂÂ nÃÂ£o mais hardcoded
# Os nomes abaixo sÃÂ£o usados como fallback para ordenaÃÂ§ÃÂ£o nos grÃÂ¡ficos
VENDORS_DISPLAY_ORDER = ["RAQUEL", "RAFAEL", "JUNIO", "DUDA"]
VENDORS_EXPECTED      = VENDORS_DISPLAY_ORDER  # serÃÂ¡ atualizado dinamicamente em build_data_object()
MODAIS_EXPECTED  = ["MENSAL", "TRIMESTRAL", "SEMESTRAL", "ANUAL", "BÃÂSICO", "DESAFIO", "VIP", "PREMIUM"]


# Ã¢ÂÂÃ¢ÂÂ DOWNLOAD Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def build_download_url(url: str, sheet_type: str) -> str:
    """
    Converte qualquer URL de compartilhamento do OneDrive/SharePoint
    para URL de download direto usando a API de shares do OneDrive.
    Suporta: 1drv.ms, onedrive.live.com, sharepoint.com
    """
    import base64 as _b64
    
    # Tenta converter para URL de download direto via API de shares
    try:
        encoded = _b64.b64encode(url.encode()).decode()
        encoded = 'u!' + encoded.rstrip('=').replace('+', '-').replace('/', '_')
        direct = f"https://api.onedrive.com/v1.0/shares/{encoded}/root/content"
        return direct
    except Exception:
        return url


def download_sheet(url: str, sheet_type: str) -> pd.DataFrame:
    """
    Baixa o XLSX e lÃÂª APENAS as abas de vendas (2025 e 2026),
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
    print(f"[fetch] Abas disponÃÂ­veis: {xl.sheet_names}")

    frames = []

    # 1ÃÂª tentativa: abas com nomes exatos confirmados na planilha
    for sheet_name in SHEET_NAMES:
        if sheet_name in xl.sheet_names:
            try:
                df = xl.parse(sheet_name, header=HEADER_ROW)
                df = df.dropna(how="all")
                if len(df) > 5:
                    frames.append(df)
                    print(f"[fetch]   Ã¢ÂÂ Aba '{sheet_name}': {len(df)} linhas")
            except Exception as e:
                print(f"[fetch]   Ã¢ÂÂ Aba '{sheet_name}': {e}")

    # 2ÃÂª tentativa: heurÃÂ­stica por nome (qualquer aba com "VENDAS" no nome)
    if not frames:
        print("[fetch] Nomes exatos nÃÂ£o encontrados Ã¢ÂÂ tentando heurÃÂ­stica...")
        for sheet in xl.sheet_names:
            if any(k in sheet.upper() for k in ["VENDAS", "VENDA", "SALES"]):
                try:
                    df = xl.parse(sheet, header=HEADER_ROW)
                    df = df.dropna(how="all")
                    if len(df) > 5:
                        frames.append(df)
                        print(f"[fetch]   Ã¢ÂÂ '{sheet}' (heurÃÂ­stica): {len(df)} linhas")
                except Exception:
                    pass

    # 3ÃÂº fallback: primeira aba com header=5
    if not frames:
        print("[fetch] Fallback: lendo primeira aba com header=5...")
        df = xl.parse(0, header=HEADER_ROW)
        df = df.dropna(how="all")
        frames.append(df)
        print(f"[fetch]   Ã¢ÂÂ Aba 0 (fallback): {len(df)} linhas")

    if not frames:
        raise RuntimeError("Nenhuma aba vÃÂ¡lida encontrada na planilha.")

    combined = pd.concat(frames, ignore_index=True)
    print(f"[fetch] Total: {len(combined)} linhas de {len(frames)} aba(s)")
    return combined


# Ã¢ÂÂÃ¢ÂÂ NORMALIZAÃÂÃÂO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).lower().strip() for c in df.columns]
    rename = {c: COL_MAP[c] for c in df.columns if c in COL_MAP}
    df = df.rename(columns=rename)

    # Checa colunas obrigatÃÂ³rias
    required = {"data", "vendedor", "modalidade", "valor"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas nÃÂ£o encontradas: {missing}\n"
            f"Colunas disponÃÂ­veis: {list(df.columns)}\n"
            f"Ajuste COL_MAP em fetch_data.py."
        )

    if "com_vend"   not in df.columns: df["com_vend"]   = 0.0
    if "com_treino" not in df.columns: df["com_treino"] = 0.0

    df["data"]       = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["valor"]      = pd.to_numeric(df["valor"],      errors="coerce").fillna(0)
    df["com_vend"]   = pd.to_numeric(df["com_vend"],   errors="coerce").fillna(0)
    df["com_treino"] = pd.to_numeric(df["com_treino"], errors="coerce").fillna(0)
    df["vendedor"]   = df["vendedor"].astype(str).str.upper().str.strip()
    df["modalidade"] = df["modalidade"].astype(str).str.upper().str.strip()

    df = df.dropna(subset=["data"]).query("valor > 0").copy()

    df["ano"]     = df["data"].dt.year.astype(str)
    df["mes_num"] = df["data"].dt.month
    df["mes"]     = df["mes_num"].map(MES_MAP)

    anos = sorted(df["ano"].unique())
    print(f"[fetch] Anos encontrados: {anos}")
    print(f"[fetch] {len(df)} registros vÃÂ¡lidos")
    return df


# Ã¢ÂÂÃ¢ÂÂ CÃÂLCULO POR BLOCO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def calc_block(sub: pd.DataFrame, ref_df: pd.DataFrame) -> dict:
    """Calcula KPIs e distribuiÃÂ§ÃÂµes para um subconjunto de dados."""
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
    ctreino = round(sub["com_treino"].sum())

    modal = {}
    for m in MODAIS_EXPECTED:
        s = sub[sub["modalidade"] == m]
        modal[m] = {"c": len(s), "v": round(s["valor"].sum())}

    vend = {}
    for v in VENDORS_EXPECTED:
        s  = sub[sub["vendedor"] == v]
        sv = round(s["valor"].sum())
        sc = len(s)
        vend[v] = {"c":sc,"v":sv,"tkt":round(sv/sc) if sc>0 else 0,
                   "cv":round(s["com_vend"].sum()),"ct":round(s["com_treino"].sum())}

    mes = {}
    for m in MES_ORDER:
        s = sub[sub["mes"] == m]
        mes[m] = {"c": len(s), "v": round(s["valor"].sum())}

    return {"n":n,"fat":fat,"tkt":tkt,"cvend":cvend,"ctreino":ctreino,
            "modal":modal,"vend":vend,"mes":mes}


# Ã¢ÂÂÃ¢ÂÂ COMPARATIVO YoY Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def calc_yoy(data_2025: dict, data_2026: dict) -> dict:
    """
    Gera comparativo year-over-year para cada mÃÂªs e para totais.
    Para cada mÃÂ©trica: valor 2025, valor 2026, variaÃÂ§ÃÂ£o % e absoluta.
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

    # Por mÃÂªs
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


# Ã¢ÂÂÃ¢ÂÂ BUILD COMPLETO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def build_data_object(df: pd.DataFrame) -> dict:
    """
    ConstrÃÂ³i DATA completo com todos os anos, combinaÃÂ§ÃÂµes e YoY.
    """
    global VENDORS_EXPECTED
    # Detecta vendedores presentes na planilha (pode incluir DUDA, novos, etc.)
    vendors_na_planilha = sorted(df["vendedor"].dropna().unique().tolist())
    # MantÃÂ©m ordem preferencial p/ grÃÂ¡ficos, depois adiciona novos ao final
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

        # Por mÃÂªs
        for m in MES_ORDER:
            sub = df_ano[df_ano["mes"] == m]
            ano_data[m] = calc_block(sub, df_ano)

        # Por vendedor
        for v in VENDORS_EXPECTED:
            vk  = v.lower()
            sub = df_ano[df_ano["vendedor"] == v]
            ano_data[vk] = calc_block(sub, df_ano)

        # Vendedor ÃÂ MÃÂªs
        for v in VENDORS_EXPECTED:
            for m in MES_ORDER:
                key = f"{v.lower()}_{m}"
                sub = df_ano[(df_ano["vendedor"]==v) & (df_ano["mes"]==m)]
                ano_data[key] = calc_block(sub, df_ano)

        data[ano] = ano_data
        print(f"[fetch] Ano {ano}: {len(df_ano)} registros ÃÂ· {len(ano_data)} combinaÃÂ§ÃÂµes")

    # Comparativo YoY (se hÃÂ¡ 2025 e 2026)
    if "2025" in data and "2026" in data:
        data["compare"] = calc_yoy(data["2025"], data["2026"])
        print(f"[fetch] Comparativo YoY calculado.")

    # Compat: mantÃÂ©m "all" no nÃÂ­vel raiz apontando para o ano mais recente
    latest = anos[-1]
    data["all"] = data[latest]["all"]

    return data


# Ã¢ÂÂÃ¢ÂÂ HISTÃÂRICO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

    # MantÃÂ©m os ÃÂºltimos 72 snapshots
    for old in sorted(HISTORY_DIR.glob("snapshot_*.json"))[:-72]:
        old.unlink()

    print(f"[fetch] HistÃÂ³rico salvo: {out.name}")
    return snapshot


# Ã¢ÂÂÃ¢ÂÂ MAIN Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def main() -> dict:
    if not SHEET_URL:
        raise EnvironmentError("SHEET_URL nÃÂ£o configurado!")

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
    }


if __name__ == "__main__":
    r = main()
    print(f"\nÃ¢ÂÂ Processado: {r['records']} registros ÃÂ· anos: {r['anos']} ÃÂ· fat: R$ {r['fat_total']:,.0f}")
