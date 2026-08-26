"""
INVIO DELLE EMAIL DI AVVISO.

Usa smtplib, il modulo di Python per spedire email, collegandosi
al server di Gmail con la "Password per le App".

La connessione e' cifrata (SSL sulla porta 465): la password non
viaggia mai in chiaro.
"""

import html
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

import impostazioni

SERVER = "smtp.gmail.com"
PORTA = 465


class EmailNonInviata(Exception):
    pass


def _colore(match: int) -> str:
    if match >= 45:
        return "#10b981"
    if match >= 25:
        return "#f59e0b"
    return "#64748b"


def _scheda(o: dict) -> str:
    acc = _colore(o.get("match", 0))
    competenze = "".join(
        f'<span style="display:inline-block;background:#e6fffa;color:#0d9488;'
        f'border:1px solid #99f6e4;border-radius:6px;padding:2px 7px;'
        f'font-size:12px;margin:2px 3px 0 0">{html.escape(c)}</span>'
        for c in (o.get("competenze") or [])
    )
    tipo = o.get("tipo_esperienza", "")
    colore_tipo = "#7c3aed" if tipo == "Internship" else "#64748b"

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px 0;
           border:1px solid #e5e7eb;border-left:4px solid {acc};border-radius:12px;
           background:#ffffff">
      <tr><td style="padding:16px 18px">
        <div style="font-size:11px;font-weight:700;letter-spacing:.5px;
                    text-transform:uppercase;color:{colore_tipo};margin-bottom:6px">
          {html.escape(tipo)} &nbsp;·&nbsp; {html.escape(o.get('settore',''))}
        </div>
        <div style="font-size:17px;font-weight:700;color:#111827;line-height:1.3">
          {html.escape(o.get('titolo',''))}
        </div>
        <div style="font-size:14px;color:#374151;margin-top:4px">
          <b>{html.escape(o.get('azienda',''))}</b>
          &nbsp;·&nbsp; 📍 {html.escape(o.get('luogo_esteso') or o.get('citta',''))}
        </div>
        <div style="font-size:13px;color:{acc};font-weight:600;margin-top:8px">
          ⏱ {html.escape(o.get('motivo_esperienza',''))}
          &nbsp;·&nbsp; Match {o.get('match',0)}%
        </div>
        <div style="margin-top:8px">{competenze}</div>
        <div style="margin-top:14px">
          <a href="{html.escape(o.get('link','#'), quote=True)}"
             style="display:inline-block;background:#4f46e5;color:#ffffff;
                    text-decoration:none;font-size:14px;font-weight:700;
                    padding:10px 20px;border-radius:8px">Candidati subito →</a>
        </div>
      </td></tr>
    </table>"""


def componi(offerte: list[dict]) -> tuple[str, str, str]:
    """Prepara oggetto, testo semplice e versione grafica dell'email."""
    n = len(offerte)
    stage = sum(1 for o in offerte if o.get("tipo_esperienza") == "Internship")
    aziende_citate = ", ".join(dict.fromkeys(o.get("azienda", "") for o in offerte))[:70]

    oggetto = (f"🎯 {n} nuova offerta: {aziende_citate}" if n == 1
               else f"🎯 {n} nuove offerte — {aziende_citate}…")

    righe = [f"{o.get('titolo')} — {o.get('azienda')} ({o.get('citta')})\n"
             f"  {o.get('motivo_esperienza')} · Match {o.get('match',0)}%\n"
             f"  {o.get('link')}\n" for o in offerte]
    testo = ("JOB RADAR — nuove offerte compatibili con il tuo profilo\n\n"
             + "\n".join(righe))

    grafica = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;
      background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
      <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px">
        <table width="100%" style="max-width:620px" cellpadding="0" cellspacing="0">
          <tr><td style="padding-bottom:18px">
            <div style="font-size:26px;font-weight:800;color:#4f46e5;letter-spacing:-.5px">
              🎯 Job Radar</div>
            <div style="font-size:14px;color:#6b7280;margin-top:4px">
              {n} nuova offerta compatibile{'' if n == 1 else 'i'} con il tuo profilo
              {f' · {stage} stage' if stage else ''}
              &nbsp;·&nbsp; {datetime.now().strftime('%d/%m/%Y alle %H:%M')}
            </div>
          </td></tr>
          <tr><td>{''.join(_scheda(o) for o in offerte)}</td></tr>
          <tr><td style="padding-top:10px;font-size:12px;color:#9ca3af;line-height:1.6">
            Sei tra i primi a vedere questi annunci: candidarsi presto aumenta
            molto le probabilità di essere selezionati.<br>
            Messaggio generato dal tuo Job Radar in esecuzione sul tuo Mac.
          </td></tr>
        </table>
      </td></tr></table></body></html>"""

    return oggetto, testo, grafica


def invia(offerte: list[dict], destinatario: str = "", password: str = ""):
    """Spedisce l'email con le nuove offerte."""
    if not offerte:
        return False

    destinatario = destinatario or impostazioni.leggi_email()
    password = password or (impostazioni.leggi_password(destinatario) or "")

    if not destinatario or not password:
        raise EmailNonInviata(
            "Indirizzo email o Password per le App mancanti: "
            "configurali nella dashboard."
        )

    oggetto, testo, grafica = componi(offerte)
    messaggio = EmailMessage()
    messaggio["Subject"] = oggetto
    messaggio["From"] = destinatario
    messaggio["To"] = destinatario
    messaggio.set_content(testo)
    messaggio.add_alternative(grafica, subtype="html")

    try:
        contesto = ssl.create_default_context()
        with smtplib.SMTP_SSL(SERVER, PORTA, context=contesto, timeout=30) as server:
            server.login(destinatario, password.replace(" ", ""))
            server.send_message(messaggio)
    except smtplib.SMTPAuthenticationError:
        raise EmailNonInviata(
            "Gmail ha rifiutato la password. Assicurati di aver incollato la "
            "«Password per le App» di 16 lettere, non la password normale di Google."
        )
    except (smtplib.SMTPException, OSError) as errore:
        raise EmailNonInviata(f"Invio non riuscito: {errore}")

    return True


def invia_prova(destinatario: str, password: str):
    """Email di verifica, per controllare che la configurazione funzioni."""
    esempio = [{
        "titolo": "Summer Analyst — Investment Banking",
        "azienda": "Esempio Bank", "citta": "Milano",
        "luogo_esteso": "Milano, Italia", "settore": "Investment Banking",
        "tipo_esperienza": "Internship", "match": 62,
        "motivo_esperienza": "Stage / internship: nessuna esperienza richiesta",
        "competenze": ["Financial Modelling", "Valuation", "M&A"],
        "link": "https://example.com/offerta-di-prova",
    }]
    oggetto, testo, grafica = componi(esempio)
    messaggio = EmailMessage()
    messaggio["Subject"] = "✅ Job Radar — email di prova"
    messaggio["From"] = destinatario
    messaggio["To"] = destinatario
    messaggio.set_content("Se leggi questo messaggio, le notifiche funzionano.\n\n" + testo)
    messaggio.add_alternative(grafica, subtype="html")

    try:
        with smtplib.SMTP_SSL(SERVER, PORTA, context=ssl.create_default_context(),
                              timeout=30) as server:
            server.login(destinatario, password.replace(" ", ""))
            server.send_message(messaggio)
    except smtplib.SMTPAuthenticationError:
        raise EmailNonInviata(
            "Gmail ha rifiutato la password. Serve la «Password per le App» "
            "di 16 lettere generata da Google, non la tua password abituale."
        )
    except (smtplib.SMTPException, OSError) as errore:
        raise EmailNonInviata(f"Invio non riuscito: {errore}")
    return True
