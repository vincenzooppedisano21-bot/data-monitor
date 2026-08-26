"""
IMPOSTAZIONI DELLE NOTIFICHE EMAIL.

Le preferenze (indirizzo, filtri, frequenza) finiscono in un file
"impostazioni.json" dentro la cartella del progetto.

La PASSWORD invece non viene MAI scritta su file: la salviamo nel
Portachiavi di macOS, lo stesso posto dove il Mac custodisce le tue
password del browser. Solo il tuo utente puo' rileggerla.
"""

import json
import os
from pathlib import Path

PERCORSO = Path(__file__).parent / "impostazioni.json"
SEGRETI = Path(__file__).parent / "segreti.env"
SERVIZIO = "job-radar"   # nome con cui la password compare nel Portachiavi

# Il Portachiavi esiste solo su macOS. Su un server Linux non c'e':
# li' la password si legge dal file protetto "segreti.env".
try:
    import keyring
    PORTACHIAVI = True
except ImportError:
    keyring = None
    PORTACHIAVI = False

PREDEFINITE = {
    "email": "",
    "notifiche_attive": False,
    "tipi_da_notificare": ["Internship", "Entry level"],
    "match_minimo": 0,
    "frequenza_minuti": 15,
    "giorni_linkedin": 1,
    "solo_target": True,
    "ultimo_controllo_aziende": "",
    "ultimo_controllo": "",
}


def leggi() -> dict:
    dati = dict(PREDEFINITE)
    if PERCORSO.exists():
        try:
            dati.update(json.loads(PERCORSO.read_text()))
        except json.JSONDecodeError:
            pass
    return dati


def salva(nuove: dict):
    dati = leggi()
    dati.update(nuove)
    PERCORSO.write_text(json.dumps(dati, indent=2, ensure_ascii=False))
    return dati


# ---------------------------------------------------------------
# PASSWORD
#
# Viene cercata in tre posti, in quest'ordine:
#   1. le variabili d'ambiente          (utile per Docker)
#   2. il file "segreti.env"            (usato sul server Linux)
#   3. il Portachiavi di macOS          (usato sul tuo Mac)
# ---------------------------------------------------------------
def _leggi_segreti() -> dict:
    """Legge il file segreti.env, se esiste."""
    dati = {}
    if not SEGRETI.exists():
        return dati
    for riga in SEGRETI.read_text().splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("#") or "=" not in riga:
            continue
        chiave, valore = riga.split("=", 1)
        dati[chiave.strip()] = valore.strip().strip('"').strip("'")
    return dati


def salva_password(email: str, password: str):
    password = password.replace(" ", "")
    if PORTACHIAVI:
        keyring.set_password(SERVIZIO, email, password)
    else:
        scrivi_segreti(email, password)


def scrivi_segreti(email: str, password: str):
    """Scrive email e password nel file protetto (server senza Portachiavi)."""
    SEGRETI.write_text(
        "# Credenziali di Job Radar — NON condividere questo file.\n"
        f"JOBRADAR_EMAIL={email}\n"
        f"JOBRADAR_PASSWORD={password.replace(' ', '')}\n"
    )
    SEGRETI.chmod(0o600)   # leggibile solo dal proprietario


def leggi_password(email: str = "") -> str | None:
    dalla_ambiente = os.environ.get("JOBRADAR_PASSWORD")
    if dalla_ambiente:
        return dalla_ambiente.replace(" ", "")

    dal_file = _leggi_segreti().get("JOBRADAR_PASSWORD")
    if dal_file:
        return dal_file.replace(" ", "")

    if PORTACHIAVI and email:
        return keyring.get_password(SERVIZIO, email)
    return None


def leggi_email() -> str:
    return (os.environ.get("JOBRADAR_EMAIL")
            or _leggi_segreti().get("JOBRADAR_EMAIL")
            or leggi().get("email", ""))


def cancella_password(email: str):
    if PORTACHIAVI:
        try:
            keyring.delete_password(SERVIZIO, email)
        except Exception:
            pass
    if SEGRETI.exists():
        SEGRETI.unlink()


def configurate() -> bool:
    """True se email e password sono a posto."""
    email = leggi_email()
    return bool(email and leggi_password(email))
