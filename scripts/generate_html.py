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
    # Label "Tudo" combina os anos disponiveis (ex: "2025+2026")
    anos_label = '+'.join(sorted(anos))
    track_buttons = [
        '<button class="filter-btn active" data-ano="latest" onclick="setAno(\'latest\')">Atual</button>',
        f'<button class="filter-btn" data-ano="todos" onclick="setAno(\'todos\')" title="Soma todos os anos">{anos_label}</button>'
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
const META_MENSAL = 70000;
function calcComissaoVendedor(receita) {{
  // Regra antiga (01/08/2026), segue valendo pros demais vendedores: aliquota
  // unica sobre o total que o proprio vendedor vendeu no mes (nao progressiva).
  if (!receita || receita <= 0) return 0;
  if (receita <= 50000)  return receita * 0.03;
  if (receita <= 75000)  return receita * 0.035;
  if (receita <= 100000) return receita * 0.04;
  if (receita <= 125000) return receita * 0.045;
  return receita * 0.05;
}}

// Regra da Micaelly (proposta de setembro/2026): fixo R$ 2.300 e comissao
// sobre o que ELA vendeu (so o pago). O percentual e definido por onde a
// casa fecha o mes (tambem so o pago) e pelo nivel dela na carreira.
const MICA_FIXO  = 2300;
const MICA_NIVEL = 'Júnior';
const MICA_TIERS = {{ 'Júnior':[3,3.5,4.5,5.5], 'Pleno':[3.5,4,5,6], 'Sênior':[4,4.5,5.5,6.5] }};
function faixaCasa(casa) {{
  if (casa >= 100000) return 3;
  if (casa >= 70000)  return 2;
  if (casa >= 50000)  return 1;
  return 0;
}}
function pctMica(casa, nivel) {{
  const t = MICA_TIERS[nivel] || MICA_TIERS['Júnior'];
  return t[faixaCasa(casa)];
}}

let chartDiario = null;
function diarioMesAtivo() {{
  const ano = (typeof getAnoData === 'function') ? getAnoData() : {{}};
  const dd = ano.diario || {{}};
  if (activeMes !== 'all' && dd[activeMes] && dd[activeMes].length) return activeMes;
  const ordem = ['dez','nov','out','set','ago','jul','jun','mai','abr','mar','fev','jan'];
  for (const m of ordem) if (dd[m] && dd[m].length) return m;
  return null;
}}
function renderDiario() {{
  const anoData = (typeof getAnoData === 'function') ? getAnoData() : {{}};
  const dd = anoData.diario || {{}};
  const mes = diarioMesAtivo();
  const dias = (mes && dd[mes]) ? dd[mes] : [];
  const filtro = (activeVend && activeVend !== 'all') ? activeVend.toUpperCase() : null;

  const pts = dias.map(x => {{
    const val = filtro ? ((x.vd && x.vd[filtro]) || 0) : x.v;
    let qtd = x.n;
    if (filtro) qtd = (x.vd && x.vd[filtro]) ? null : 0;   // sem contagem por vendedor no dia
    return {{d: x.d, v: val, n: qtd}};
  }}).filter(x => !filtro || x.v > 0);

  const sub = document.getElementById('diario-sub');
  if (sub) sub.textContent = mes
    ? ('Mês: ' + mes.toUpperCase() + (filtro ? ' · Vendedor: ' + filtro : ' · Todos os vendedores'))
    : 'Sem dados no recorte';

  // grafico
  const cv = document.getElementById('chartDiario');
  if (cv && typeof Chart !== 'undefined') {{
    const labels = pts.map(p => String(p.d).padStart(2,'0'));
    const vals   = pts.map(p => p.v);
    const metaDia = META_MENSAL / 21;
    const linha  = pts.map(() => Math.round(metaDia));
    if (chartDiario) {{
      chartDiario.data.labels = labels;
      chartDiario.data.datasets[0].data = vals;
      chartDiario.data.datasets[1].data = linha;
      chartDiario.update();
    }} else {{
      chartDiario = new Chart(cv, {{
        type: 'bar',
        data: {{ labels: labels, datasets: [
          {{ label: 'Receita do dia', data: vals, backgroundColor: '#3b82f6', borderRadius: 4, order: 2 }},
          {{ label: 'Meta diária', data: linha, type: 'line', borderColor: '#ef4444',
             borderDash: [6,4], borderWidth: 2, pointRadius: 0, fill: false, order: 1 }}
        ]}},
        options: {{ responsive: true, maintainAspectRatio: false,
          plugins: {{ legend: {{ display: true, position: 'bottom' }},
            tooltip: {{ callbacks: {{ label: c => c.dataset.label + ': R$ ' + fmt(c.parsed.y) }} }} }},
          scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: v => 'R$ ' + fmt(v) }} }} }} }}
      }});
    }}
  }}

  // resumo
  const tot   = pts.reduce((a,b) => a + b.v, 0);
  const ndias = pts.filter(p => p.v > 0).length;
  const media = ndias ? tot / ndias : 0;
  const melhor = pts.reduce((a,b) => (b.v > (a ? a.v : -1) ? b : a), null);
  const metaDia = META_MENSAL / 21;
  const acima = pts.filter(p => p.v >= metaDia).length;
  const elR = document.getElementById('diario-resumo');
  if (elR) elR.innerHTML = '<div style="padding:14px">' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Dias com venda</span><strong>' + ndias + '</strong></div>' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Média por dia com venda</span><strong>R$ ' + fmt(Math.round(media)) + '</strong></div>' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Melhor dia</span><strong>' + (melhor ? ('dia ' + melhor.d + ' · R$ ' + fmt(melhor.v)) : '-') + '</strong></div>' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Dias que bateram a meta diária</span><strong>' + acima + ' de ' + ndias + '</strong></div>' +
    '<div style="border-top:1px solid #e2e8f0;padding-top:10px;display:flex;justify-content:space-between"><span><strong>Total no recorte</strong></span><strong style="color:#10b981">R$ ' + fmt(tot) + '</strong></div>' +
    '<div style="margin-top:8px;font-size:12px;color:#94a3b8">Meta diária de referência: R$ ' + fmt(Math.round(metaDia)) + ' (meta do mês dividida por 21 dias úteis).</div></div>';

  // tabela dia a dia
  const elT = document.getElementById('diario-tabela');
  if (elT) {{
    let acum = 0;
    const linhas = pts.slice().sort((a,b) => a.d - b.d).map(p => {{ acum += p.v; return {{...p, acum}}; }});
    const rows = linhas.slice().reverse().map(p => {{
      const bateu = p.v >= metaDia;
      return '<tr><td>dia ' + String(p.d).padStart(2,'0') + '</td>' +
        '<td>' + (p.n === null ? '-' : p.n) + '</td>' +
        '<td>R$ ' + fmt(p.v) + '</td>' +
        '<td style="color:' + (bateu ? '#10b981' : '#ef4444') + '">' + (bateu ? 'bateu' : 'abaixo') + '</td>' +
        '<td>R$ ' + fmt(p.acum) + '</td></tr>';
    }}).join('');
    elT.innerHTML = '<table class="yoy-table" style="width:100%">' +
      '<thead><tr><th>Dia</th><th>Vendas</th><th>Receita</th><th>vs meta diária</th><th>Acumulado no mês</th></tr></thead>' +
      '<tbody>' + (rows || '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:20px">Sem vendas no recorte</td></tr>') + '</tbody></table>';
  }}
}}

function renderRenovacao() {{
  const anoData = (typeof getAnoData === 'function') ? getAnoData() : {{}};
  const key = (typeof getKey === 'function') ? getKey() : 'all';
  const d = anoData[key] || anoData['all'] || {{}};

  // renovacao x venda nova
  const op = d.oper || {{}};
  const ren = op['Renovação'] || {{c:0,v:0}};
  const nov = op['Nova Venda'] || {{c:0,v:0}};
  const tot = (ren.v || 0) + (nov.v || 0);
  const pctR = tot ? Math.round(ren.v / tot * 100) : 0;
  const el1 = document.getElementById('renov-split');
  if (el1) el1.innerHTML = '<div style="padding:14px">' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Renovação</span><strong>' + (ren.c||0) + ' · R$ ' + fmt(ren.v||0) + '</strong></div>' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:12px"><span>Venda nova</span><strong>' + (nov.c||0) + ' · R$ ' + fmt(nov.v||0) + '</strong></div>' +
    '<div style="height:10px;border-radius:5px;overflow:hidden;background:#e2e8f0;display:flex">' +
      '<div style="width:' + pctR + '%;background:#22c55e"></div><div style="flex:1;background:#3b82f6"></div></div>' +
    '<div style="margin-top:8px;font-size:13px;color:#64748b">' + pctR + '% da receita veio de quem já era cliente</div></div>';

  // pendentes
  const p = d.pend || {{c:0,v:0}};
  const el2 = document.getElementById('renov-pend');
  if (el2) el2.innerHTML = (p.c ?
    '<div style="padding:14px"><div style="font-size:32px;font-weight:700;color:#f59e0b">R$ ' + fmt(p.v) + '</div>' +
    '<div style="color:#64748b;font-size:13px;margin-top:4px">' + p.c + ' venda(s) com valor ainda não recebido (status Pendente ou parcial anotado na Obs.)</div>' +
    '<div style="margin-top:10px;font-size:12px;color:#94a3b8">Esse valor fica fora da meta e da comissão do vendedor até a planilha marcar como Pago.</div></div>'
    : '<div style="text-align:center;padding:30px 12px;color:#94a3b8">✅<br><strong>Nada pendente</strong></div>');

  // carteira
  const cart = anoData.carteira || [];
  const vencidos = cart.filter(x => x.dias < 0);
  const aVencer  = cart.filter(x => x.dias >= 0);
  const sv = a => a.reduce((s,x) => s + (x.valor||0), 0);
  const el3 = document.getElementById('renov-carteira-resumo');
  if (el3) el3.innerHTML = '<div style="padding:14px">' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Já venceram</span><strong style="color:#ef4444">' + vencidos.length + ' · R$ ' + fmt(sv(vencidos)) + '</strong></div>' +
    '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Vencem em 60 dias</span><strong style="color:#f59e0b">' + aVencer.length + ' · R$ ' + fmt(sv(aVencer)) + '</strong></div>' +
    '<div style="border-top:1px solid #e2e8f0;padding-top:10px;display:flex;justify-content:space-between"><span><strong>Total em jogo</strong></span><strong style="color:#10b981">R$ ' + fmt(sv(cart)) + '</strong></div>' +
    '<div style="margin-top:8px;font-size:12px;color:#94a3b8">Baseado no último plano de cada paciente e na duração dele.</div></div>';

  const el4 = document.getElementById('renov-carteira-tabela');
  if (el4) {{
    const linhas = cart.slice(0, 60).map(x => {{
      const cor = x.dias < 0 ? '#ef4444' : (x.dias <= 7 ? '#f59e0b' : '#64748b');
      const txt = x.dias < 0 ? ('venceu há ' + Math.abs(x.dias) + 'd') : (x.dias === 0 ? 'vence hoje' : 'vence em ' + x.dias + 'd');
      return '<tr><td>' + x.nome + '</td><td>' + x.plano + '</td><td>R$ ' + fmt(x.valor) + '</td>' +
             '<td>' + x.venc + '</td><td style="color:' + cor + '"><strong>' + txt + '</strong></td><td>' + (x.vend||'') + '</td></tr>';
    }}).join('');
    el4.innerHTML = '<table class="yoy-table" style="width:100%">' +
      '<thead><tr><th>Paciente</th><th>Plano</th><th>Valor</th><th>Vence</th><th>Situação</th><th>Vendedor</th></tr></thead>' +
      '<tbody>' + (linhas || '<tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:20px">Sem carteira no período</td></tr>') + '</tbody></table>' +
      (cart.length > 60 ? '<div style="margin-top:8px;font-size:12px;color:#94a3b8">Mostrando 60 de ' + cart.length + ' pacientes.</div>' : '');
  }}
}}
function renderRemuneracao() {{
  const anoData = (typeof getAnoData === 'function') ? getAnoData() : {{}};
  const key = (typeof getKey === 'function') ? getKey() : 'all';
  const d = anoData[key] || anoData['all'] || {{}};
  const receita  = d.fat || 0;
  // Meta e deficit comercial: so conta o que esta PAGO (status + Obs. de parcial)
  const recebido = (d.fat_pago != null) ? d.fat_pago : receita;
  const aReceber = Math.max(receita - recebido, 0);
  const pct = Math.round(recebido / META_MENSAL * 100);
  const bateu = recebido >= META_MENSAL;
  const corPct = bateu ? '#10b981' : pct >= 80 ? '#f59e0b' : '#ef4444';
  // Comissao da Micaelly: o degrau vem de onde a CASA fecha o mes (so o pago),
  // por isso a base e o bloco do mes, ignorando o filtro de vendedor.
  const casaD = anoData[activeMes === 'all' ? 'all' : activeMes] || d;
  const casaPago = (casaD.fat_pago != null) ? casaD.fat_pago : (casaD.fat || 0);
  const vendCasa = casaD.vend || {{}};
  const vpDe = k => (vendCasa[k] && (vendCasa[k].vp != null ? vendCasa[k].vp : vendCasa[k].v)) || 0;
  const micaV   = vpDe('MICAELLY');
  const micaPct = pctMica(casaPago, MICA_NIVEL);
  const micaCom = Math.round(micaV * micaPct) / 100;
  // Demais vendedores comissionados seguem a regra antiga, sobre a propria venda paga
  const outros = [];
  for (const k of ['CHRISTOFER', 'JUNIO']) {{
    const v = vpDe(k);
    if (v > 0) outros.push({{ nome: (typeof VEND_NAMES !== 'undefined' && VEND_NAMES[k]) || k, com: calcComissaoVendedor(v) }});
  }}
  const elStatus = document.getElementById('rv-status');
  if (elStatus) elStatus.innerHTML = '<div style="text-align:center;padding:12px">' +
    '<div style="font-size:36px;font-weight:700;color:' + corPct + '">' + pct + '%</div>' +
    '<div style="color:#64748b;font-size:13px">da meta de R$ 70.000 · só vendas pagas</div>' +
    '<div style="margin-top:14px;font-size:18px"><strong>R$ ' + fmt(recebido) + '</strong> <span style="font-size:13px;color:#64748b">recebido</span></div>' +
    (aReceber > 0 ? '<div style="margin-top:4px;font-size:12px;color:#f59e0b">+ R$ ' + fmt(aReceber) + ' vendido aguardando pagamento (fora da conta)</div>' : '') +
    '<div style="margin-top:6px;color:#64748b;font-size:13px">' +
    (bateu ? '✅ Meta batida' : 'Faltam R$ ' + fmt(META_MENSAL - recebido)) + '</div></div>';
  const elVend = document.getElementById('rv-vendedor');
  if (elVend) {{
    let vh = '<div style="padding:14px">' +
      '<div style="font-size:12px;color:#94a3b8;margin-bottom:8px">Micaelly · nível ' + MICA_NIVEL + ' · casa em R$ ' + fmt(casaPago) + '</div>' +
      '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Fixo</span><strong>R$ ' + fmt(MICA_FIXO) + '</strong></div>' +
      '<div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Comissão (' + String(micaPct).replace('.', ',') + '% de R$ ' + fmt(micaV) + ')</span><strong>R$ ' + fmt(micaCom) + '</strong></div>' +
      '<div style="border-top:1px solid #e2e8f0;padding-top:10px;display:flex;justify-content:space-between;align-items:baseline">' +
      '<span><strong>Total estimado</strong></span><strong style="color:#10b981;font-size:22px">R$ ' + fmt(MICA_FIXO + micaCom) + '</strong></div>';
    for (const o of outros) {{
      vh += '<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#64748b"><span>' + o.nome + ' (regra antiga)</span><span>comissão R$ ' + fmt(o.com) + '</span></div>';
    }}
    if (activeMes === 'all') {{
      vh += '<div style="margin-top:8px;font-size:11px;color:#94a3b8">Visão do ano inteiro: a regra é mensal, selecione um mês pra ver o valor real.</div>';
    }}
    elVend.innerHTML = vh + '</div>';
  }}
  const elSup = document.getElementById('rv-suporte');
  if (elSup) {{
    if (!bateu) {{
      elSup.innerHTML = '<div style="text-align:center;padding:30px 12px;color:#94a3b8">🔒<br><strong>Travado</strong><br><small style="font-size:12px">Libera quando receita ≥ R$ 70.000</small></div>';
    }} else {{
      elSup.innerHTML = '<div style="padding:14px">' +
        '<div style="margin-bottom:10px;color:#64748b;font-size:13px">Por pessoa (Lais e Emilly), conforme taxa de renovação real:</div>' +
        '<div style="display:flex;justify-content:space-between;margin-bottom:6px"><span>60% a 79%</span><strong>R$ 300</strong></div>' +
        '<div style="display:flex;justify-content:space-between;margin-bottom:10px"><span>80% ou mais</span><strong style="color:#10b981">R$ 600</strong></div>' +
        '<div style="font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0;padding-top:8px">2 pessoas → total R$ 600 a R$ 1.200/mês</div></div>';
    }}
  }}
  const elFx = document.getElementById('rv-faixas');
  if (elFx) {{
    const colAtiva = faixaCasa(casaPago);
    const cols = ['Casa abaixo de R$ 50 mil', 'R$ 50 mil', 'R$ 70 mil · a meta', 'R$ 100 mil'];
    let fx = '<table class="yoy-table" style="width:100%"><thead><tr><th>Nível</th>';
    cols.forEach((c, i) => {{ fx += '<th' + (i === colAtiva ? ' style="background:#fef9c3"' : '') + '>' + c + '</th>'; }});
    fx += '</tr></thead><tbody>';
    for (const nv of ['Júnior', 'Pleno', 'Sênior']) {{
      fx += '<tr><td>' + nv + (nv === MICA_NIVEL ? ' <span style="font-size:11px;color:#ec4899;font-weight:700">· atual</span>' : '') + '</td>';
      MICA_TIERS[nv].forEach((p, i) => {{
        const on = (nv === MICA_NIVEL && i === colAtiva);
        fx += '<td' + (on ? ' style="background:#fef9c3;font-weight:700"' : '') + '>' + String(p).replace('.', ',') + '%</td>';
      }});
      fx += '</tr>';
    }}
    fx += '</tbody></table>' +
      '<div style="margin-top:8px;font-size:12px;color:#94a3b8">O percentual incide sobre o que a própria vendedora vendeu no mês (só vendas pagas). O degrau é definido por onde a casa fecha o mês, também só com vendas pagas. Vigente desde setembro/2026. Demais vendedores seguem a regra antiga: 3% a 5% sobre a própria venda paga, alíquota única.</div>';
    elFx.innerHTML = fx;
  }}
  // Placar do mes no topo da pagina: sempre MENSAL (no "Todos", usa o mes
  // mais recente com venda), porque a meta de R$ 70 mil e por mes
  const elHero = document.getElementById('hero-placar');
  if (elHero) {{
    const mesPlacar = (activeMes !== 'all') ? activeMes
      : ((typeof diarioMesAtivo === 'function') ? diarioMesAtivo() : null);
    const dP = (mesPlacar && anoData[mesPlacar]) ? anoData[mesPlacar] : d;
    const recP  = (dP.fat_pago != null) ? dP.fat_pago : (dP.fat || 0);
    const abertoP = Math.max((dP.fat || 0) - recP, 0);
    const pctP  = Math.round(recP / META_MENSAL * 100);
    const okP   = recP >= META_MENSAL;
    const corP  = okP ? '#10b981' : pctP >= 80 ? '#f59e0b' : '#ef4444';
    const nomeMes = {{jan:'Janeiro',fev:'Fevereiro',mar:'Março',abr:'Abril',mai:'Maio',jun:'Junho',jul:'Julho',ago:'Agosto',set:'Setembro',out:'Outubro',nov:'Novembro',dez:'Dezembro'}}[mesPlacar] || 'Mês atual';
    elHero.style.display = 'block';
    elHero.innerHTML =
      '<div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:14px;justify-content:space-between">' +
      '<div><div style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.04em">Placar de ' + nomeMes + ' · só vendas pagas</div>' +
      '<div style="font-size:30px;font-weight:800;color:' + corP + '">R$ ' + fmt(recP) + ' <span style="font-size:14px;color:#64748b;font-weight:600">de R$ ' + fmt(META_MENSAL) + '</span></div></div>' +
      '<div style="text-align:right"><div style="font-size:22px;font-weight:800;color:' + corP + '">' + pctP + '%</div>' +
      '<div style="font-size:12px;color:#64748b">' + (okP ? '✅ Meta batida' : 'faltam R$ ' + fmt(META_MENSAL - recP)) +
      (abertoP > 0 ? ' · R$ ' + fmt(abertoP) + ' aguardando pagamento' : '') + '</div></div></div>' +
      '<div style="margin-top:10px;height:10px;background:#f1f5f9;border-radius:999px;overflow:hidden">' +
      '<div style="height:100%;width:' + Math.min(pctP, 100) + '%;background:' + corP + ';border-radius:999px"></div></div>';
  }}
}}

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

const VEND_NAMES  = {{RAQUEL:'Raquel',RAFAEL:'Rafael',JUNIO:'Junio',CHRISTOFER:'Christofer',SUPORTE:'Suporte',MICAELLY:'Micaelly',DUDA:'Duda',BIA:'Bia'}};
const VEND_COLORS = {{RAQUEL:'#22c55e',RAFAEL:'#3b82f6',JUNIO:'#f59e0b',CHRISTOFER:'#8b5cf6',SUPORTE:'#64748b',MICAELLY:'#ec4899',DUDA:'#06b6d4',BIA:'#14b8a6'}};
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

    # Seção de Remuneração Variável (Vendedor + Suporte)
    rv_section = """
<div id="rv-section" class="main" style="padding-top:0">
  <div class="section-header">
    <div class="section-header-title">💰 Remuneração Variável</div>
    <div class="section-header-sub">Meta R$ 70.000 · Comissão da vendedora (Micaelly) · Bônus do Suporte</div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Status do Mês</div>
      <div class="chart-sub">Receita atual vs meta</div>
      <div id="rv-status"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Comissão da Vendedora (estimada)</div>
      <div class="chart-sub">Micaelly: fixo R$ 2.300 + % definido pela casa e pelo nível</div>
      <div id="rv-vendedor"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Bônus Suporte (renovação)</div>
      <div class="chart-sub">Libera apenas se meta de receita batida</div>
      <div id="rv-suporte"></div>
    </div>
  </div>
  <div class="chart-card" style="margin-bottom:16px">
    <div class="chart-title">Matriz de comissão da vendedora</div>
    <div class="chart-sub">Linha: nível na carreira · Coluna: onde a casa fecha o mês · célula atual em destaque</div>
    <div id="rv-faixas"></div>
  </div>
  <div class="charts-row" style="grid-template-columns:1fr;margin-bottom:16px">
    <div class="chart-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:14px;flex-wrap:wrap">
        <div>
          <div class="chart-title">Comissões & Cobranças</div>
          <div class="chart-sub">A pagar (vendedor / personal) + A cobrar (parceiros)</div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn-pdf" onclick="openCommissionPDF('vendedor')" style="flex-shrink:0" title="Comprovante de comissão do vendedor (regra vigente de cada um)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            Vendedor
          </button>
          <button class="btn-pdf" onclick="openCommissionPDF('personal')" style="flex-shrink:0;border-color:rgba(239,68,68,.3);color:#b91c1c" title="Repasse do personal: R$ 50 x meses do plano, pago integral no mês da venda (jul/2026+); antes, 15%">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 2h12v6h2v12H4V8h2V2z"/><path d="M9 12h6M9 16h6"/></svg>
            Personal
          </button>
          <button class="btn-pdf" onclick="openCommissionPDF('parceiro')" style="flex-shrink:0;border-color:rgba(139,92,246,.3);color:#7c3aed" title="Cobrança de parceiros: Plano Gustavo repassa R$ 50 x meses do plano, integral no mês da venda (jul/2026+); demais parceiros extrato do mês">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            Parceiros
          </button>
          <button class="btn-pdf" onclick="openCommissionPDF('renovacao')" style="flex-shrink:0;border-color:rgba(20,184,166,.35);color:#0f766e" title="Lista de pacientes com plano vencendo no mês escolhido, pra equipe de renovação trabalhar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/></svg>
            Renovações
          </button>
        </div>
      </div>
      <table class="comissoes-table">
        <thead>
          <tr>
            <th>Vendedor</th>
            <th>Vendas</th>
            <th>Faturamento</th>
            <th>Com. Vendedor</th>
            <th>Com. Treino</th>
            <th>Total Com.</th>
          </tr>
        </thead>
        <tbody id="comissoes-tbody"></tbody>
        <tfoot id="comissoes-tfoot"></tfoot>
      </table>
    </div>
  </div>
</div>
"""
    html = html.replace('<!-- bloco:pos-captacao -->', rv_section + chr(10) + '<!-- bloco:pos-captacao -->', 1)

    # Secao de Vendas Diarias
    diario_section = """
<div id="diario-section" class="main" style="padding-top:0">
  <div class="section-header">
    <div class="section-header-title">📅 Vendas por Dia</div>
    <div class="section-header-sub">Ritmo diário do mês · acompanha o filtro de mês e vendedor</div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card" style="grid-column:span 2">
      <div class="chart-title">Faturamento por dia</div>
      <div class="chart-sub" id="diario-sub">Barras: receita do dia · Linha: meta diária</div>
      <div class="chart-wrap h260"><canvas id="chartDiario"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Resumo do ritmo</div>
      <div class="chart-sub">Dias com venda no recorte</div>
      <div id="diario-resumo"></div>
    </div>
  </div>
  <div class="chart-card" style="margin-bottom:16px">
    <div class="chart-title">Detalhe dia a dia</div>
    <div class="chart-sub">Mais recente primeiro</div>
    <div id="diario-tabela"></div>
  </div>
</div>
"""
    html = html.replace('<!-- bloco:pos-visao -->', diario_section + chr(10) + '<!-- bloco:pos-visao -->', 1)

    # Secao de Renovacao, carteira e pendencias
    renov_section = """
<div id="renov-section" class="main" style="padding-top:0">
  <div class="section-header">
    <div class="section-header-title">🔄 Renovação e Carteira</div>
    <div class="section-header-sub">Renovação x venda nova · quem vence agora · o que ainda não foi pago</div>
  </div>
  <div class="charts-row charts-row-3" style="margin-bottom:16px">
    <div class="chart-card">
      <div class="chart-title">Renovação x Venda Nova</div>
      <div class="chart-sub">No recorte selecionado</div>
      <div id="renov-split"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Vendas não pagas</div>
      <div class="chart-sub">Contam na receita, não geram comissão</div>
      <div id="renov-pend"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Carteira de renovação</div>
      <div class="chart-sub">Vencidos e a vencer em 60 dias</div>
      <div id="renov-carteira-resumo"></div>
    </div>
  </div>
  <div class="chart-card" style="margin-bottom:16px">
    <div class="chart-title">Quem precisa de contato</div>
    <div class="chart-sub">Vencidos primeiro, do mais antigo para o mais recente</div>
    <div id="renov-carteira-tabela"></div>
  </div>
</div>
"""
    html = html.replace('<!-- bloco:pos-captacao -->', renov_section + chr(10) + '<!-- bloco:pos-captacao -->', 1)



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
const VENDORS_LIST = (DATA.meta && DATA.meta.vendors) ? DATA.meta.vendors : ['CHRISTOFER','RAFAEL','SUPORTE'];

// Paleta de cores para vendedores extras (além dos 3 originais)
const EXTRA_COLORS = ['#8b5cf6','#ec4899','#14b8a6','#f97316','#64748b','#ef4444'];
VENDORS_LIST.forEach((v, i) => {
  if (!VEND_COLORS[v]) VEND_COLORS[v] = EXTRA_COLORS[i % EXTRA_COLORS.length];
  if (!VEND_NAMES[v])  VEND_NAMES[v]  = v.toLowerCase().split(' ').map(w => w ? w.charAt(0).toUpperCase() + w.slice(1) : w).join(' ');
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
  // Funciona com qualquer combinacao de filtros (mes/vendedor)
  (function() {
    const MES_ORDER_LOC = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
    const MES_LBL_SHORT = {jan:'Jan',fev:'Fev',mar:'Mar',abr:'Abr',mai:'Mai',jun:'Jun',jul:'Jul',ago:'Ago',set:'Set',out:'Out',nov:'Nov',dez:'Dez'};
    function blockFor(mes) {
      if (activeVend !== 'all') {
        const b = anoData[activeVend + '_' + mes];
        if (!b) return null;
        return { v: b.fat || 0, c: b.n || 0 };
      }
      const blk = anoData[mes];
      if (blk && blk.fat !== undefined) return { v: blk.fat, c: blk.n };
      const all = anoData['all'];
      if (all && all.mes && all.mes[mes]) return { v: all.mes[mes].v || 0, c: all.mes[mes].c || 0 };
      return null;
    }
    let curMes = null, prevMes = null;
    if (activeMes === 'all') {
      const allMes = (anoData['all'] && anoData['all'].mes) || {};
      const ms = MES_ORDER_LOC.filter(m => allMes[m] && allMes[m].v > 0);
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
    const cur = curMes ? blockFor(curMes) : null;
    const prev = prevMes ? blockFor(prevMes) : null;
    if (cur && prev && prev.v > 0) {
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
  VENDORS_LIST.forEach(v => { vLblMap[v.toLowerCase()] = ' · ' + (VEND_NAMES[v] || v); });
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
    const nome = VEND_NAMES[v] || v;
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
  if(typeof renderRemuneracao === 'function') renderRemuneracao();
  if(typeof renderDiario === 'function') renderDiario();
  if(typeof renderRenovacao === 'function') renderRenovacao();
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
    const nome = VEND_NAMES[v] || v;
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

    gerar_paginas_equipe(data, timestamp)

    return OUTPUT_PATH


# =====================================================================
# PAGINAS DA EQUIPE (links separados, so com o que cada time pode ver)
# Transparencia do processo sem expor margem, custos e repasses:
# o dado sensivel NEM ENTRA no arquivo dessas paginas.
# =====================================================================
MES_ORDEM = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MES_NOME = {"jan": "Janeiro", "fev": "Fevereiro", "mar": "Março", "abr": "Abril", "mai": "Maio",
            "jun": "Junho", "jul": "Julho", "ago": "Agosto", "set": "Setembro", "out": "Outubro",
            "nov": "Novembro", "dez": "Dezembro"}
VEND_NOME = {"MICAELLY": "Micaelly", "CHRISTOFER": "Christofer", "RAFAEL": "Rafael",
             "SUPORTE": "Suporte", "OUTROS": "Outros", "JUNIO": "Junio"}
EQUIPE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f8fafc;color:#0f172a;padding-bottom:40px}
.topo{background:#0f172a;color:#fff;padding:16px 18px;display:flex;align-items:center;gap:12px}
.logo{width:38px;height:38px;border-radius:10px;background:#10b981;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px;flex-shrink:0}
.topo h1{font-size:16px;font-weight:800}.topo p{font-size:12px;color:#94a3b8}
.main{max-width:760px;margin:0 auto;padding:16px 14px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;margin-bottom:14px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
h2{font-size:12px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px}
.num{font-size:28px;font-weight:800}
.sub{font-size:12px;color:#64748b}
.bar{height:10px;background:#f1f5f9;border-radius:999px;overflow:hidden;margin-top:10px}
.bar>div{height:100%;border-radius:999px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:#64748b;padding:6px;border-bottom:2px solid #e2e8f0}
td{padding:7px 6px;border-bottom:1px solid #f1f5f9}
tr:last-child td{border-bottom:none}
.dir{text-align:right}th.dir{text-align:right}
.chip{display:inline-block;font-size:10px;font-weight:700;border-radius:999px;padding:3px 9px;white-space:nowrap}
.chip-verde{background:#dcfce7;color:#15803d}.chip-amarela{background:#fef9c3;color:#a16207}
.chip-vermelha{background:#fee2e2;color:#b91c1c}.chip-azul{background:#dbeafe;color:#1d4ed8}
.destaque{background:#fdf2f8}
.regras li{font-size:12.5px;color:#475569;margin:6px 0 6px 16px}
.rodape{text-align:center;font-size:11px;color:#94a3b8;padding:18px 14px}
.celula-atual{background:#fef9c3;font-weight:800}
@media(max-width:480px){.num{font-size:24px}td,th{padding:6px 4px}}
"""


def _brl(n, cents=False):
    s = f"{n:,.2f}" if cents else f"{round(n):,.0f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


def _pct_mica(casa):
    return 5.5 if casa >= 100000 else 4.5 if casa >= 70000 else 3.5 if casa >= 50000 else 3.0


def _com_antiga(v):
    if v <= 0:
        return 0.0
    if v <= 50000:
        return v * 0.03
    if v <= 75000:
        return v * 0.035
    if v <= 100000:
        return v * 0.04
    if v <= 125000:
        return v * 0.045
    return v * 0.05


def _pagina(titulo, sub, corpo, gerado_em):
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{titulo}</title><style>{EQUIPE_CSS}</style></head>
<body>
<div class="topo"><div class="logo">RA</div><div><h1>{titulo}</h1><p>{sub}</p></div></div>
<div class="main">
{corpo}
</div>
<div class="rodape">Atualizado automaticamente em {gerado_em} · Venda só conta quando está <strong>paga</strong> na planilha (a Obs. corrige pagamento parcial).</div>
</body></html>"""


def gerar_paginas_equipe(data: dict, timestamp: str) -> None:
    from datetime import datetime as _dt
    try:
        gerado_em = _dt.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        gerado_em = timestamp

    anos = sorted(k for k in data.keys() if k.isdigit())
    if not anos:
        return
    ano = anos[-1]
    ano_d = data[ano]
    mes = None
    for m in MES_ORDEM:
        b = ano_d.get(m)
        if isinstance(b, dict) and b.get("n"):
            mes = m
    if not mes:
        return
    bloco = ano_d[mes]
    casa = bloco.get("fat_pago", bloco.get("fat", 0))
    fat = bloco.get("fat", 0)
    aberto = max(fat - casa, 0)
    meta = 70000
    pct = round(casa / meta * 100)
    bateu = casa >= meta
    cor = "#10b981" if bateu else "#f59e0b" if pct >= 80 else "#ef4444"
    nome_mes = MES_NOME[mes]

    # ---------- PAGINA DO COMERCIAL ----------
    placar = (
        f'<div class="card"><h2>Placar de {nome_mes} · só vendas pagas</h2>'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px">'
        f'<div class="num" style="color:{cor}">R$ {_brl(casa)} <span class="sub">de R$ {_brl(meta)}</span></div>'
        f'<div style="text-align:right"><div style="font-size:20px;font-weight:800;color:{cor}">{pct}%</div>'
        f'<div class="sub">{"✅ Meta batida" if bateu else "faltam R$ " + _brl(meta - casa)}</div></div></div>'
        f'<div class="bar"><div style="width:{min(pct, 100)}%;background:{cor}"></div></div>'
        + (f'<div class="sub" style="margin-top:8px">+ R$ {_brl(aberto)} vendidos aguardando pagamento (entram quando a planilha marcar Pago)</div>' if aberto > 0 else "")
        + "</div>"
    )

    vend = bloco.get("vend", {})
    linhas = []
    ordem_v = sorted(
        ((k, v) for k, v in vend.items() if k != "-" and (v.get("v") or 0) > 0),
        key=lambda kv: -(kv[1].get("vp", kv[1].get("v", 0)) or 0),
    )
    for k, v in ordem_v:
        vp = v.get("vp", v.get("v", 0)) or 0
        destaque = ' class="destaque"' if k == "MICAELLY" else ""
        linhas.append(
            f'<tr{destaque}><td><strong>{VEND_NOME.get(k, k.title())}</strong></td>'
            f'<td class="dir">{v.get("c", 0)}</td><td class="dir">R$ {_brl(v.get("v", 0))}</td>'
            f'<td class="dir"><strong>R$ {_brl(vp)}</strong></td></tr>'
        )
    ranking = (
        f'<div class="card"><h2>Quem vendeu em {nome_mes}</h2>'
        '<table><thead><tr><th>Vendedor</th><th class="dir">Vendas</th><th class="dir">Vendido</th><th class="dir">Pago</th></tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody></table></div>'
    )

    pm = _pct_mica(casa)
    mica = vend.get("MICAELLY", {})
    mica_vp = mica.get("vp", mica.get("v", 0)) or 0
    mica_com = mica_vp * pm / 100
    tiers = {"Júnior": [3, 3.5, 4.5, 5.5], "Pleno": [3.5, 4, 5, 6], "Sênior": [4, 4.5, 5.5, 6.5]}
    col_atual = 3 if casa >= 100000 else 2 if casa >= 70000 else 1 if casa >= 50000 else 0
    cab = ["abaixo de R$ 50 mil", "R$ 50 mil", "R$ 70 mil · a meta", "R$ 100 mil"]
    mt = '<table><thead><tr><th>Nível</th>' + "".join(
        f'<th class="dir{" celula-atual" if i == col_atual else ""}">{c}</th>' for i, c in enumerate(cab)
    ) + "</tr></thead><tbody>"
    for nv, ts in tiers.items():
        mt += f'<tr><td><strong>{nv}</strong>{" · atual" if nv == "Júnior" else ""}</td>' + "".join(
            f'<td class="dir{" celula-atual" if nv == "Júnior" and i == col_atual else ""}">{str(p).replace(".", ",")}%</td>'
            for i, p in enumerate(ts)
        ) + "</tr>"
    mt += "</tbody></table>"
    chris = vend.get("CHRISTOFER", {})
    chris_vp = chris.get("vp", chris.get("v", 0)) or 0
    chris_com = _com_antiga(chris_vp)
    comissao = (
        '<div class="card"><h2>Comissão · como funciona</h2>'
        f'<div style="margin-bottom:12px"><strong>Micaelly</strong> <span class="chip chip-azul">nível Júnior</span><br>'
        '<span class="sub">O percentual vale sobre TUDO que ela vendeu e está pago no mês, e o degrau sobe quando a CASA cruza 50, 70 e 100 mil (só vendas pagas).</span><br>'
        f'<span style="font-size:15px">Agora: <strong>{str(pm).replace(".", ",")}%</strong> de R$ {_brl(mica_vp)} = '
        f'<strong style="color:#10b981">R$ {_brl(mica_com, cents=True)}</strong> <span class="sub">+ fixo R$ 2.300</span></span></div>'
        + mt +
        '<div style="margin-top:14px"><strong>Christofer</strong> <span class="sub">· regra própria: 3% a 5% sobre a própria venda paga</span><br>'
        f'<span style="font-size:15px">Estimativa do mês: <strong style="color:#10b981">R$ {_brl(chris_com, cents=True)}</strong></span></div></div>'
    )

    dias = (ano_d.get("diario", {}) or {}).get(mes, [])
    vmax = max((d.get("v", 0) for d in dias), default=0) or 1
    ritmo_linhas = "".join(
        f'<tr><td style="width:34px">{d["d"]:02d}</td>'
        f'<td><div class="bar" style="margin:0"><div style="width:{max(round(d["v"] / vmax * 100), 2)}%;background:#10b981"></div></div></td>'
        f'<td class="dir" style="width:90px">R$ {_brl(d["v"])}</td><td class="dir sub" style="width:64px">{d["n"]} venda{"s" if d["n"] != 1 else ""}</td></tr>'
        for d in dias
    )
    ritmo = (
        f'<div class="card"><h2>Ritmo de {nome_mes} · dia a dia</h2>'
        f'<table><tbody>{ritmo_linhas or "<tr><td class=sub>Sem vendas no mês ainda.</td></tr>"}</tbody></table>'
        '<div class="sub" style="margin-top:8px">Aqui é o valor VENDIDO no dia (pago ou não), pra acompanhar o ritmo.</div></div>'
    )

    regras = (
        '<div class="card"><h2>Regras do jogo</h2><ul class="regras">'
        '<li>A meta da casa é <strong>R$ 70.000/mês</strong> e só conta venda com status <strong>Pago</strong> na planilha.</li>'
        '<li>Pagamento parcial anotado na Obs. ("só pagou 200", "FALTA 197") conta só o que entrou.</li>'
        '<li>Venda pendente não gera comissão até virar Pago, e fica fora do placar da meta.</li>'
        '<li>O percentual da Micaelly sobe pra TODAS as vendas pagas dela no mês quando a casa cruza um degrau: vale puxar as últimas vendas do mês.</li>'
        '</ul></div>'
    )

    corpo_c = placar + ranking + comissao + ritmo + regras
    pagina_c = _pagina("Placar Comercial", f"Nutri Rafael Albergaria · {nome_mes}/{ano}", corpo_c, gerado_em)
    out_c = OUTPUT_PATH.parent / "equipe-comercial.html"
    out_c.write_text(pagina_c, encoding="utf-8")
    print(f"[generate] Pagina da equipe comercial: {out_c.name} ({out_c.stat().st_size / 1024:.1f} KB)")

    # ---------- PAGINA DA RENOVACAO ----------
    oper = bloco.get("oper", {}) or {}
    ren = oper.get("Renovação", {"c": 0, "v": 0})
    nova = oper.get("Nova Venda", {"c": 0, "v": 0})
    tiles = (
        f'<div class="card"><h2>{nome_mes} até agora</h2>'
        '<div style="display:flex;gap:16px;flex-wrap:wrap">'
        f'<div style="flex:1;min-width:140px"><div class="sub">Renovações</div><div class="num" style="color:#1d4ed8">{ren.get("c", 0)}</div><div class="sub">R$ {_brl(ren.get("v", 0))}</div></div>'
        f'<div style="flex:1;min-width:140px"><div class="sub">Vendas novas</div><div class="num" style="color:#15803d">{nova.get("c", 0)}</div><div class="sub">R$ {_brl(nova.get("v", 0))}</div></div>'
        '</div></div>'
    )

    bonus = (
        '<div class="card"><h2>Bônus do suporte</h2>'
        f'<div class="sub" style="margin-bottom:8px">Libera quando a casa bate R$ 70.000 no mês (só vendas pagas). Status de {nome_mes}:</div>'
        f'<div style="font-size:15px;font-weight:700;color:{cor}">{"✅ Meta batida: bônus liberado" if bateu else "🔒 R$ " + _brl(casa) + " de R$ " + _brl(meta) + " (" + str(pct) + "%)"}</div>'
        '<table style="margin-top:10px"><thead><tr><th>Taxa de renovação no mês</th><th class="dir">Bônus por pessoa</th></tr></thead>'
        '<tbody><tr><td>60% a 79%</td><td class="dir"><strong>R$ 300</strong></td></tr>'
        '<tr><td>80% ou mais</td><td class="dir"><strong>R$ 600</strong></td></tr></tbody></table></div>'
    )

    carteira = ano_d.get("carteira", []) or []
    venc_prox = [c for c in carteira if 0 <= c["dias"] <= 30]
    venc_rec = sorted([c for c in carteira if -30 <= c["dias"] < 0], key=lambda c: -c["dias"])
    venc_antigo = len([c for c in carteira if c["dias"] < -30])

    def tabela_carteira(lista, titulo, vazio):
        if not lista:
            linhas_t = f'<tr><td class="sub" colspan="4">{vazio}</td></tr>'
        else:
            linhas_t = ""
            for c in lista:
                di = c["dias"]
                if di < 0:
                    chip = f'<span class="chip chip-vermelha">venceu há {-di} dia{"s" if di != -1 else ""}</span>'
                elif di == 0:
                    chip = '<span class="chip chip-amarela">vence hoje</span>'
                elif di <= 7:
                    chip = f'<span class="chip chip-amarela">vence em {di} dia{"s" if di != 1 else ""}</span>'
                else:
                    chip = f'<span class="chip chip-verde">vence em {di} dias</span>'
                linhas_t += (
                    f'<tr><td><strong>{c["nome"]}</strong></td><td>{c["plano"].title()}</td>'
                    f'<td>{c["venc"][:5]}</td><td class="dir">{chip}</td></tr>'
                )
        return (
            f'<div class="card"><h2>{titulo}</h2>'
            '<table><thead><tr><th>Paciente</th><th>Plano</th><th>Vence</th><th class="dir">Situação</th></tr></thead>'
            f'<tbody>{linhas_t}</tbody></table></div>'
        )

    cart_html = tabela_carteira(venc_prox, f"Pra trabalhar agora · vence nos próximos 30 dias ({len(venc_prox)})", "Ninguém vencendo nos próximos 30 dias 🎉")
    cart_html += tabela_carteira(venc_rec, f"Venceu há pouco · últimos 30 dias ({len(venc_rec)})", "Ninguém vencido nos últimos 30 dias 🎉")
    if venc_antigo:
        cart_html += f'<div class="sub" style="margin:-6px 2px 14px">+ {venc_antigo} paciente(s) vencidos há mais de 30 dias ficam na rotina de vencidos, fora desta lista.</div>'

    regras_r = (
        '<div class="card"><h2>Como essa lista é montada</h2><ul class="regras">'
        '<li>Vencimento = data da última compra + duração do plano (Mensal 1, Trimestral 3, Semestral 6, Anual 12 meses).</li>'
        '<li>Quem já comprou de novo sai da lista sozinho na próxima atualização.</li>'
        '<li>Renovação conta no placar quando a venda entra na planilha como Renovação e é paga.</li>'
        '</ul></div>'
    )

    corpo_r = tiles + bonus + cart_html + regras_r
    pagina_r = _pagina("Renovação & Carteira", f"Nutri Rafael Albergaria · {nome_mes}/{ano}", corpo_r, gerado_em)
    out_r = OUTPUT_PATH.parent / "equipe-renovacao.html"
    out_r.write_text(pagina_r, encoding="utf-8")
    print(f"[generate] Pagina da equipe de renovacao: {out_r.name} ({out_r.stat().st_size / 1024:.1f} KB)")


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
