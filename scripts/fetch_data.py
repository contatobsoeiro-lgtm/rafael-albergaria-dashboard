"""
fetch_data.py — versão multi-ano (2025 + 2026 + YoY)
─────────────────────────────────────────────────────────────
Baixa a planilha, separa por ANO, calcula todas as combinações
de filtro por ano, e gera comparativo YoY (year-over-year).

Estrutura de saída do DATA:
  DATA["2026"]         → dados 2026 (all, jan, fev, mar, vendedores...)
  DATA["2025"]         → dados 2025 (all, jan..dez, vendedores...)
  DATA["compare"]      → comparativos YoY por mês e por vendedor
  DATA["meta"]         → metadados: anos disponíveis, meses, etc.

VARIÁVEIS DE AMBIENTE:
  SHEET_URL   → link de download da planilha (.xlsx)
  SHEET_TYPE  → "onedrive" | "google" | "url"
─────────────────────────────────────────────────────────────
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# ── CONFIGURAÇÃO ──────────────────────────────────────────────
SHEET_URL   = os.getenv("SHEET_URL", "")
SHEET_TYPE  = os.getenv("SHEET_TYPE", "onedrive")
HISTORY_DIR = Path(__file__).parent.parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)

# ── NOMES EXATOS DAS COLUNAS (confirmados na planilha em 02/04/2026) ──────────
# Estrutura do arquivo: header na LINHA 6 (header=5 em pandas, 0-indexed)
# Abas: "CONTROLE DE VENDAS (2025)" e "CONTROLE DE VENDAS (2026)"
# Colunas: DATA DA VENDA | PACIENTE | TIPO | MODALIDADE | CONSULTA ONLINE |
#           ADICIONAL | VALOR | VENDEDOR | R$ COMISSÃO VENDEDOR | R$ COMISSÃO TREINO |
#           CÓD. INDICAÇÃO | HISTÓRICO
HEADER_ROW   = 5        # linha 6 da planilha = índice 5 em pandas (0-based)
SHEET_NAMES  = [
    "CONTROLE DE VENDAS (2025)",
    "CONTROLE DE VENDAS (2026)",
]

COL_MAP = {
    # ── Data ──────────────────────────────────────────────────────
    "data da venda":           "data",
    "data":                    "data",
    "dt":                      "data",
    "data venda":              "data",
    # ── Vendedor ──────────────────────────────────────────────────
    "vendedor":                "vendedor",
    "vend":                    "vendedor",
    "nome vendedor":           "vendedor",
    # ── Modalidade ────────────────────────────────────────────────
    "modalidade":              "modalidade",
    "plano":                   "modalidade",
    "tipo de plano":           "modalidade",
    # ── Valor ─────────────────────────────────────────────────────
    "valor":                   "valor",
    "valor pago":              "valor",
    "receita":                 "valor",
    "valor total":             "valor",
    # ── Comissão Vendedor (com e sem "R$") ────────────────────────
    "r$ comissão vendedor":    "com_vend",   # ← nome exato da planilha
    "r$ comissao vendedor":    "com_vend",
    "comissão vendedor":       "com_vend",
    "comissao vendedor":       "com_vend",
    "com. vendedor":           "com_vend",
    # ── Comissão Treino (com e sem "R$") ──────────────────────────
    "r$ comissão treino":      "com_treino", # ← nome exato da planilha
    "r$ comissao treino":      "com_treino",
    "comissão treino":         "com_treino",
    "comissao treino":         "com_treino",
    "custo personal":          "com_treino",
    "com. treino":             "com_treino",
    "personal":                "com_treino",
}

MES_MAP   = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",
             7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
MES_LABEL = {"jan":"Janeiro","fev":"Fevereiro","mar":"Março","abr":"Abril",
             "mai":"Maio","jun":"Junho","jul":"Julho","ago":"Agosto",
             "set":"Setembro","out":"Outubro","nov":"Novembro","dez":"Dezembro"}
MES_ORDER = list(MES_MAP.values())

# Vendedores detectados dinamicamente na planilha — não mais hardcoded
# Os nomes abaixo são usados como fallback para ordenação nos gráficos
VENDORS_DISPLAY_ORDER = ["RAQUEL", "RAFAEL", "JUNIO", "DUDA"]
VENDORS_EXPECTED      = VENDORS_DISPLAY_ORDER  # será atualizado dinamicamente em build_data_object()
MODAIS_EXPECTED  = ["MENSAL", "TRIMESTRAL", "SEMESTRAL", "ANUAL", "BÁSICO", "DESAFIO", "VIP", "PREMIUM"]


# ── DOWNLOAD ──────────────────────────────────────────────────

def build_download_url(raw_url: str, sheet_type: str) -> str:
    """
    Converte links de compartilhamento em links de download direto.

    OneDrive: use o link gerado por Compartilhar → Copiar link (não o doc.aspx!)
    O link de compartilhamento tem formato: https://1drv.ms/x/... ou
    https://onedrive.live.com/:x:/...
    """
    if sheet_type == "onedrive":
        # Link de compartilhamento OneDrive pessoal (1drv.ms ou onedrive.live.com)
        if "1drv.ms" in raw_url:
            return raw_url  # será redirecionado automaticamente
        if "onedrive.live.com" in raw_url and "resid=" in raw_url:
            # Extrai resid e cid do URL de compartilhamento
            sep = "&" if "?" in raw_url else "?"
            if "download=1" not in raw_url:
                return raw_url + sep + "download=1"
        if "sharepoint.com" in raw_url:
            sep = "&" if "?" in raw_url else "?"
            return raw_url + sep + "download=1"
    elif sheet_type == "google":
        if "/edit" in raw_url:
            return raw_url.replace("/edit", "/export?format=xlsx")
        if "docs.google.com/spreadsheets" in raw_url and "export" not in raw_url:
            sheet_id = raw_url.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    return raw_url


def download_sheet(url: str, sheet_type: str) -> pd.DataFrame:
    """
    Baixa o XLSX e lê APENAS as abas de vendas (2025 e 2026),
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
    print(f"[fetch] Abas disponíveis: {xl.sheet_names}")

    frames = []

    # 1ª tentativa: abas com nomes exatos confirmados na planilha
    for sheet_name in SHEET_NAMES:
        if sheet_name in xl.sheet_names:
            try:
                df = xl.parse(sheet_name, header=HEADER_ROW)
                df = df.dropna(how="all")
                if len(df) > 5:
                    frames.append(df)
                    print(f"[fetch]   ✓ Aba '{sheet_name}': {len(df)} linhas")
            except Exception as e:
                print(f"[fetch]   ✗ Aba '{sheet_name}': {e}")

    # 2ª tentativa: heurística por nome (qualquer aba com "VENDAS" no nome)
    if not frames:
        print("[fetch] Nomes exatos não encontrados — tentando heurística...")
        for sheet in xl.sheet_names:
            if any(k in sheet.upper() for k in ["VENDAS", "VENDA", "SALES"]):
                try:
                    df = xl.parse(sheet, header=HEADER_ROW)
                    df = df.dropna(how="all")
                    if len(df) > 5:
                        frames.append(df)
                        print(f"[fetch]   ✓ '{sheet}' (heurística): {len(df)} linhas")
                except Exception:
                    pass

    # 3º fallback: primeira aba com header=5
    if not frames:
        print("[fetch] Fallback: lendo primeira aba com header=5...")
        df = xl.parse(0, header=HEADER_ROW)
        df = df.dropna(how="all")
        frames.append(df)
        print(f"[fetch]   ✓ Aba 0 (fallback): {len(df)} linhas")

    if not frames:
        raise RuntimeError("Nenhuma aba válida encontrada na planilha.")

    combined = pd.concat(frames, ignore_index=True)
    print(f"[fetch] Total: {len(combined)} linhas de {len(frames)} aba(s)")
    return combined


# ── NORMALIZAÇÃO ──────────────────────────────────────────────

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).lower().strip() for c in df.columns]
    rename = {c: COL_MAP[c] for c in df.columns if c in COL_MAP}
    df = df.rename(columns=rename)

    # Checa colunas obrigatórias
    required = {"data", "vendedor", "modalidade", "valor"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas não encontradas: {missing}\n"
            f"Colunas disponíveis: {list(df.columns)}\n"
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
    print(f"[fetch] {len(df)} registros válidos")
    return df


# ── CÁLCULO POR BLOCO ─────────────────────────────────────────

def calc_block(sub: pd.DataFrame, ref_df: pd.DataFrame) -> dict:
    """Calcula KPIs e distribuições para um subconjunto de dados."""
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
    for v in VE9ORS_EXPECTED:
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


# ── COMPARATIVO YoY ───────────────────────────────────────────

def calc_yoy(data_2025: dict, data_2026: dict) -> dict:
    """
    Gera comparativo year-over-year para cada mês e para totais.
    Para cada métrica: valor 2025, valor 2026, variação % e absoluta.
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

    # Por mês
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


# ── BUILD COMPLETO ────────────────────────────────────────────

def build_data_object(df: pd.DataFrame) -> dict:
    """
    Constrói DATA completo com todos os anos, combinações e YoY.
    """
    global VENDORS_EXPECTED
    # Detecta vendedores presentes na planilha (pode incluir DUDA, novos, etc.)
    vendors_na_planilha = sorted(df["vendedor"].dropna().unique().tolist())
    # Mantém ordem preferencial p/ gráficos, depois adiciona novos ao final
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

        # Por mês
        for m in MES_ORDER:
            sub = df_ano[df_ano["mes"] == m]
            ano_data[m] = calc_block(sub, df_ano)

        # Por vendedor
        for v in VENDORS_EXPECTED:
            vk  = v.lower()
            sub = df_ano[df_ano["vendedor"] == v]
            ano_data[vk] = calc_block(sub, df_ano)

        # Vendedor × Mês
        for v in VENDORS_EXPECTED:
            for m in MES_ORDER:
                key = f"{v.lower()}_{m}"
                sub = df_ano[(df_ano["vendedor"]==v) & (df_ano["mes"]==m)]
                ano_data[key] = calc_block(sub, df_ano)

        data[ano] = ano_data
        print(f"[fetch] Ano {ano}: {len(df_ano)} registros · {len(ano_data)} combinações")

    # Comparativo YoY (se há 2025 e 2026)
    if "2025" in data and "2026" in data:
        data["compare"] = calc_yoy(data["2025"], data["2026"])
        print(f"[fetch] Comparativo YoY calculado.")

    # Compat: mantém "all" no nível raiz apontando para o ano mais recente
    latest = anos[-1]
    data["all"] = data[latest]["all"]

    return data


# ── HISTÓRICO ─────────────────────────────────────────────────

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

    # Mantém os últimos 72 snapshots
    for old in sorted(HISTORY_DIR.glob("snapshot_*.json"))[:-72]:
        old.unlink()

    print(f"[fetch] Histórico salvo: {out.name}")
    return snapshot


# ── MAIN ──────────────────────────────────────────────────────

def main() -> dict:
    if not SHEET_URL:
        raise EnvironmentError("SHEET_URL não configurado!")

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
    print(f"\n✅ Processado: {r['records']} registros · anos: {r['anos']} · fat: R$ {r['fat_total']:,.0f}")
