"""
generate_html.py ÃÂ¢ÃÂÃÂ versÃÂÃÂ£o multi-ano (2025 + 2026 + YoY)
ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
Injeta o objeto DATA multi-ano no template HTML e:
  - Atualiza filtros de perÃÂÃÂ­odo e ano dinamicamente
  - Atualiza metadados (data, registros, rodapÃÂÃÂ©)
  - Preserva toda a lÃÂÃÂ³gica JS existente do dashboard
ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
"""

import re
import json
from datetime import datetime
from pathlib import Path

BASE_DIR      = Path(__file__).parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "dashboard.html"
OUTPUT_PATH   = BASE_DIR / "docs"      / "index.html"
OUTPUT_PATH.parent.mkdir(exist_ok=True)

MES_ORDER = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
MES_LABEL = {
    "jan":"Janeiro","fev":"Fevereiro","mar":"MarÃÂÃÂ§o","abr":"Abril",
    "mai":"Maio","jun":"Junho","jul":"Julho","ago":"Agosto",
    "set":"Setembro","out":"Outubro","nov":"Novembro","dez":"Dezembro"
}

# Regex para localizar o bloco const DATA = {...}
DATA_PATTERN = re.compile(
    r"(const DATA\s*=\s*)\{[\s\S]*?\n\};\s*\n",
    re.MULTILINE
)


def build_js_data(data: dict) -> str:
    """Serializa DATA para JS com formataÃÂÃÂ§ÃÂÃÂ£o legÃÂÃÂ­vel."""
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js = re.sub(r',(?="[^"]+":)', ',\n  ', js)
    return f"const DATA = {js[0]}\n  {js[1:-1]}\n{js[-1]};\n"


def inject_data(html: str, data: dict) -> str:
    """Substitui const DATA = {...} no HTML."""
    new_block = build_js_data(data)
    if DATA_PATTERN.search(html):
        return DATA_PATTERN.sub(new_block + "\n", html)
    # Fallback: injeta antes de ESTADO
    return html.replace(
        "// =====================================================================\n// ESTADO",
        new_block + "\n// =====================================================================\n// ESTADO"
    )


def update_year_filter(html: str, anos: list) -> str:
    """
    Injeta (ou atualiza) os botÃÂÃÂµes de filtro de ANO no HTML.
    Adiciona logo apÃÂÃÂ³s o bloco de filtros de mÃÂÃÂªs existente.
    """
    # Monta botÃÂÃÂµes de ano
    year_buttons = ['<button class="filter-btn active" data-ano="latest" onclick="setAno(\'latest\')">Atual</button>']
    for ano in sorted(anos, reverse=True):
        year_buttons.append(
            f'<button class="filter-btn" data-ano="{ano}" onclick="setAno(\'{ano}\')">{ano}</button>'
        )
    year_buttons.append(
        '<button class="filter-btn filter-btn-compare" data-ano="compare" onclick="setAno(\'compare\')">\U0001F4CA Comparar Anos</button>'
    )

    year_block = (
        '\n    <div class="filter-divider"></div>\n'
        '    <div class="filter-group" id="year-filter-group">\n'
        '      <span class="filter-label">Ano</span>\n'
        '      ' + "\n      ".join(year_buttons) + "\n"
        '    </div>'
    )

    # Substitui bloco de ano se jÃÂÃÂ¡ existir, senÃÂÃÂ£o insere antes do fechamento da filter-section
    if 'id="year-filter-group"' in html:
        html = re.sub(
            r'<div class="filter-group" id="year-filter-group">[\s\S]*?</div>',
            year_block.strip(),
            html
        )
    else:
        html = html.replace(
            '</div>\n</div>\n\n  <div class="kpi-grid">',
            year_block + '\n  </div>\n\n  <div class="kpi-grid">'
        )
    return html


def update_month_filter(html: str, data: dict, anos: list) -> str:
    """Atualiza botÃÂÃÂµes de mÃÂÃÂªs para os meses com dados (uniÃÂÃÂ£o de todos os anos)."""
    active_months = set()
    for ano in anos:
        for m in MES_ORDER:
            if data.get(ano, {}).get(m, {}).get("n", 0) > 0:
                active_months.add(m)

    buttons = ['<button class="filter-btn active" data-mes="all" onclick="setMes(\'all\')">Todos</button>']
    for m in MES_ORDER:
        if m in active_months:
            buttons.append(
                f'<button class="filter-btn" data-mes="{m}" onclick="setMes(\'{m}\')">{MES_LABEL[m]}</button>'
            )

    new_buttons = "\n      ".join(buttons)
    html = re.sub(
        r'(<span class="filter-label">Per[ÃÂÃÂ­i]odo</span>\s*)([\s\S]*?)(\s*</div>\s*<div class="filter-divider">)',
        lambda m: m.group(1) + "\n      " + new_buttons + "\n    " + m.group(3),
        html,
        count=1
    )
    return html


def update_meta(html: str, records: int, timestamp: str, anos: list) -> str:
    """Atualiza data, registros e rodapÃÂÃÂ©."""
    dt       = datetime.fromisoformat(timestamp)
    date_str = dt.strftime("%d/%m/%Y \u2014 dados reais")
    time_str = f"{records} registros \u00b7 {', '.join(sorted(anos))}"
    full_date = dt.strftime("%d/%m/%Y")
    anos_str  = " + ".join(sorted(anos))

    html = re.sub(r'(<strong id="updateDate">)[^<]*(</strong>)',
                  f'\\g<1>{date_str}\\g<2>', html)
    html = re.sub(r'(<span id="updateTime">)[^<]*(</span>)',
                  f'\\g<1>{time_str}\\g<2>', html)
    html = re.sub(r'(<strong id="footer-records">)[^<]*(</strong>)',
                  f'\\g<1>{records} registros \u00b7 {anos_str}\\g<2>', html)
    html = re.sub(r'(Ültima atualização: <strong>)[^<]*(</strong>)',
                  f'\\g<1>{full_date}\\g<2>', html)
    html = re.sub(r'(Controle de Vendas )\d{4}',
                  f'\\g<1>{anos_str}', html)
    return html


def inject_multiyear_js(html: str, anos: list) -> str:
    """
    Injeta/substitui a lÃÂÃÂ³gica JS de controle multi-ano no dashboard.
    Adiciona: activeAno, setAno(), getKey() compatÃÂÃÂ­vel com anos, seÃÂÃÂ§ÃÂÃÂ£o YoY.
    """
    latest = sorted(anos)[-1]

    js_multiyr = f"""
// =====================================================================
// CONTROLE MULTI-ANO ÃÂ¢ÃÂÃÂ {" + ".join(sorted(anos))}
// =====================================================================
let activeAno  = 'latest';   // 'latest' | '2025' | '2026' | 'compare'
let activeMes  = 'all';
let activeVend = 'all';

const ANOS_DISPONIVEIS = {json.dumps(sorted(anos))};
const LATEST_ANO = '{latest}';

function setAno(ano) {{
  activeAno = ano;
  document.querySelectorAll('[data-ano]').forEach(b =>
    b.classList.toggle('active', b.dataset.ano === ano));

  // No modo comparaÃÂÃÂ§ÃÂÃÂ£o, limpa filtros de mÃÂÃÂªs/vendedor
  if (ano === 'compare') {{
    activeMes  = 'all';
    activeVend = 'all';
    document.querySelectorAll('[data-mes]').forEach(b => b.classList.toggle('active', b.dataset.mes === 'all'));
    document.querySelectorAll('[data-vend]').forEach(b => b.classList.toggle('active', b.dataset.vend === 'all'));
    renderCompare();
    return;
  }}
  hideCompare();
  updateDashboard();
}}

function setMes(mes) {{
  activeMes = mes;
  document.querySelectorAll('[data-mes]').forEach(b =>
    b.classList.toggle('active', b.dataset.mes === mes));
  if (activeAno !== 'compare') updateDashboard();
}}

function setVend(vend) {{
  activeVend = vend;
  document.querySelectorAll('[data-vend]').forEach(b =>
    b.classList.toggle('active', b.dataset.vend === vend));
  if (activeAno !== 'compare') updateDashboard();
}}

function getAnoData() {{
  const ano = activeAno === 'latest' ? LATEST_ANO : activeAno;
  return DATA[ano] || DATA[LATEST_ANO] || {{}};
}}

function getKey() {{
  if (activeMes==='all' && activeVend==='all') return 'all';
  if (activeMes!=='all' && activeVend==='all') return activeMes;
  if (activeMes==='all' && activeVend!=='all') return activeVend;
  return activeVend + '_' + activeMes;
}}
"""

    # CSS para botÃÂÃÂ£o comparar
    css_compare = """
  .filter-btn-compare { border-color: #8b5cf6 !important; color: #7c3aed !important; }
  .filter-btn-compare.active { background: #8b5cf6 !important; border-color: #8b5cf6 !important; color: #fff !important; }
  #compare-section { display: none; }
  #compare-section.show { display: block; }
  .yoy-up   { color: #16a34a; font-weight: 700; }
  .yoy-down { color: #dc2626; font-weight: 700; }
  .yoy-neu  { color: #64748b; font-weight: 600; }
  .yoy-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .yoy-table th { font-size:11px; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:.4px; padding:8px 10px; border-bottom:2px solid var(--cinza-border); text-align:left; }
  .yoy-table td { padding:9px 10px; border-bottom:1px solid var(--cinza-border); }
  .yoy-table tbody tr:hover td { background:var(--cinza); }
"""

    # Injeta CSS
    html = html.replace("</style>", css_compare + "\n</style>", 1)

    # Injeta seÃÂÃÂ§ÃÂÃÂ£o HTML de comparaÃÂÃÂ§ÃÂÃÂ£o antes do rodapÃÂÃÂ©
    compare_section = """
<!-- ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
     SEÃÂÃÂÃÂÃÂO COMPARATIVO YoY (2025 vs 2026)
     ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ -->
<div id="compare-section" class="main" style="padding-top:0">
  <div class="section-header">
    <div class="section-header-title">ÃÂ°ÃÂÃÂÃÂ Comparativo 2025 vs 2026</div>
    <div class="section-header-sub">EvoluÃÂÃÂ§ÃÂÃÂ£o mensal ÃÂÃÂ· YoY por vendedor ÃÂÃÂ· Crescimento</div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Faturamento por MÃÂÃÂªs ÃÂ¢ÃÂÃÂ 2025 vs 2026</div>
      <div class="chart-sub">ComparaÃÂÃÂ§ÃÂÃÂ£o mÃÂÃÂªs a mÃÂÃÂªs dos dois anos</div>
      <div class="chart-wrap h260"><canvas id="chartYoY"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Crescimento YoY por MÃÂÃÂªs</div>
      <div class="chart-sub">VariaÃÂÃÂ§ÃÂÃÂ£o percentual mÃÂÃÂªs a mÃÂÃÂªs (%)</div>
      <div id="yoy-mes-table-wrap"></div>
    </div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Vendedores ÃÂ¢ÃÂÃÂ 2025 vs 2026</div>
      <div class="chart-sub">Faturamento total por vendedor em cada ano</div>
      <div id="yoy-vend-table-wrap"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">KPIs Gerais ÃÂ¢ÃÂÃÂ EvoluÃÂÃÂ§ÃÂÃÂ£o Anual</div>
      <div class="chart-sub">Totais consolidados dos dois anos</div>
      <div id="yoy-kpi-wrap"></div>
    </div>
  </div>
</div>
"""
    html = html.replace('<div class="footer">', compare_section + '\n<div class="footer">', 1)

    # Injeta JS multi-ano substituindo os blocos antigos de setMes/setVend/getKey
    html = re.sub(
        r'// ={5,}\s*\n// ESTADO[\s\S]*?// ={5,}\s*\n// CHARTS',
        js_multiyr + "\n// =====================================================================\n// CHARTS",
        html,
        count=1
    )

    # Substitui getKey() e setMes/setVend se ainda existirem como funÃÂÃÂ§ÃÂÃÂµes isoladas
    for fn in ["function setMes", "function setVend", "function getKey"]:
        html = re.sub(rf'{fn}\s*\([^)]*\)\s*\{{[\s\S]*?\n\}}', '', html)

    # Injeta chart YoY e funÃÂÃÂ§ÃÂÃÂµes renderCompare/hideCompare antes do fechamento do script
    yoy_js = """
// =====================================================================
// DASHBOARD MULTI-ANO ÃÂ¢ÃÂÃÂ lÃÂÃÂ³gica de rendering
// =====================================================================

// Lista de vendedores dinÃÂÃÂ¢mica (vem do Python via DATA.meta.vendors)
const VENDORS_LIST = (DATA.meta && DATA.meta.vendors) ? DATA.meta.vendors : ['RAQUEL','RAFAEL','JUNIO'];

// Paleta de cores para vendedores extras (alÃÂÃÂ©m dos 3 originais)
const EXTRA_COLORS = ['#8b5cf6','#ec4899','#14b8a6','#f97316','#64748b','#ef4444'];
VENDORS_LIST.forEach((v, i) => {
  if (!VEND_COLORS[v]) VEND_COLORS[v] = EXTRA_COLORS[i % EXTRA_COLORS.length];
  if (!VEND_NAMES[v])  VEND_NAMES[v]  = v.charAt(0) + v.slice(1).toLowerCase();
});

// Substitui updateDashboard para usar dados do ano ativo
const _origUpdateDashboard = updateDashboard;
function updateDashboard() {
  if (activeAno === 'compare') { renderCompare(); return; }
  const anoData = getAnoData();
  const key = getKey();
  const d = anoData[key] || anoData['all'] || {};

  if (!d || Object.keys(d).length === 0) return;

  // KPIs
  document.getElementById('kpi-fat').textContent      = 'R$ ' + fmt(d.fat || 0);
  document.getElementById('kpi-vendas').textContent   = d.n || 0;
  document.getElementById('kpi-ticket').textContent   = d.tkt ? 'R$ ' + fmt(d.tkt) : 'ÃÂ¢ÃÂÃÂ';
  const margem    = (d.fat||0) - (d.cvend||0) - (d.ctreino||0);
  const margemPct = d.fat > 0 ? Math.round(margem/d.fat*100) : 0;
  document.getElementById('kpi-margem').textContent     = 'R$ ' + fmt(margem);
  document.getElementById('kpi-margem-pct-val').textContent = margemPct + '%';
  document.getElementById('kpi-cvend-card').textContent = 'R$ ' + fmt(d.cvend||0);
  document.getElementById('kpi-personal').textContent   = 'R$ ' + fmt(d.ctreino||0);

  const ano    = activeAno === 'latest' ? LATEST_ANO : activeAno;
  const mesLbl = {all:ano+' acumulado',jan:'Jan '+ano,fev:'Fev '+ano,mar:'Mar '+ano,
                  abr:'Abr '+ano,mai:'Mai '+ano,jun:'Jun '+ano,jul:'Jul '+ano,
                  ago:'Ago '+ano,set:'Set '+ano,out:'Out '+ano,nov:'Nov '+ano,dez:'Dez '+ano};
  // Gera mapeamento vendÃÂ¢ÃÂÃÂ²label dinamicamente
  const vLblMap = {all:''};
  VENDORS_LIST.forEach(v => { vLblMap[v.toLowerCase()] = ' ÃÂÃÂ· ' + v.charAt(0) + v.slice(1).toLowerCase(); });
  document.getElementById('kpi-fat-badge').textContent = (mesLbl[activeMes]||ano) + (vLblMap[activeVend]||'');

  // Meses com dados
  const mesKeys = Object.keys(d.mes||{}).filter(m => (d.mes[m].v||0) > 0);
  const mesVals = mesKeys.map(m => d.mes[m].v);
  const mesLbls = mesKeys.map(m => ({jan:'Jan',fev:'Fev',mar:'Mar',abr:'Abr',mai:'Mai',jun:'Jun',jul:'Jul',ago:'Ago',set:'Set',out:'Out',nov:'Nov',dez:'Dez'}[m]||m));

  chartMes.data.labels   = mesLbls;
  chartMes.data.datasets[0].data = mesVals;
  chartMes.data.datasets[0].backgroundColor = mesLbls.map((_,i)=>['rgba(34,197,94,.85)','rgba(59,130,246,.85)','rgba(245,158,11,.85)','rgba(139,92,246,.85)','rgba(236,72,153,.85)','rgba(20,184,166,.85)'][i%6]);
  chartMes.update();

  chartModal.data.datasets[0].data = ['MENSAL','TRIMESTRAL','SEMESTRAL','ANUAL'].map(m=>(d.modal&&d.modal[m])?d.modal[m].c:0);
  chartModal.update();

  chartVend.data.labels = VENDORS_LIST;
  chartVend.data.datasets[0].data = VENDORS_LIST.map(v=>(d.vend&&d.vend[v])?d.vend[v].v:0);
  chartVend.update();

  chartTicket.data.labels = VENDORS_LIST;
  chartTicket.data.datasets[0].data = VENDORS_LIST.map(v=>(d.vend&&d.vend[v]&&d.vend[v].tkt)?d.vend[v].tkt:0);
  chartTicket.update();

  // ComissÃÂÃÂµes ÃÂ¢ÃÂÃÂ todos os vendedores dinÃÂÃÂ¢micos
  let totN=0,totV=0,totCv=0,totCt=0, rows='';
  VENDORS_LIST.forEach(v=>{
    const vd=(d.vend&&d.vend[v]);
    if(!vd||vd.c===0) return;
    totN+=vd.c;totV+=vd.v;totCv+=vd.cv;totCt+=vd.ct;
    const cor = VEND_COLORS[v] || '#94a3b8';
    const nome = VEND_NAMES[v] || (v.charAt(0) + v.slice(1).toLowerCase());
    rows+=`<tr>
      <td><span class="vend-badge"><span class="vend-dot" style="background:${cor}"></span>${nome}</span></td>
      <td>${vd.c}</td><td>R$ ${fmt(vd.v)}</td>
      <td class="num-green">R$ ${fmt(vd.cv)}</td>
      <td>R$ ${fmt(vd.ct)}</td>
      <td><strong>R$ ${fmt(vd.cv+vd.ct)}</strong></td></tr>`;
  });
  document.getElementById('comissoes-tbody').innerHTML=rows||'<tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:20px">Sem dados</td></tr>';
  document.getElementById('comissoes-tfoot').innerHTML=totN>0?`<tr>
    <td><strong>Total</strong></td><td><strong>${totN}</strong></td>
    <td><strong>R$ ${fmt(totV)}</strong></td>
    <td class="num-green"><strong>R$ ${fmt(totCv)}</strong></td>
    <td><strong>R$ ${fmt(totCt)}</strong></td>
    <td><strong>R$ ${fmt(totCv+totCt)}</strong></td></tr>`:'';

  if(typeof updateAdvanced === 'function') updateAdvanced();
}

// ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ GrÃÂÃÂ¡fico YoY (criado uma vez, atualizado ao entrar em Comparar) ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
let chartYoY = null;

function renderCompare() {
  document.getElementById('compare-section').classList.add('show');
  const cmp = DATA.compare;
  if (!cmp) { document.getElementById('compare-section').innerHTML='<p style="padding:20px;color:#94a3b8">Dados de comparaÃÂÃÂ§ÃÂÃÂ£o nÃÂÃÂ£o disponÃÂÃÂ­veis (ÃÂÃÂ© necessÃÂÃÂ¡rio ter 2025 e 2026 na planilha).</p>'; return; }

  // GrÃÂÃÂ¡fico de barras lado-a-lado por mÃÂÃÂªs
  const mesesCmp = Object.keys(cmp.mensal||{});
  const mesLbls  = mesesCmp.map(m=>({jan:'Jan',fev:'Fev',mar:'Mar',abr:'Abr',mai:'Mai',jun:'Jun',jul:'Jul',ago:'Ago',set:'Set',out:'Out',nov:'Nov',dez:'Dez'}[m]||m));
  const v25 = mesesCmp.map(m=>(cmp.mensal[m].fat.v25||0));
  const v26 = mesesCmp.map(m=>(cmp.mensal[m].fat.v26||0));

  if (!chartYoY) {
    const ctx = document.getElementById('chartYoY').getContext('2d');
    chartYoY = new Chart(ctx, {
      type:'bar',
      data:{labels:mesLbls,datasets:[
        {label:'2025',data:v25,backgroundColor:'rgba(59,130,246,.7)',borderRadius:6,borderSkipped:false},
        {label:'2026',data:v26,backgroundColor:'rgba(34,197,94,.85)',borderRadius:6,borderSkipped:false}
      ]},
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{position:'top'},tooltip:{callbacks:{label:ctx=>' R$ '+fmt(ctx.parsed.y)}}},
        scales:{
          y:{ticks:{callback:v=>'R$'+fmtK(v),font:{size:11}},grid:{color:'#f1f5f9'}},
          x:{grid:{display:false}}
        }
      }
    });
  } else {
    chartYoY.data.labels=mesLbls;
    chartYoY.data.datasets[0].data=v25;
    chartYoY.data.datasets[1].data=v26;
    chartYoY.update();
  }

  // Tabela YoY por mÃÂÃÂªs
  let rowsMes='';
  mesesCmp.forEach(m=>{
    const r=cmp.mensal[m];
    const pct=r.fat.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'ÃÂ¢ÃÂÃÂ':pct>=0?'ÃÂ¢ÃÂÃÂ² '+pct+'%':'ÃÂ¢ÃÂÃÂ¼ '+Math.abs(pct)+'%';
    rowsMes+=`<tr>
      <td><strong>${mesLbls[mesesCmp.indexOf(m)]}</strong></td>
      <td>R$ ${fmt(r.fat.v25)}</td>
      <td>R$ ${fmt(r.fat.v26)}</td>
      <td class="${cls}">${arrow}</td>
    </tr>`;
  });
  document.getElementById('yoy-mes-table-wrap').innerHTML=`
    <table class="yoy-table">
      <thead><tr><th>MÃÂÃÂªs</th><th>2025</th><th>2026</th><th>Var. %</th></tr></thead>
      <tbody>${rowsMes}</tbody>
    </table>`;

  // Tabela YoY por vendedor
  let rowsVend='';
  Object.entries(cmp.vend||{}).forEach(([v,r])=>{
    const pct=r.fat.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'ÃÂ¢ÃÂÃÂ':pct>=0?'ÃÂ¢ÃÂÃÂ² '+pct+'%':'ÃÂ¢ÃÂÃÂ¼ '+Math.abs(pct)+'%';
    rowsVend+=`<tr>
      <td><span class="vend-badge"><span class="vend-dot" style="background:${VEND_COLORS[v]||'#94a3b8'}"></span>${VEND_NAMES[v]||v}</span></td>
      <td>R$ ${fmt(r.fat.v25)}</td>
      <td>R$ ${fmt(r.fat.v26)}</td>
      <td class="${cls}">${arrow}</td>
      <td>R$ ${fmt(r.tkt.v25)}</td>
      <td>R$ ${fmt(r.tkt.v26)}</td>
    </tr>`;
  });
  document.getElementById('yoy-vend-table-wrap').innerHTML=`
    <table class="yoy-table">
      <thead><tr><th>Vendedor</th><th>Fat. 2025</th><th>Fat. 2026</th><th>Var. %</th><th>Tkt. 2025</th><th>Tkt. 2026</th></tr></thead>
      <tbody>${rowsVend}</tbody>
    </table>`;

  // KPIs gerais
  const tot=cmp.total;
  const kpis=[
    {label:'Faturamento',r:tot.fat,fmt:'R$ '},
    {label:'NÃÂÃÂº Vendas',  r:tot.n,  fmt:''},
    {label:'Ticket MÃÂÃÂ©dio',r:tot.tkt,fmt:'R$ '},
  ];
  let kpiHtml='<div style="display:grid;gap:12px">';
  kpis.forEach(k=>{
    const pct=k.r.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'ÃÂ¢ÃÂÃÂ':pct>=0?'ÃÂ¢ÃÂÃÂ² '+pct+'%':'ÃÂ¢ÃÂÃÂ¼ '+Math.abs(pct)+'%';
    kpiHtml+=`<div style="background:var(--cinza);border-radius:10px;padding:12px 16px">
      <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">${k.label}</div>
      <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap">
        <span style="font-size:14px;color:var(--text-muted)">2025: <strong>${k.fmt}${fmt(k.r.v25)}</strong></span>
        <span style="font-size:14px;color:var(--text)">2026: <strong>${k.fmt}${fmt(k.r.v26)}</strong></span>
        <span class="${cls}" style="font-size:15px">${arrow}</span>
      </div>
    </div>`;
  });
  kpiHtml+='</div>';
  document.getElementById('yoy-kpi-wrap').innerHTML=kpiHtml;
}

function hideCompare() {
  document.getElementById('compare-section').classList.remove('show');
}

function refreshData() {
  document.getElementById('loadingOverlay').classList.add('show');
  setTimeout(() => { document.getElementById('loadingOverlay').classList.remove('show'); }, 800);
  updateDashboard();
}

// Inicializa dashboard
updateDashboard();
"""

    # Substitui o bloco refreshData e a chamada inicial se existirem
    html = re.sub(r'\nasync function refreshData\(\)\s*\{[\s\S]*?\n\}\s*\n', '\n', html)
    html = re.sub(r'\n\s*updateDashboard\(\);\s*\n\s*</script>', '\n</script>', html)
    parts = html.rsplit('</script>', 1)
    html = parts[0] + yoy_js + '\n</script>' + parts[1]

    return html


def generate(data: dict, records: int, timestamp: str) -> Path:
    """Pipeline completo de geraÃÂÃÂ§ÃÂÃÂ£o do HTML."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template nÃÂÃÂ£o encontrado: {TEMPLATE_PATH}\n"
            "Coloque o arquivo original em 'templates/dashboard.html'."
        )

    anos = [k for k in data.keys() if k.isdigit()]
    if not anos:
        anos = ["2026"]

    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    print("[generate] Injetando dados multi-ano...")
    html = inject_data(html, data)

    print(f"[generate] Atualizando filtros de ano ({', '.join(sorted(anos))})...")
    html = update_year_filter(html, anos)
    html = update_month_filter(html, data, anos)

    print("[generate] Atualizando metadados...")
    html = update_meta(html, records, timestamp, anos)

    print("[generate] Injetando lÃÂÃÂ³gica JS multi-ano + YoY...")
    html = inject_multiyear_js(html, anos)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"[generate] ÃÂ¢ÃÂÃÂ HTML gerado: {OUTPUT_PATH.name} ({size_kb:.1f} KB)")

    return OUTPUT_PATH


if __name__ == "__main__":
    import sys
    history_dir = BASE_DIR / "history"
    snaps = sorted(history_dir.glob("snapshot_*.json"))
    if not snaps:
        print("Nenhum snapshot. Rode fetch_data.py primeiro.")
        sys.exit(1)
    snap = json.loads(snaps[-1].read_text(encoding="utf-8"))
    out  = generate(snap["data"], snap["records"], snap["timestamp"])
    print(f"\nÃÂ¢ÃÂÃÂ Dashboard gerado: {out}")


