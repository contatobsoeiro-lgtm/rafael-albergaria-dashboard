# 🚀 Guia de Configuração — Dashboard Rafael Albergaria
## Versão: 2025 + 2026 + Comparativo YoY | WhatsApp

---

## Checklist de Configuração (15 minutos total)

- [ ] 1. Criar repositório no GitHub
- [ ] 2. Fazer upload dos arquivos
- [ ] 3. Publicar link do Google Sheets
- [ ] 4. Ativar CallMeBot no WhatsApp do Rafael
- [ ] 5. Configurar Secrets no GitHub
- [ ] 6. Ativar GitHub Pages
- [ ] 7. Testar manualmente

---

## Passo 1 — Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `rafael-albergaria-dashboard`
3. Visibilidade: **Public** (obrigatório para GitHub Pages gratuito)
4. Clique em **Create repository**

---

## Passo 2 — Fazer upload dos arquivos

```bash
# Terminal (recomendado)
cd automacao-dashboard
git init
git add .
git commit -m "feat: dashboard multi-ano 2025+2026"
git remote add origin https://github.com/SEU-USUARIO/rafael-albergaria-dashboard.git
git push -u origin main
```

---

## Passo 3 — Link da planilha OneDrive

SHEET_URL=https://1drv.ms/x/c/924648235f649026/IQCULRz9IMOkQpZPqFUayi-SAc6B76nshG_9nswvbkxQXv8?e=CbceLr

---

## Passo 4 — Ativar CallMeBot

Número: +55 27 99766-7931
1. Adicionar +34 644 62 58 62 no celular
2. Enviar: I allow callmebot to send me messages
3. Salvar API Key como WHATSAPP_APIKEY

---

## Passo 5 — Secrets no GitHub

| Secret | Valor |
|--------|-------|
| SHEET_URL | https://1drv.ms/x/c/924648235f649026/IQCULRz9IMOkQpZPqFUayi-SAc6B76nshG_9nswvbkxQXv8?e=CbceLr |
| SHEET_TYPE | onedrive |
| NOTIFY_CHANNEL | whatsapp |
| WHATSAPP_PHONE | 5527997667931 |
| WHATSAPP_APIKEY | API Key CallMeBot |

---

## Passo 6 — GitHub Pages

1. Settings > Pages
2. Source: Deploy from a branch
3. Branch: main / /docs
4. Save
