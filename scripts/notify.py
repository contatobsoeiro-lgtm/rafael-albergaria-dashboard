"""
notify.py
─────────────────────────────────────────────────────────────
Envia notificação de atualização do dashboard via:
  1. Telegram Bot
  2. Webhook
  3. WhatsApp API (via CallMeBot)
─────────────────────────────────────────────────────────────
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import quote

NOTIFY_CHANNEL = os.getenv("NOTIFY_CHANNEL", "whatsapp")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WA_PHONE = os.getenv("WHATSAPP_PHONE", "")
WA_APIKEY = os.getenv("WHATSAPP_APIKEY", "")


def build_message(records, fat_total, timestamp, problemas=None):
    dt = datetime.fromisoformat(timestamp)
    date_str = dt.strftime("%d/%m/%Y")
    fat_str = f"R$ {fat_total:,.0f}".replace(",", ".")
    msg = (
        f"✅ *Dashboard de Vendas atualizado!*\n\n"
        f"📅 {date_str}\n"
        f"📋 {records} registros\n"
        f"💰 Faturamento: {fat_str}\n\n"
        f"🔗 Acesse: {DASHBOARD_URL}"
    )
    if problemas:
        msg += (
            f"\n\n⚠️ {len(problemas)} venda(s) ficaram FORA do dash "
            f"por erro de digitacao na planilha:\n"
        )
        msg += "\n".join(f"- {p}" for p in problemas[:8])
        if len(problemas) > 8:
            msg += f"\n(e mais {len(problemas) - 8})"
    return msg


def send_whatsapp(message):
    if not WA_PHONE or not WA_APIKEY:
        return False
    plain = message.replace("*", "").replace("_", "")
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={quote(plain)}&apikey={WA_APIKEY}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return True
    except Exception:
        return False


def notify(records, fat_total, timestamp, problemas=None):
    message = build_message(records, fat_total, timestamp, problemas)
    results = {}
    if "whatsapp" in NOTIFY_CHANNEL.lower():
        results["whatsapp"] = send_whatsapp(message)
    return results


def _falha_anterior():
    """True se o run anterior do workflow tambem falhou (evita spam no WhatsApp)."""
    repo = os.getenv("GITHUB_REPOSITORY", "")
    if not repo:
        return False
    try:
        url = (f"https://api.github.com/repos/{repo}/actions/workflows/"
               f"update.yml/runs?per_page=1&status=completed")
        r = requests.get(url, timeout=15)
        runs = r.json().get("workflow_runs", [])
        return bool(runs) and runs[0].get("conclusion") == "failure"
    except Exception:
        return False


def notify_erro(erro):
    """Avisa no WhatsApp que o robo quebrou. So no PRIMEIRO run que falha."""
    if _falha_anterior():
        print("[notify] Run anterior ja tinha falhado, aviso ja foi enviado.")
        return {}
    msg = (
        "🚨 Dashboard de Vendas NAO atualizou!\n\n"
        "O robo falhou ao ler a planilha. O dash continua no ar, "
        "mas congelado nos ultimos dados bons.\n\n"
        f"Motivo tecnico: {str(erro)[:300]}\n\n"
        "Quase sempre foi cabecalho ou celula mexida na aba Vendas."
    )
    results = {}
    if "whatsapp" in NOTIFY_CHANNEL.lower():
        results["whatsapp"] = send_whatsapp(msg)
    return results

