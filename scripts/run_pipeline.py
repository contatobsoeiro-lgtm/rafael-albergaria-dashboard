"""
run_pipeline.py
─────────────────────────────────────────────────────────────
Orquestrador do pipeline completo:
  1. fetch_data   → baixa e processa a planilha
  2. generate_html → injeta dados no template HTML
  3. notify       → envia notificação de atualização

Execute localmente:
  python scripts/run_pipeline.py

No GitHub Actions, é chamado automaticamente pelo workflow.
─────────────────────────────────────────────────────────────
"""

import sys
import traceback
from pathlib import Path

# Garante que o diretório scripts está no path
sys.path.insert(0, str(Path(__file__).parent))

import fetch_data
import generate_html
import notify as notifier


def run():
    print("=" * 60)
    print("🚀 Dashboard Rafael Albergaria — Pipeline de Atualização")
    print("=" * 60)

    # ── ETAPA 1: Buscar e processar dados ─────────────────────
    print("\n📥 [1/3] Buscando dados da planilha...")
    try:
        result = fetch_data.main()
        data      = result["data"]
        records   = result["records"]
        timestamp = result["timestamp"]
        fat_total = data["all"]["fat"]
        print(f"    ✅ {records} registros · faturamento total: R$ {fat_total:,.0f}")
    except Exception as e:
        print(f"\n❌ ERRO na etapa 1 (fetch_data): {e}")
        traceback.print_exc()
        sys.exit(1)

    # ── ETAPA 2: Gerar HTML ───────────────────────────────────
    print("\n🔧 [2/3] Gerando HTML do dashboard...")
    try:
        output_path = generate_html.generate(data, records, timestamp)
        size_kb     = output_path.stat().st_size / 1024
        print(f"    ✅ HTML gerado: {output_path.name} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"\n❌ ERRO na etapa 2 (generate_html): {e}")
        traceback.print_exc()
        sys.exit(1)

    # ── ETAPA 3: Notificar ────────────────────────────────────
    print("\n📨 [3/3] Enviando notificação...")
    try:
        results = notifier.notify(records, fat_total, timestamp)
        for channel, ok in results.items():
            status = "✅" if ok else "❌"
            print(f"    {status} {channel}")
    except Exception as e:
        # Falha na notificação NÃO deve travar o pipeline
        print(f"    ⚠️  Aviso: erro na notificação (não crítico) — {e}")

    print("\n" + "=" * 60)
    print("✅ Pipeline concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    run()
