"""
ACCENSIONE E SPEGNIMENTO DEL GUARDIANO.

Il guardiano e' un'attivita' programmata di macOS (si chiama "LaunchAgent")
che esegue sorveglianza.py ogni 15 minuti, anche quando la dashboard e' chiusa.

Questo file contiene i comandi per accenderlo, spegnerlo e sapere come sta.
"""

import getpass
import plistlib
import subprocess
import time
from pathlib import Path

ETICHETTA = "com.jobradar.guardiano"
CARTELLA = Path(__file__).parent
MODELLO = CARTELLA / "com.jobradar.guardiano.plist"
INSTALLATO = Path.home() / "Library" / "LaunchAgents" / f"{ETICHETTA}.plist"


def _utente_id() -> str:
    return subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip()


def attivo() -> bool:
    """Il guardiano e' in funzione?"""
    esito = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    return ETICHETTA in esito.stdout


def intervallo_minuti() -> int | None:
    if not INSTALLATO.exists():
        return None
    try:
        with INSTALLATO.open("rb") as f:
            return plistlib.load(f).get("StartInterval", 900) // 60
    except Exception:
        return None


def accendi(minuti: int = 15) -> tuple[bool, str]:
    """Installa e avvia il guardiano."""
    if not MODELLO.exists():
        return False, "Manca il file di configurazione com.jobradar.guardiano.plist"

    with MODELLO.open("rb") as f:
        configurazione = plistlib.load(f)
    configurazione["StartInterval"] = max(5, minuti) * 60

    INSTALLATO.parent.mkdir(parents=True, exist_ok=True)
    with INSTALLATO.open("wb") as f:
        plistlib.dump(configurazione, f)

    # se era gia' in funzione lo fermo, poi lo riavvio con i nuovi tempi
    subprocess.run(["launchctl", "bootout", f"gui/{_utente_id()}/{ETICHETTA}"],
                   capture_output=True, text=True)
    esito = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{_utente_id()}", str(INSTALLATO)],
        capture_output=True, text=True)

    if esito.returncode != 0 and not attivo():
        return False, (esito.stderr or esito.stdout or "").strip()[:200]
    return True, f"Guardiano attivo: controlla ogni {minuti} minuti."


def spegni() -> tuple[bool, str]:
    esito = subprocess.run(["launchctl", "bootout", f"gui/{_utente_id()}/{ETICHETTA}"],
                           capture_output=True, text=True)
    if INSTALLATO.exists():
        INSTALLATO.unlink()

    # launchctl impiega un attimo a fermarlo davvero: gli do qualche secondo
    for _ in range(6):
        if not attivo():
            return True, "Guardiano spento."
        time.sleep(0.5)
    return False, (esito.stderr or "Non sono riuscito a fermarlo").strip()[:200]


def ultime_righe(quante: int = 12) -> str:
    registro = CARTELLA / "guardiano.log"
    if not registro.exists():
        return "Nessun controllo ancora eseguito."
    righe = registro.read_text(errors="replace").splitlines()
    return "\n".join(righe[-quante:]) or "Registro vuoto."
