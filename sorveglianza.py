"""
IL GUARDIANO.

Questo programma fa un giro di controllo: cerca nuove offerte,
le salva in archivio e — se ce ne sono di nuove e compatibili —
ti manda subito un'email.

Viene lanciato automaticamente dal Mac ogni 15 minuti (vedi il file
com.jobradar.guardiano.plist), ma puoi anche eseguirlo a mano:

    cd ~/job-radar && .venv/bin/python sorveglianza.py

Per non appesantire i siti, il giro e' "leggero":
  - LinkedIn viene controllato a ogni giro (solo le ultime ore)
  - i portali aziendali una volta all'ora
"""

import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# permette di lanciarlo da qualunque cartella
sys.path.insert(0, str(Path(__file__).parent))

import aziende
import config
import database
import impostazioni
import linkedin
import notifiche
import siti_aziende

REGISTRO = Path(__file__).parent / "guardiano.log"

# Un giro di controllo deve essere veloce: alzo poco alla volta
MAX_RICERCA_VELOCE = 10
MAX_DETTAGLI_VELOCE = 25
MINUTI_TRA_CONTROLLI_AZIENDE = 60


def annota(messaggio: str):
    riga = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {messaggio}"
    print(riga, flush=True)
    with REGISTRO.open("a") as f:
        f.write(riga + "\n")


def _punteggio(titolo: str, descrizione: str) -> tuple[int, list[str]]:
    testo = f"{titolo} {descrizione}".lower()
    trovate = [c for c in config.COMPETENZE if c.lower() in testo]
    massimo = sum(config.COMPETENZE.values())
    punti = sum(config.COMPETENZE[c] for c in trovate)
    return (round(punti / massimo * 100) if massimo else 0), trovate


def _tocca_controllare_aziende(conf: dict) -> bool:
    ultimo = (database.leggi_stato("ultimo_controllo_aziende")
              or conf.get("ultimo_controllo_aziende") or "")
    if not ultimo:
        return True
    try:
        passato = datetime.fromisoformat(ultimo)
    except ValueError:
        return True
    return datetime.now() - passato > timedelta(minutes=MINUTI_TRA_CONTROLLI_AZIENDE)


def notifiche_accese(conf: dict) -> bool:
    """
    Le notifiche sono attive se le hai accese dalla dashboard
    oppure se e' impostata la variabile JOBRADAR_NOTIFICHE
    (e' cosi' che le accendiamo quando il guardiano gira su GitHub).
    """
    da_ambiente = os.environ.get("JOBRADAR_NOTIFICHE", "").strip().lower()
    if da_ambiente in ("1", "true", "si", "sì", "yes"):
        return True
    return bool(conf.get("notifiche_attive"))


def giro_di_controllo() -> dict:
    conf = impostazioni.leggi()

    citta = list(config.CITTA_TARGET) if conf["solo_target"] else list(config.CITTA)
    settori = list(config.SETTORI_TARGET) if conf["solo_target"] else list(config.SETTORI)

    trovate = []

    # ---------- LinkedIn (a ogni giro) ----------
    limite_originale = config.MAX_PER_RICERCA, config.MAX_DETTAGLI
    config.MAX_PER_RICERCA, config.MAX_DETTAGLI = MAX_RICERCA_VELOCE, MAX_DETTAGLI_VELOCE
    try:
        parziali, stat = linkedin.raccogli(
            citta_scelte=citta, settori_scelti=settori,
            giorni=conf["giorni_linkedin"], solo_entry_level=True)
        trovate += parziali
        annota(f"LinkedIn: {stat['cercate']} esaminati, {stat['trovate']} adatti")
    except Exception as errore:
        annota(f"LinkedIn non raggiungibile: {errore}")
    finally:
        config.MAX_PER_RICERCA, config.MAX_DETTAGLI = limite_originale

    # ---------- Portali aziendali (una volta all'ora) ----------
    if _tocca_controllare_aziende(conf):
        originale = aziende.MAX_DETTAGLI
        aziende.MAX_DETTAGLI = 30
        try:
            parziali, stat = siti_aziende.raccogli(
                citta_scelte=citta, settori_scelti=settori,
                giorni=7, solo_entry_level=True)
            trovate += parziali
            annota(f"Portali aziendali: {stat['cercate']} esaminati, "
                   f"{stat['trovate']} adatti")
            database.salva_stato("ultimo_controllo_aziende", datetime.now().isoformat())
            try:
                impostazioni.salva({"ultimo_controllo_aziende": datetime.now().isoformat()})
            except OSError:
                pass   # su GitHub il file non è scrivibile: non è un problema
        except Exception as errore:
            annota(f"Portali aziendali non raggiungibili: {errore}")
        finally:
            aziende.MAX_DETTAGLI = originale

    # ---------- Archivio ----------
    for o in trovate:
        o["match"], o["competenze"] = _punteggio(o["titolo"], o.get("descrizione", ""))
    nuove = database.salva(trovate)
    database.salva_stato("ultimo_controllo", datetime.now().isoformat())
    try:
        impostazioni.salva({"ultimo_controllo": datetime.now().isoformat()})
    except OSError:
        pass

    # ---------- Notifica ----------
    inviate = 0
    if notifiche_accese(conf):
        candidate = [
            o for o in database.da_notificare()
            if o.get("tipo_esperienza") in conf["tipi_da_notificare"]
            and (o.get("match") or 0) >= conf["match_minimo"]
        ]
        # le piu' promettenti per prime, al massimo 15 per email
        candidate.sort(key=lambda o: o.get("match") or 0, reverse=True)
        candidate = candidate[:15]

        if candidate:
            try:
                notifiche.invia(candidate)
                database.segna_inviate([o["id"] for o in candidate])
                inviate = len(candidate)
                annota(f"📧 Email inviata con {inviate} offerte")
            except notifiche.EmailNonInviata as errore:
                annota(f"Email NON inviata: {errore}")
        else:
            # niente da segnalare: marco comunque quelle non idonee
            escluse = [o["id"] for o in database.da_notificare()]
            database.segna_inviate(escluse)

    annota(f"Giro completato: {len(trovate)} offerte adatte, {nuove} nuove, "
           f"{inviate} segnalate via email")
    return {"trovate": len(trovate), "nuove": nuove, "inviate": inviate}


def sorveglia_in_continuo():
    """
    Modalita' server: resta acceso e ripete il giro all'infinito.
    Su Linux e' cosi' che il guardiano lavora 24 ore su 24
    (su macOS ci pensa invece l'attivita' programmata di Apple).
    """
    conf = impostazioni.leggi()
    minuti = max(5, conf.get("frequenza_minuti", 15))
    annota(f"🟢 Guardiano avviato in modalità continua: un giro ogni {minuti} minuti")

    errori_di_fila = 0
    while True:
        inizio = time.time()
        try:
            giro_di_controllo()
            errori_di_fila = 0
        except KeyboardInterrupt:
            annota("Guardiano fermato a mano.")
            return
        except Exception:
            errori_di_fila += 1
            annota(f"ERRORE nel giro (#{errori_di_fila}):\n" + traceback.format_exc())
            # dopo errori ripetuti aspetto di piu', per non insistere a vuoto
            time.sleep(min(errori_di_fila, 6) * 60)

        # rileggo le preferenze: se cambi la frequenza non serve riavviare
        minuti = max(5, impostazioni.leggi().get("frequenza_minuti", 15))
        attesa = minuti * 60 - (time.time() - inizio)
        if attesa > 0:
            time.sleep(attesa)


if __name__ == "__main__":
    if "--continuo" in sys.argv:
        sorveglia_in_continuo()
    else:
        try:
            giro_di_controllo()
        except Exception:
            annota("ERRORE IMPREVISTO:\n" + traceback.format_exc())
            sys.exit(1)
