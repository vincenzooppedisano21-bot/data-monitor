"""
ARCHIVIO DELLE OFFERTE.

Le offerte trovate vengono salvate in un piccolo archivio sul tuo computer
(il file "offerte.db"). Cosi':
  - la dashboard si apre subito, senza dover ricontattare LinkedIn ogni volta
  - le offerte gia' viste non vengono duplicate
  - possiamo sapere quali sono NUOVE rispetto all'ultimo controllo
    (servira' per il briefing giornaliero via email)
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

PERCORSO = Path(__file__).parent / "offerte.db"

CREAZIONE = """
CREATE TABLE IF NOT EXISTS offerte (
    id                TEXT PRIMARY KEY,
    titolo            TEXT,
    azienda           TEXT,
    citta             TEXT,
    luogo_esteso      TEXT,
    settore           TEXT,
    fonte             TEXT,
    descrizione       TEXT,
    link              TEXT,
    data_pubblicazione TEXT,
    anzianita         TEXT,
    tipo_esperienza   TEXT,
    anni_richiesti    INTEGER,
    motivo_esperienza TEXT,
    match             INTEGER,
    competenze        TEXT,
    trovata_il        TEXT,
    inviata_via_email INTEGER DEFAULT 0
);
"""


def _connetti():
    c = sqlite3.connect(PERCORSO)
    c.row_factory = sqlite3.Row
    return c


def inizializza():
    with _connetti() as c:
        c.execute(CREAZIONE)
        # Se l'archivio era stato creato con una versione precedente,
        # aggiungo le colonne mancanti senza perdere i dati gia' salvati.
        presenti = {r[1] for r in c.execute("PRAGMA table_info(offerte)")}
        for colonna, tipo in [("anzianita", "TEXT"), ("tipo_impiego", "TEXT")]:
            if colonna not in presenti:
                c.execute(f"ALTER TABLE offerte ADD COLUMN {colonna} {tipo}")


def salva(offerte: list[dict]) -> int:
    """
    Salva le offerte nell'archivio.
    Restituisce quante erano davvero NUOVE (mai viste prima).
    """
    inizializza()
    adesso = datetime.now().isoformat(timespec="seconds")
    nuove = 0

    with _connetti() as c:
        for o in offerte:
            gia_presente = c.execute(
                "SELECT 1 FROM offerte WHERE id = ?", (o["id"],)
            ).fetchone()

            if gia_presente:
                # aggiorno solo i dati che possono cambiare
                c.execute(
                    "UPDATE offerte SET match = ?, competenze = ?, settore = ? WHERE id = ?",
                    (o.get("match", 0), json.dumps(o.get("competenze", [])),
                     o.get("settore", ""), o["id"]),
                )
                continue

            c.execute(
                """INSERT INTO offerte
                   (id, titolo, azienda, citta, luogo_esteso, settore, fonte,
                    descrizione, link, data_pubblicazione, anzianita, tipo_impiego,
                    tipo_esperienza, anni_richiesti, motivo_esperienza,
                    match, competenze, trovata_il)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    o["id"], o.get("titolo", ""), o.get("azienda", ""),
                    o.get("citta", ""), o.get("luogo_esteso", ""),
                    o.get("settore", ""), o.get("fonte", "LinkedIn"),
                    o.get("descrizione", ""), o.get("link", ""),
                    o.get("data_pubblicazione", ""), o.get("anzianita", ""),
                    o.get("tipo_impiego", ""), o.get("tipo_esperienza", ""),
                    o.get("anni_richiesti"), o.get("motivo_esperienza", ""),
                    o.get("match", 0), json.dumps(o.get("competenze", [])), adesso,
                ),
            )
            nuove += 1

    return nuove


def leggi() -> list[dict]:
    """Restituisce tutte le offerte archiviate, dalla piu' recente."""
    inizializza()
    with _connetti() as c:
        righe = c.execute(
            "SELECT * FROM offerte ORDER BY trovata_il DESC, match DESC"
        ).fetchall()

    offerte = []
    for r in righe:
        o = dict(r)
        try:
            o["competenze"] = json.loads(o["competenze"] or "[]")
        except json.JSONDecodeError:
            o["competenze"] = []
        offerte.append(o)
    return offerte


def ultimo_aggiornamento() -> str | None:
    inizializza()
    with _connetti() as c:
        r = c.execute("SELECT MAX(trovata_il) AS q FROM offerte").fetchone()
    return r["q"] if r and r["q"] else None


def svuota():
    """Cancella tutto l'archivio (utile per ripartire da zero)."""
    inizializza()
    with _connetti() as c:
        c.execute("DELETE FROM offerte")


# ===============================================================
# GESTIONE DELLE NOTIFICHE EMAIL
# ===============================================================
def da_notificare() -> list[dict]:
    """Offerte mai segnalate via email."""
    return [o for o in leggi() if not o.get("inviata_via_email")]


def segna_inviate(identificativi: list[str]):
    """Segna come 'gia' avvisata' un elenco di offerte."""
    if not identificativi:
        return
    inizializza()
    with _connetti() as c:
        c.executemany("UPDATE offerte SET inviata_via_email = 1 WHERE id = ?",
                      [(i,) for i in identificativi])


def segna_tutte_inviate():
    """
    Segna l'intero archivio come gia' notificato.
    Si usa quando attivi le notifiche per la prima volta, cosi' non ti
    arriva un'email con tutte le offerte gia' presenti.
    """
    inizializza()
    with _connetti() as c:
        c.execute("UPDATE offerte SET inviata_via_email = 1")


# ===============================================================
# MEMORIA DEL GUARDIANO
# Cose che il guardiano deve ricordare tra un giro e l'altro
# (es. quando ha controllato l'ultima volta i portali aziendali).
# Stanno qui dentro e non in un file separato, cosi' viaggiano
# insieme all'archivio anche quando il guardiano gira su GitHub.
# ===============================================================
def _crea_stato(c):
    c.execute("CREATE TABLE IF NOT EXISTS stato (chiave TEXT PRIMARY KEY, valore TEXT)")


def salva_stato(chiave: str, valore: str):
    inizializza()
    with _connetti() as c:
        _crea_stato(c)
        c.execute("INSERT INTO stato (chiave, valore) VALUES (?, ?) "
                  "ON CONFLICT(chiave) DO UPDATE SET valore = excluded.valore",
                  (chiave, valore))


def leggi_stato(chiave: str, predefinito: str = "") -> str:
    inizializza()
    with _connetti() as c:
        _crea_stato(c)
        r = c.execute("SELECT valore FROM stato WHERE chiave = ?", (chiave,)).fetchone()
    return r["valore"] if r else predefinito
