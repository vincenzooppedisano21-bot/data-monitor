"""
RACCOLTA OFFERTE DAI SITI CARRIERE DELLE AZIENDE.

Legge direttamente i portali ufficiali (Workday, Phenom...) usando
gli stessi indirizzi che usa il sito quando tu clicchi "cerca lavoro".
Sono dati pubblici e non serve alcun account.

Funziona cosi':
  1. per ogni azienda cerca le parole chiave (analyst, intern, graduate...)
  2. tiene solo gli annunci nelle citta' che hai scelto
  3. scarica la descrizione completa
  4. applica il filtro sull'esperienza (zero esperienza richiesta)
"""

import html as libreria_html
import json
import re
import time
from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup

import aziende
import config
import esperienza

INTESTAZIONI = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
}

_ultima_richiesta = 0.0


def _pausa():
    global _ultima_richiesta
    attesa = aziende.PAUSA_TRA_RICHIESTE - (time.time() - _ultima_richiesta)
    if attesa > 0:
        time.sleep(attesa)
    _ultima_richiesta = time.time()


def _pulisci(testo: str) -> str:
    return re.sub(r"\s+", " ", (testo or "")).strip()


def _testo_da_html(grezzo: str) -> str:
    """Trasforma una descrizione HTML in testo leggibile."""
    if not grezzo:
        return ""
    # alcuni portali codificano l'HTML due volte
    testo = libreria_html.unescape(libreria_html.unescape(grezzo))
    testo = re.sub(r"<(br|/p|/li|/div)[^>]*>", " ", testo, flags=re.I)
    testo = re.sub(r"<[^>]+>", " ", testo)
    return _pulisci(testo)


def _nomi_citta(citta_it: str) -> list[str]:
    """Nomi con cui la citta' puo' comparire (italiano e inglese)."""
    inglese = config.CITTA_LINKEDIN.get(citta_it, citta_it)
    nomi = {citta_it.lower(), inglese.split(",")[0].strip().lower()}
    return [n for n in nomi if n]


def citta_riconosciuta(luogo: str, citta_scelte: list[str]) -> str | None:
    """Se il luogo dell'annuncio e' una delle mie citta', la restituisce."""
    testo = (luogo or "").lower()
    if not testo:
        return None
    for citta in citta_scelte:
        if citta == "Da remoto":
            if any(p in testo for p in ("remote", "da remoto", "anywhere")):
                return citta
            continue
        if any(nome in testo for nome in _nomi_citta(citta)):
            return citta
    return None


def _data_da_postedon(testo: str) -> str:
    """Converte «Posted 3 Days Ago» in una data vera."""
    t = (testo or "").lower()
    oggi = date.today()
    if "today" in t or "oggi" in t:
        return oggi.isoformat()
    if "yesterday" in t or "ieri" in t:
        return (oggi - timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\+?\s*(day|days|giorn)", t)
    if m:
        return (oggi - timedelta(days=int(m.group(1)))).isoformat()
    m = re.search(r"(\d+)\+?\s*(month|mese|mesi)", t)
    if m:
        return (oggi - timedelta(days=int(m.group(1)) * 30)).isoformat()
    return ""


# ---------------------------------------------------------------
# PIATTAFORMA WORKDAY
# ---------------------------------------------------------------
def _workday_cerca(azienda: dict, parola: str, massimo: int) -> list[dict]:
    base = f"https://{azienda['host']}/wday/cxs/{azienda['tenant']}/{azienda['sito']}"
    trovati = []

    for scarto in range(0, massimo, 20):
        _pausa()
        try:
            r = requests.post(f"{base}/jobs", headers=INTESTAZIONI, timeout=25,
                              json={"appliedFacets": {}, "limit": 20,
                                    "offset": scarto, "searchText": parola})
        except requests.RequestException:
            break
        if r.status_code != 200:
            break

        annunci = r.json().get("jobPostings", [])
        if not annunci:
            break

        for a in annunci:
            percorso = a.get("externalPath", "")
            codice = (a.get("bulletFields") or [""])[0] or percorso.rsplit("_", 1)[-1]
            trovati.append({
                "id": f"wd-{azienda['tenant']}-{codice}",
                "titolo": _pulisci(a.get("title", "")),
                "azienda": azienda["nome"],
                "luogo_esteso": _pulisci(a.get("locationsText", "")),
                "settore": azienda["settore"],
                "fonte": azienda["nome"],
                "data_pubblicazione": _data_da_postedon(a.get("postedOn", "")),
                "link": f"https://{azienda['host']}/en-US/{azienda['sito']}{percorso}",
                "_percorso": percorso,
                "_base": base,
            })

        if len(annunci) < 20:
            break
    return trovati


def _workday_dettaglio(offerta: dict) -> dict:
    _pausa()
    try:
        r = requests.get(f"{offerta['_base']}{offerta['_percorso']}",
                         headers=INTESTAZIONI, timeout=25)
        if r.status_code != 200:
            return {}
        info = r.json().get("jobPostingInfo", {})
    except (requests.RequestException, ValueError):
        return {}

    return {
        "descrizione": _testo_da_html(info.get("jobDescription", "")),
        "data_pubblicazione": info.get("startDate") or offerta.get("data_pubblicazione", ""),
        "luogo_esteso": _pulisci(info.get("location", "")) or offerta.get("luogo_esteso", ""),
        "tipo_impiego": _pulisci(info.get("timeType", "")),
    }


# ---------------------------------------------------------------
# PIATTAFORMA PHENOM
# ---------------------------------------------------------------
def _phenom_cerca(azienda: dict, parola: str, massimo: int) -> list[dict]:
    trovati = []
    for scarto in range(0, massimo, 20):
        _pausa()
        corpo = {
            "lang": "en_global", "deviceType": "desktop", "country": "global",
            "pageName": "search-results", "ddoKey": "refineSearch", "sortBy": "",
            "subsearch": "", "from": scarto, "jobs": True, "counts": True,
            "all_fields": ["category", "country", "state", "city", "type"],
            "size": 20, "clearAll": False, "jdsource": "facets",
            "isSliderEnable": False, "pageId": "page16", "siteType": "external",
            "keywords": parola, "global": True, "selected_fields": {},
            "sort": {"order": "", "field": ""}, "locationData": {},
        }
        try:
            r = requests.post(f"https://{azienda['host']}/widgets",
                              headers={**INTESTAZIONI, "Content-Type": "application/json"},
                              json=corpo, timeout=25)
        except requests.RequestException:
            break
        if r.status_code != 200:
            break

        annunci = r.json().get("refineSearch", {}).get("data", {}).get("jobs", [])
        if not annunci:
            break

        for a in annunci:
            luogo = a.get("location") or ", ".join(
                x for x in (a.get("city"), a.get("state"), a.get("country")) if x)
            trovati.append({
                "id": f"ph-{azienda['host'].split('.')[1]}-{a.get('jobId')}",
                "titolo": _pulisci(a.get("title", "")),
                "azienda": azienda["nome"],
                "luogo_esteso": _pulisci(luogo),
                "settore": azienda["settore"],
                "fonte": azienda["nome"],
                "data_pubblicazione": (a.get("postedDate") or "")[:10],
                "link": a.get("applyUrl", ""),
                "descrizione": _pulisci(a.get("descriptionTeaser", "")),
            })

        if len(annunci) < 20:
            break
    return trovati


def _descrizione_da_pagina(url: str) -> str:
    """
    Legge la descrizione completa da una pagina web.
    Quasi tutti i portali includono i dati dell'annuncio in un blocco
    strutturato (JSON-LD) pensato proprio per essere letto dai programmi.
    """
    if not url:
        return ""
    _pausa()
    try:
        r = requests.get(url, headers=INTESTAZIONI, timeout=25)
        if r.status_code != 200:
            return ""
    except requests.RequestException:
        return ""

    pagina = BeautifulSoup(r.text, "lxml")
    for blocco in pagina.select('script[type="application/ld+json"]'):
        try:
            dati = json.loads(blocco.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        for elemento in (dati if isinstance(dati, list) else [dati]):
            if isinstance(elemento, dict) and elemento.get("@type") == "JobPosting":
                return _testo_da_html(elemento.get("description", ""))
    return ""


def _distribuisci(offerte: list[dict], massimo: int) -> list[dict]:
    """
    Sceglie quali annunci leggere per intero, a turno tra le aziende.
    Senza questo, un'azienda con centinaia di offerte (es. Deutsche Bank)
    consumerebbe tutto il budget e le altre non verrebbero mai lette.
    """
    per_azienda: dict[str, list[dict]] = {}
    for o in offerte:
        per_azienda.setdefault(o["azienda"], []).append(o)

    scelte, giro = [], 0
    while len(scelte) < massimo:
        aggiunto = False
        for lista in per_azienda.values():
            if giro < len(lista) and len(scelte) < massimo:
                scelte.append(lista[giro])
                aggiunto = True
        if not aggiunto:
            break
        giro += 1
    return scelte


# ---------------------------------------------------------------
# RACCOLTA COMPLETA
# ---------------------------------------------------------------
def raccogli(citta_scelte, settori_scelti=None, giorni=30,
             solo_entry_level=True, avanzamento=None):
    """
    Passa in rassegna tutti i portali aziendali e restituisce le offerte
    adatte, gia' filtrate per citta' ed esperienza richiesta.
    """
    def avvisa(frazione, messaggio):
        if avanzamento:
            avanzamento(min(max(frazione, 0.0), 1.0), messaggio)

    elenco = aziende.AZIENDE
    if settori_scelti:
        elenco = [a for a in elenco if a["settore"] in settori_scelti]
    if not elenco:
        return [], {"cercate": 0, "trovate": 0, "scartate": 0, "portali": 0}

    limite = date.today() - timedelta(days=giorni)
    grezze, viste = [], set()

    # --- Fase 1: interrogo i portali ---
    for i, azienda in enumerate(elenco):
        avvisa(i / len(elenco) * 0.45,
               f"Leggo il portale di {azienda['nome']} ({azienda['etichetta']})…")

        cerca = _workday_cerca if azienda["piattaforma"] == "workday" else _phenom_cerca
        raccolte = []
        for parola in aziende.PAROLE_RICERCA:
            try:
                raccolte += cerca(azienda, parola, aziende.MAX_PER_AZIENDA)
            except Exception:
                continue

        for o in raccolte:
            if o["id"] in viste:
                continue
            viste.add(o["id"])

            # tengo solo le citta' che mi interessano
            citta = citta_riconosciuta(o["luogo_esteso"], citta_scelte)
            if not citta:
                continue
            o["citta"] = citta

            # e solo gli annunci abbastanza recenti
            if o["data_pubblicazione"]:
                try:
                    if datetime.fromisoformat(o["data_pubblicazione"][:10]).date() < limite:
                        continue
                except ValueError:
                    pass

            grezze.append(o)

    # --- Fase 2: tengo solo i ruoli che mi interessano ---
    candidate, scartate = [], 0
    for o in grezze:
        # il titolo deve parlare di un ruolo adatto a me
        if not esperienza.contiene(o["titolo"], aziende.RUOLI_AMMESSI):
            scartate += 1
            continue
        # e non deve essere palesemente senior
        if solo_entry_level and not esperienza.valuta(o["titolo"])["adatta"]:
            scartate += 1
            continue
        candidate.append(o)

    candidate = _distribuisci(candidate, aziende.MAX_DETTAGLI)

    # --- Fase 3: leggo le descrizioni e applico il filtro esperienza ---
    buone = []
    for i, o in enumerate(candidate):
        avvisa(0.45 + i / max(len(candidate), 1) * 0.55,
               f"Leggo l'annuncio {i + 1} di {len(candidate)} ({o['azienda']})…")

        if "_base" in o:                      # Workday
            o.update({k: v for k, v in _workday_dettaglio(o).items() if v})
        elif not o.get("descrizione") or len(o["descrizione"]) < 400:
            piena = _descrizione_da_pagina(o.get("link", ""))
            if piena:
                o["descrizione"] = piena

        o.pop("_base", None)
        o.pop("_percorso", None)

        v = esperienza.valuta(o["titolo"], o.get("descrizione", ""), "")
        o["tipo_esperienza"] = v["tipo"]
        o["anni_richiesti"] = v["anni"]
        o["motivo_esperienza"] = v["motivo"]
        o["anzianita"] = ""

        if solo_entry_level and not v["adatta"]:
            scartate += 1
            continue
        buone.append(o)

    avvisa(1.0, "Fatto!")
    return buone, {"cercate": len(grezze), "trovate": len(buone),
                   "scartate": scartate, "portali": len(elenco)}
