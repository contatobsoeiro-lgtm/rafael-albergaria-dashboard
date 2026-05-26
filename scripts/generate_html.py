"""
generate_html.py — versão multi-ano (2025 + 2026 + YoY)
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
Injeta o objeto DATA multi-ano no template HTML e:
  - Atualiza filtros de período e ano dinamicamente
  - Atualiza metadados (data, registros, rodapé)
  - Preserva toda a lógica JS existente do dashboard
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
    "jan":"Janeiro","fev":"Fevereiro","mar":"Março","abr":"Abril",
    "mai":"Maio","jun":"Junho","jul":"Julho","ago":"Agosto",
    "set":"Setembro","out":"Outubro","nov":"Novembro","dez":"Dezembro"
}
MES_LABEL_SHORT = {
    "jan":"Jan","fev":"Fev","mar":"Mar","abr":"Abr",
    "mai":"Mai","jun":"Jun","jul":"Jul","ago":"Ago",
    "set":"Set","out":"Out","nov":"Nov","dez":"Dez"
}

# Regex para localizar o bloco const DATA = {...}
DATA_PATTERN = re.compile(
    r"(const DATA\s*=\s*)\{[\s\S]*?\n\};\s*\n",
    re.MULTILINE
)


def build_js_data(data: dict) -> str:
    """Serializa DATA para JS com formatação legível."""
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
    Injeta (ou atualiza) os botões de filtro de ANO no HTML (formato novo com filter-track).
    Botoes Atual/Todos/Anos ficam dentro do track; "Comparar Anos" fica fora como acao destacada.
    """
    track_buttons = [
        '<button class="filter-btn active" data-ano="latest" onclick="setAno(\'latest\')">Atual</button>',
        '<button class="filter-btn" data-ano="todos" onclick="setAno(\'todos\')">Todos</button>'
    ]
    for ano in sorted(anos, reverse=True):
        track_buttons.append(
            f'<button class="filter-btn" data-ano="{ano}" onclick="setAno(\'{ano}\')">{ano}</button>'
        )

    year_label = (
        '<span class="filter-label">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">'
        '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
        '</svg>Ano</span>'
    )

    year_block = (
        '<div class="filter-group" id="year-filter-group">\n'
        '      ' + year_label + '\n'
        '      <div class="filter-track">\n'
        '        ' + "\n        ".join(track_buttons) + "\n"
        '      </div>\n'
        '      <button class="filter-btn filter-btn-compare" data-ano="compare" onclick="setAno(\'compare\')">📊 Comparar Anos</button>\n'
        '    </div>'
    )

    # Substituicao com balance de divs (regex puro nao da conta de aninhamento)
    if 'id="year-filter-group"' in html:
        start = html.find('<div class="filter-group" id="year-filter-group">')
        if start >= 0:
            depth = 0
            i = start
            while i < len(html):
                if html[i:i+4] == '<div':
                    depth += 1
                    # Pula ate fechar a tag de abertura
                    i = html.find('>', i) + 1
                    continue
                if html[i:i+6] == '</div>':
                    depth -= 1
                    i += 6
                    if depth == 0:
                        break
                    continue
                i += 1
            html = html[:start] + year_block + html[i:]
    else:
        html = html.replace(
            '</div>\n</div>\n\n  <div class="kpi-grid">',
            year_block + '\n  </div>\n\n  <div class="kpi-grid">'
        )
    return html


def update_month_filter(html: str, data: dict, anos: list) -> str:
    """Sempre inclui os 12 meses no filtro (labels abreviados) — barra de seleção fixa."""
    buttons = ['<button class="filter-btn active" data-mes="all" onclick="setMes(\'all\')">Todos</button>']
    for m in MES_ORDER:
        buttons.append(
            f'<button class="filter-btn" data-mes="{m}" onclick="setMes(\'{m}\')">{MES_LABEL_SHORT[m]}</button>'
        )

    new_buttons = "\n        ".join(buttons)
    # Match: span Periodo + filter-track inteiro
    html = re.sub(
        r'(<span class="filter-label"[^>]*>(?:<svg[\s\S]*?</svg>)?\s*Per[íi]odo</span>\s*)<div class="filter-track">[\s\S]*?</div>',
        lambda m: m.group(1) + '<div class="filter-track">\n        ' + new_buttons + '\n      </div>',
        html,
        count=1
    )
    return html


def update_meta(html: str, records: int, timestamp: str, anos: list) -> str:
    """Atualiza data, registros e rodapé."""
    dt       = datetime.fromisoformat(timestamp)
    date_str = dt.strftime("%d/%m/%Y — dados reais")
    time_str = f"{records} registros · {', '.join(sorted(anos))}"
    full_date = dt.strftime("%d/%m/%Y")
    anos_str  = " + ".join(sorted(anos))

    html = re.sub(r'(<strong id="updateDate">)[^<]*(</strong>)',
                  f'\\g<1>{date_str}\\g<2>', html)
    html = re.sub(r'(<span id="updateTime">)[^<]*(</span>)',
                  f'\\g<1>{time_str}\\g<2>', html)
    html = re.sub(r'(<strong id="footer-records">)[^<]*(</strong>)',
                  f'\\g<1>{records} registros · {anos_str}\\g<2>', html)
    html = re.sub(r'(Última atualização: <strong>)[^<]*(</strong>)',
                  f'\\g<1>{full_date}\\g<2>', html)
    html = re.sub(r'(Controle de Vendas )\d{4}',
                  f'\\g<1>{anos_str}', html)
    return html


def inject_multiyear_js(html: str, anos: list) -> str:
    """
    Injeta/substitui a lógica JS de controle multi-ano no dashboard.
    Adiciona: activeAno, setAno(), getKey() compatível com anos, seção YoY.
    """
    latest = sorted(anos)[-1]

    js_multiyr = f"""
// =====================================================================
// CONTROLE MULTI-ANO — {" + ".join(sorted(anos))}
// =====================================================================
let activeAno  = 'latest';   // 'latest' | '2025' | '2026' | 'compare'
let activeMes  = 'all';
let activeVend = 'all';

const ANOS_DISPONIVEIS = {json.dumps(sorted(anos))};
const LATEST_ANO = '{latest}';
const META_MENSAL = 60000;

function setAno(ano) {{
  activeAno = ano;
  document.querySelectorAll('[data-ano]').forEach(b =>
    b.classList.toggle('active', b.dataset.ano === ano));

  // No modo comparação, limpa filtros de mês/vendedor
  if (ano === 'compare') {{
    activeMes  = 'all';
    activeVend = 'all';
    document.querySelectorAll('[data-mes]').forEach(b => b.classList.toggle('active', b.dataset.mes === 'all'));
    document.querySelectorAll('[data-vend]').forEach(b => b.classList.toggle('active', b.dataset.vend === 'all'));
    renderCompare();
    return;
  }}
  if (typeof hideCompare === 'function') hideCompare();
  updateDashboard();
  if (typeof updateClearBtn === 'function') updateClearBtn();
}}

function setMes(mes) {{
  activeMes = mes;
  document.querySelectorAll('[data-mes]').forEach(b =>
    b.classList.toggle('active', b.dataset.mes === mes));
  if (activeAno !== 'compare') updateDashboard();
  if (typeof updateClearBtn === 'function') updateClearBtn();
}}

function setVend(vend) {{
  activeVend = vend;
  document.querySelectorAll('[data-vend]').forEach(b =>
    b.classList.toggle('active', b.dataset.vend === vend));
  if (activeAno !== 'compare') updateDashboard();
  if (typeof updateClearBtn === 'function') updateClearBtn();
}}

function updateClearBtn() {{
  const btn = document.getElementById('btn-clear-filters');
  if (!btn) return;
  const hasFilter = (typeof activeMes !== 'undefined' && activeMes !== 'all') ||
                    (typeof activeVend !== 'undefined' && activeVend !== 'all') ||
                    (typeof activeAno !== 'undefined' && activeAno !== 'latest');
  btn.style.display = hasFilter ? 'inline-flex' : 'none';
}}

function clearFilters() {{
  if (typeof setMes === 'function') setMes('all');
  if (typeof setVend === 'function') setVend('all');
  if (typeof setAno === 'function') setAno('latest');
  updateClearBtn();
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

const VEND_NAMES  = {{RAQUEL:'Raquel',RAFAEL:'Rafael',JUNIO:'Junio'}};
const VEND_COLORS = {{RAQUEL:'#22c55e',RAFAEL:'#3b82f6',JUNIO:'#f59e0b'}};
const MODAL_COLORS = ['#22c55e','#3b82f6','#f59e0b','#8b5cf6'];

// Registra plugin datalabels (off por padrao; habilitado em cada chart)
if (window.ChartDataLabels) {{
  Chart.register(ChartDataLabels);
  Chart.defaults.set('plugins.datalabels', {{ display: false }});
}}
"""

    # CSS para botão comparar
    css_compare = """
  .filter-btn-compare { color: #7c3aed !important; background: rgba(139,92,246,.08) !important; padding-left: 14px !important; padding-right: 14px !important; font-weight: 700 !important; margin-left: 6px; }
  .filter-btn-compare:hover { background: rgba(139,92,246,.15) !important; color: #6d28d9 !important; }
  .filter-btn-compare.active { background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important; color: #fff !important; box-shadow: 0 1px 2px rgba(15,23,42,.08), 0 2px 8px rgba(139,92,246,.32) !important; }
  .filter-btn-compare.active:hover { background: linear-gradient(135deg, #7c3aed, #6d28d9) !important; }
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

    # Injeta seção HTML de comparação antes do rodapé
    compare_section = """
<!-- ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
     SEÇÃO COMPARATIVO YoY (2025 vs 2026)
     ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ -->
<div id="compare-section" class="main" style="padding-top:0">
  <div class="section-header">
    <div class="section-header-title">📊 Comparativo 2025 vs 2026</div>
    <div class="section-header-sub">Evolução mensal · YoY por vendedor · Crescimento</div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Faturamento por Mês — 2025 vs 2026</div>
      <div class="chart-sub">Comparação mês a mês dos dois anos</div>
      <div class="chart-wrap h260"><canvas id="chartYoY"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Crescimento YoY por Mês</div>
      <div class="chart-sub">Variação percentual mês a mês (%)</div>
      <div id="yoy-mes-table-wrap"></div>
    </div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Vendedores — 2025 vs 2026</div>
      <div class="chart-sub">Faturamento total por vendedor em cada ano</div>
      <div id="yoy-vend-table-wrap"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">KPIs Gerais — Evolução Anual</div>
      <div class="chart-sub">Totais consolidados dos dois anos</div>
      <div id="yoy-kpi-wrap"></div>
    </div>
  </div>
</div>
"""
    html = html.replace('<div class="footer">', compare_section + '\n<div class="footer">', 1)

    # Remove as versoes antigas de setMes/setVend/getKey ANTES de injetar js_multiyr
    # (evita que o cleanup remova as versoes novas que serao injetadas a seguir)
    for fn in ["function setMes", "function setVend", "function getKey"]:
        html = re.sub(rf'{fn}\s*\([^)]*\)\s*\{{[\s\S]*?\n\}}', '', html)

    # Injeta JS multi-ano substituindo o bloco ESTADO (agora com as novas funcoes)
    html = re.sub(
        r'// ={5,}\s*\n// ESTADO[\s\S]*?// ={5,}\s*\n// CHARTS',
        js_multiyr + "\n// =====================================================================\n// CHARTS",
        html,
        count=1
    )

    # Injeta chart YoY e funções renderCompare/hideCompare antes do fechamento do script
    yoy_js = """
// =====================================================================
// DASHBOARD MULTI-ANO — lógica de rendering
// =====================================================================

// Lista de vendedores dinâmica (vem do Python via DATA.meta.vendors)
const VENDORS_LIST = (DATA.meta && DATA.meta.vendors) ? DATA.meta.vendors : ['RAQUEL','RAFAEL','JUNIO'];

// Paleta de cores para vendedores extras (além dos 3 originais)
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
  document.getElementById('kpi-ticket').textContent   = d.tkt ? 'R$ ' + fmt(d.tkt) : '—';
  const margem    = (d.fat||0) - (d.cvend||0) - (d.ctreino||0);
  const margemPct = d.fat > 0 ? Math.round(margem/d.fat*100) : 0;
  document.getElementById('kpi-margem').textContent     = 'R$ ' + fmt(margem);
  document.getElementById('kpi-margem-pct-val').textContent = margemPct + '%';
  document.getElementById('kpi-cvend-card').textContent = 'R$ ' + fmt(d.cvend||0);
  document.getElementById('kpi-personal').textContent   = 'R$ ' + fmt(d.ctreino||0);

  // Indicador MoM (variacao vs mes anterior) nos 3 KPIs principais
  (function() {
    const MES_ORDER_LOC = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
    const mesData = d.mes || {};
    let curMes = null, prevMes = null;
    if (activeMes === 'all') {
      const ms = MES_ORDER_LOC.filter(m => mesData[m] && mesData[m].v > 0);
      if (ms.length >= 2) { curMes = ms[ms.length-1]; prevMes = ms[ms.length-2]; }
    } else {
      const idx = MES_ORDER_LOC.indexOf(activeMes);
      if (idx >= 1) { curMes = activeMes; prevMes = MES_ORDER_LOC[idx-1]; }
    }
    function renderTrend(elId, pct, lbl) {
      const el = document.getElementById(elId);
      if (!el) return;
      if (pct === null || !isFinite(pct)) { el.innerHTML = ''; return; }
      const cls = pct > 0 ? 'up' : (pct < 0 ? 'down' : 'neu');
      const arrow = pct > 0 ? '▲' : (pct < 0 ? '▼' : '·');
      const sign = pct > 0 ? '+' : '';
      el.innerHTML = ' <span class="kpi-trend ' + cls + '" title="' + lbl + '">' + arrow + ' ' + sign + pct + '%</span>';
    }
    if (curMes && prevMes && mesData[curMes] && mesData[prevMes] && mesData[prevMes].v > 0) {
      const cur = mesData[curMes], prev = mesData[prevMes];
      const MES_LBL_SHORT = {jan:'Jan',fev:'Fev',mar:'Mar',abr:'Abr',mai:'Mai',jun:'Jun',jul:'Jul',ago:'Ago',set:'Set',out:'Out',nov:'Nov',dez:'Dez'};
      const lbl = (MES_LBL_SHORT[curMes]||curMes) + ' vs ' + (MES_LBL_SHORT[prevMes]||prevMes);
      const fatPct = Math.round((cur.v - prev.v) / prev.v * 100);
      const vendPct = prev.c > 0 ? Math.round((cur.c - prev.c) / prev.c * 100) : null;
      const curTkt = cur.c > 0 ? cur.v / cur.c : 0;
      const prevTkt = prev.c > 0 ? prev.v / prev.c : 0;
      const tktPct = prevTkt > 0 ? Math.round((curTkt - prevTkt) / prevTkt * 100) : null;
      renderTrend('kpi-fat-trend', fatPct, 'Faturamento ' + lbl);
      renderTrend('kpi-vendas-trend', vendPct, 'Vendas ' + lbl);
      renderTrend('kpi-ticket-trend', tktPct, 'Ticket ' + lbl);
    } else {
      ['kpi-fat-trend','kpi-vendas-trend','kpi-ticket-trend'].forEach(id => {
        const el = document.getElementById(id); if (el) el.innerHTML = '';
      });
    }
  })();

  const ano    = activeAno === 'latest' ? LATEST_ANO : activeAno;
  const anoTxt = activeAno === 'todos' ? 'Todos os anos' : ano;
  const mesLbl = {all:anoTxt+' acumulado',jan:'Jan '+ano,fev:'Fev '+ano,mar:'Mar '+ano,
                  abr:'Abr '+ano,mai:'Mai '+ano,jun:'Jun '+ano,jul:'Jul '+ano,
                  ago:'Ago '+ano,set:'Set '+ano,out:'Out '+ano,nov:'Nov '+ano,dez:'Dez '+ano};
  // Gera mapeamento vend→label dinamicamente
  const vLblMap = {all:''};
  VENDORS_LIST.forEach(v => { vLblMap[v.toLowerCase()] = ' · ' + v.charAt(0) + v.slice(1).toLowerCase(); });
  document.getElementById('kpi-fat-badge').textContent = (mesLbl[activeMes]||anoTxt) + (vLblMap[activeVend]||'');

  // Sub-titulos dinamicos (refletem filtros)
  const filterSuffix = (mesLbl[activeMes]||anoTxt) + (vLblMap[activeVend]||'');
  const subMesEl   = document.getElementById('sub-mes');
  const subModalEl = document.getElementById('sub-modal');
  const subVendEl  = document.getElementById('sub-vend');
  if (subModalEl) subModalEl.textContent = 'Distribuição por número de vendas · ' + filterSuffix;
  if (subVendEl)  subVendEl.textContent  = 'Faturamento por vendedor · ' + filterSuffix;

  // Meses com dados
  const mesKeys = Object.keys(d.mes||{}).filter(m => (d.mes[m].v||0) > 0);
  const mesVals = mesKeys.map(m => d.mes[m].v);
  const mesNames = {jan:'Jan',fev:'Fev',mar:'Mar',abr:'Abr',mai:'Mai',jun:'Jun',jul:'Jul',ago:'Ago',set:'Set',out:'Out',nov:'Nov',dez:'Dez'};
  const mesNamesFull = {jan:'Janeiro',fev:'Fevereiro',mar:'Março',abr:'Abril',mai:'Maio',jun:'Junho',jul:'Julho',ago:'Agosto',set:'Setembro',out:'Outubro',nov:'Novembro',dez:'Dezembro'};
  const mesLbls = mesKeys.map(m => mesNames[m]||m);

  if (subMesEl) {
    if (activeMes !== 'all') {
      subMesEl.textContent = (mesNamesFull[activeMes]||activeMes) + ' ' + ano + (vLblMap[activeVend]||'');
    } else if (mesKeys.length === 0) {
      subMesEl.textContent = 'Sem dados · ' + anoTxt + (vLblMap[activeVend]||'');
    } else if (mesKeys.length === 1) {
      subMesEl.textContent = (mesNamesFull[mesKeys[0]]||mesKeys[0]) + ' · ' + anoTxt + (vLblMap[activeVend]||'');
    } else {
      const first = mesNamesFull[mesKeys[0]] || mesKeys[0];
      const last  = mesNamesFull[mesKeys[mesKeys.length-1]] || mesKeys[mesKeys.length-1];
      subMesEl.textContent = first + ' a ' + last + ' · ' + anoTxt + (vLblMap[activeVend]||'');
    }
  }

  chartMes.data.labels   = mesLbls;
  chartMes.data.datasets[0].data = mesVals;
  chartMes.data.datasets[0].backgroundColor = mesLbls.map((_,i)=>['rgba(34,197,94,.85)','rgba(59,130,246,.85)','rgba(245,158,11,.85)','rgba(139,92,246,.85)','rgba(236,72,153,.85)','rgba(20,184,166,.85)'][i%6]);
  chartMes.data.datasets[1].data = Array(mesLbls.length).fill(META_MENSAL);
  chartMes.update();

  chartModal.data.datasets[0].data = ['MENSAL','TRIMESTRAL','SEMESTRAL','ANUAL'].map(m=>(d.modal&&d.modal[m])?d.modal[m].c:0);
  chartModal.update();

  chartVend.data.labels = VENDORS_LIST;
  chartVend.data.datasets[0].data = VENDORS_LIST.map(v=>(d.vend&&d.vend[v])?d.vend[v].v:0);
  chartVend.update();

  chartTicket.data.labels = VENDORS_LIST;
  chartTicket.data.datasets[0].data = VENDORS_LIST.map(v=>(d.vend&&d.vend[v]&&d.vend[v].tkt)?d.vend[v].tkt:0);
  chartTicket.update();

  // Comissões — todos os vendedores dinâmicos
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

// Override updateAdvanced to use multi-year data structure
function updateAdvanced() {
  const anoData = getAnoData();
  let rows = '';
  VENDORS_LIST.forEach(v => {
    const vk = v.toLowerCase();
    if (activeVend !== 'all' && activeVend !== vk) return;
    const dataKey = activeMes !== 'all' ? vk + '_' + activeMes : vk;
    const vd = anoData[dataKey];
    if (!vd || !vd.n) return;
    const m = vd.modal || {};
    const n = vd.n;
    const pct = val => n > 0 ? Math.round((val||0) / n * 100) : 0;
    const cM = (m.MENSAL    && m.MENSAL.c)    || 0;
    const cT = (m.TRIMESTRAL && m.TRIMESTRAL.c) || 0;
    const cS = (m.SEMESTRAL  && m.SEMESTRAL.c)  || 0;
    const cA = (m.ANUAL      && m.ANUAL.c)      || 0;
    const pLongo = pct(cS + cA);
    const pillClass = pLongo >= 35 ? 'pill-green' : pLongo >= 25 ? 'pill-blue' : 'pill-gray';
    const cor = VEND_COLORS[v] || '#94a3b8';
    const nome = VEND_NAMES[v] || (v.charAt(0) + v.slice(1).toLowerCase());
    rows += '<tr>' +
      '<td><span class="vend-badge"><span class="vend-dot" style="background:' + cor + '"></span>' + nome + '</span></td>' +
      '<td>' + pct(cM) + '% <small style="color:var(--text-muted)">(' + cM + ')</small></td>' +
      '<td>' + pct(cT) + '% <small style="color:var(--text-muted)">(' + cT + ')</small></td>' +
      '<td>' + pct(cS) + '% <small style="color:var(--text-muted)">(' + cS + ')</small></td>' +
      '<td>' + pct(cA) + '% <small style="color:var(--text-muted)">(' + cA + ')</small></td>' +
      '<td><span class="pill ' + pillClass + '">' + pLongo + '%</span></td>' +
      '</tr>';
  });
  const el = document.getElementById('upsell-tbody');
  if (el) el.innerHTML = rows;
}

// -- Grafico YoY (criado uma vez, atualizado ao entrar em Comparar) ââ
let chartYoY = null;

function renderCompare() {
  document.getElementById('compare-section').classList.add('show');
  document.getElementById('compare-section').scrollIntoView({behavior:'smooth',block:'start'});
  const cmp = DATA.compare;
  if (!cmp) { document.getElementById('compare-section').innerHTML='<p style="padding:20px;color:#94a3b8">Dados de comparação não disponíveis (é necessário ter 2025 e 2026 na planilha).</p>'; return; }

  // Gráfico de barras lado-a-lado por mês
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

  // Tabela YoY por mês
  let rowsMes='';
  mesesCmp.forEach(m=>{
    const r=cmp.mensal[m];
    const pct=r.fat.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'—':pct>=0?'▲ '+pct+'%':'▼ '+Math.abs(pct)+'%';
    rowsMes+=`<tr>
      <td><strong>${mesLbls[mesesCmp.indexOf(m)]}</strong></td>
      <td>R$ ${fmt(r.fat.v25)}</td>
      <td>R$ ${fmt(r.fat.v26)}</td>
      <td class="${cls}">${arrow}</td>
    </tr>`;
  });
  document.getElementById('yoy-mes-table-wrap').innerHTML=`
    <table class="yoy-table">
      <thead><tr><th>Mês</th><th>2025</th><th>2026</th><th>Var. %</th></tr></thead>
      <tbody>${rowsMes}</tbody>
    </table>`;

  // Tabela YoY por vendedor
  let rowsVend='';
  Object.entries(cmp.vend||{}).forEach(([v,r])=>{
    const pct=r.fat.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'—':pct>=0?'▲ '+pct+'%':'▼ '+Math.abs(pct)+'%';
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
    {label:'Nº Vendas',  r:tot.n,  fmt:''},
    {label:'Ticket Médio',r:tot.tkt,fmt:'R$ '},
  ];
  let kpiHtml='<div style="display:grid;gap:12px">';
  kpis.forEach(k=>{
    const pct=k.r.pct;
    const cls=pct===null?'yoy-neu':pct>=0?'yoy-up':'yoy-down';
    const arrow=pct===null?'—':pct>=0?'▲ '+pct+'%':'▼ '+Math.abs(pct)+'%';
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
    html = re.sub(r'\nasync\s+function refreshData\(\)\s*\{[\s\S]*?\n\}\s*\n', '\n', html)
    html = re.sub(r'\n\s*updateDashboard\(\);\s*\n\s*</script>', '\n</script>', html)
    parts = html.rsplit('</script>', 1)
    html  = parts[0] + yoy_js + '\n</script>' + parts[1]

    return html


def generate(data: dict, records: int, timestamp: str) -> Path:
    """Pipeline completo de geração do HTML."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template não encontrado: {TEMPLATE_PATH}\n"
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

    print("[generate] Injetando lógica JS multi-ano + YoY...")
    html = inject_multiyear_js(html, anos)

    # Inject Todos aggregation JS
    # Injeta script de agregação "Todos" (soma todos os anos)
    _todos_js = """<script>
(function(){
  var _origGetAnoData = getAnoData;
  getAnoData = function() {
    if (activeAno === 'todos') return buildTodosData();
    return _origGetAnoData.call(this);
  };
  window.buildTodosData = function() {
    var anos = Object.keys(DATA).filter(function(k){ return k.length===4 && !isNaN(k); });
    if (!anos.length) return {};
    var allKeys = {};
    anos.forEach(function(a){ Object.keys(DATA[a]).forEach(function(k){ allKeys[k]=1; }); });
    function mergeBlock(a, b) {
      if (!a && !b) return {n:0,fat:0,tkt:0,cvend:0,ctreino:0,modal:{},vend:{},mes:{}};
      if (!a) return JSON.parse(JSON.stringify(b));
      if (!b) return JSON.parse(JSON.stringify(a));
      var n=+(a.n||0)+ +(b.n||0), fat=+(a.fat||0)+ +(b.fat||0);
      var cv=+(a.cvend||0)+ +(b.cvend||0), ct=+(a.ctreino||0)+ +(b.ctreino||0);
      var modal={}, vend={}, mes={};
      [a.modal||{}, b.modal||{}].forEach(function(obj){
        Object.keys(obj).forEach(function(k){ modal[k]=(modal[k]||0)+(obj[k]||0); });
      });
      [a.vend||{}, b.vend||{}].forEach(function(obj){
        Object.keys(obj).forEach(function(k){
          if (!vend[k]) vend[k]={c:0,v:0,tkt:0,cv:0,ct:0};
          vend[k].c += (obj[k] ? obj[k].c||0 : 0);
          vend[k].v += (obj[k] ? obj[k].v||0 : 0);
          vend[k].cv += (obj[k] ? obj[k].cv||0 : 0);
          vend[k].ct += (obj[k] ? obj[k].ct||0 : 0);
        });
      });
      Object.keys(vend).forEach(function(k){
        vend[k].tkt = vend[k].c ? Math.round(vend[k].v/vend[k].c) : 0;
      });
      [a.mes||{}, b.mes||{}].forEach(function(obj){
        Object.keys(obj).forEach(function(k){
          if (!mes[k]) mes[k]={c:0,v:0};
          mes[k].c += (obj[k] ? obj[k].c||0 : 0);
          mes[k].v += (obj[k] ? obj[k].v||0 : 0);
        });
      });
      return {n:n,fat:fat,tkt:n?Math.round(fat/n):0,cvend:cv,ctreino:ct,modal:modal,vend:vend,mes:mes};
    }
    var result={};
    Object.keys(allKeys).forEach(function(key){
      var merged=null;
      anos.forEach(function(ano){ merged=mergeBlock(merged, DATA[ano][key]); });
      result[key]=merged;
    });
    return result;
  };
})();
</script>"""
    html = html.replace('</body>', _todos_js + '\n</body>')

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"[generate] â HTML gerado: {OUTPUT_PATH.name} ({size_kb:.1f} KB)")

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
    print(f"\nâ Dashboard gerado: {out}")
