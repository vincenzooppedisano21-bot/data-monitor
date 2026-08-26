"""
RACCOLTA OFFERTE DA LINKEDIN.

Usa la pagina pubblica delle offerte, quella che chiunque puo' vedere
SENZA fare login. Quindi il tuo account non viene mai usato e non corre
alcun rischio di blocco.

Per rispetto verso il sito (ed evitare di essere rallentati) le richieste
sono distanziate di qualche secondo l'una dall'altra.
"""

import random
import re
import time

import requests
from bs4 import BeautifulSoup

import config
import esperienza

URL_ELENCO = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
URL_DETTAGLIO = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"

INTESTAZIONI = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
}

_ultima_richiesta = 0.0


class LinkedInOccupato(Exception):
    """LinkedIn ci sta chiedendo di rallentare."""


def _pausa():
    """Aspetta il tempo necessario prima della prossima richiesta."""
    global _ultima_richiesta
    trascorso = time.time() - _ultima_richiesta
    attesa = config.PAUSA_TRA_RICHIESTE - trascorso
    if attesa > 0:
        time.sleep(attesa + random.uniform(0, 0.8))
    _ultima_richiesta = time.time()


def _scarica(url: str, params: dict | None = None, tentativi: int = 3) -> str | None:
    """Scarica una pagina, con pause e nuovi tentativi se il sito rallenta."""
    for n in range(tentativi):
        _pausa()
        try:
            r = requests.get(url, params=params, headers=INTESTAZIONI, timeout=25)
        except requests.RequestException:
            time.sleep(3 * (n + 1))
            continue

        if r.status_code == 200:
            return r.text
        if r.status_code in (429, 999, 403):
            # LinkedIn chiede di rallentare: aspetto sempre di piu'
            time.sleep(10 * (n + 1))
            continue
        if r.status_code == 404:
            return None
    raise LinkedInOccupato(
        "LinkedIn sta limitando le richieste. Riprova tra qualche minuto."
    )


def _pulisci(testo: str) -> str:
    return re.sub(r"\s+", " ", (testo or "")).strip()


def _nomi_citta(citta_it: str) -> list[str]:
    """
    Nomi con cui la citta' puo' comparire su LinkedIn.
    Es. per "Milano" -> ["milan", "milano"]
    """
    inglese = config.CITTA_LINKEDIN.get(citta_it, citta_it)
    nomi = {citta_it.lower(), inglese.split(",")[0].strip().lower()}
    return [n for n in nomi if n]


def cerca(query: str, citta_it: str, giorni: int = 7, massimo: int = 25) -> list[dict]:
    """
    Cerca su LinkedIn le offerte per una parola chiave in una citta'.
    Restituisce la lista delle schede trovate (senza descrizione completa).
    """
    luogo = config.CITTA_LINKEDIN.get(citta_it, citta_it)
    risultati, viste = [], set()

    for inizio in range(0, massimo, 10):
        parametri = {
            "keywords": query,
            "location": luogo,
            "f_E": config.LIVELLI_LINKEDIN,
            "f_TPR": f"r{giorni * 86400}",
            "start": inizio,
        }
        if citta_it == "Da remoto":
            parametri["f_WT"] = "2"  # solo lavoro da remoto

        html_pagina = _scarica(URL_ELENCO, parametri)
        if not html_pagina:
            break

        schede = BeautifulSoup(html_pagina, "lxml").select("div.base-card")
        if not schede:
            break

        for scheda in schede:
            urn = scheda.get("data-entity-urn", "")
            id_offerta = urn.split(":")[-1] if urn else ""
            if not id_offerta or id_offerta in viste:
                continue
            viste.add(id_offerta)

            titolo_el = scheda.select_one("h3.base-search-card__title")
            azienda_el = scheda.select_one("h4.base-search-card__subtitle")
            luogo_el = scheda.select_one("span.job-search-card__location")
            data_el = scheda.select_one("time")
            link_el = scheda.select_one("a.base-card__full-link")

            luogo_testo = _pulisci(luogo_el.get_text()) if luogo_el else ""

            # Scarto le offerte troppo lontane dalla citta' richiesta
            if citta_it != "Da remoto":
                atteso = _nomi_citta(citta_it)
                if not any(n in luogo_testo.lower() for n in atteso):
                    continue

            risultati.append({
                "id": id_offerta,
                "titolo": _pulisci(titolo_el.get_text()) if titolo_el else "",
                "azienda": _pulisci(azienda_el.get_text()) if azienda_el else "",
                "citta": citta_it,
                "luogo_esteso": luogo_testo,
                "data_pubblicazione": data_el.get("datetime", "") if data_el else "",
                "link": (link_el.get("href", "").split("?")[0] if link_el else ""),
                "fonte": "LinkedIn",
            })

        if len(schede) < 10:
            break  # ultima pagina

    return risultati


def dettaglio(id_offerta: str) -> dict:
    """Scarica la descrizione completa e il livello di anzianita' dell'offerta."""
    html_pagina = _scarica(URL_DETTAGLIO.format(id_offerta))
    if not html_pagina:
        return {"descrizione": "", "anzianita": "", "tipo_impiego": ""}

    pagina = BeautifulSoup(html_pagina, "lxml")
    blocco = pagina.select_one("div.description__text, div.show-more-less-html__markup")
    descrizione = _pulisci(blocco.get_text(" ", strip=True)) if blocco else ""

    criteri = {}
    etichette = pagina.select("h3.description__job-criteria-subheader")
    valori = pagina.select("span.description__job-criteria-text")
    for e, v in zip(etichette, valori):
        criteri[_pulisci(e.get_text()).lower()] = _pulisci(v.get_text())

    return {
        "descrizione": descrizione,
        "anzianita": criteri.get("livello di anzianità", criteri.get("seniority level", "")),
        "tipo_impiego": criteri.get("tipo di impiego", criteri.get("employment type", "")),
    }


def raccogli(citta_scelte, settori_scelti, giorni=7, solo_entry_level=True, avanzamento=None):
    """
    Raccolta completa: per ogni citta' e ogni settore cerca su LinkedIn,
    scarica le descrizioni e applica il filtro sull'esperienza.

    'avanzamento' e' una funzione opzionale che viene chiamata per aggiornare
    la barra di avanzamento nella dashboard.
    """
    def avvisa(frazione, messaggio):
        if avanzamento:
            avanzamento(frazione, messaggio)

    coppie = [(c, s) for c in citta_scelte for s in settori_scelti]
    if not coppie:
        return [], {"cercate": 0, "trovate": 0, "scartate": 0}

    grezze, viste = [], set()

    # --- Fase 1: cerco gli annunci ---
    for i, (citta, settore) in enumerate(coppie):
        query = config.QUERY_PER_SETTORE.get(settore, settore)
        avvisa(i / len(coppie) * 0.5, f"Cerco «{query}» a {citta}…")
        try:
            for o in cerca(query, citta, giorni, config.MAX_PER_RICERCA):
                if o["id"] in viste:
                    continue
                viste.add(o["id"])
                o["settore"] = settore
                grezze.append(o)
        except LinkedInOccupato:
            avvisa(0.5, "LinkedIn ha rallentato le richieste: mi fermo qui.")
            break

    # --- Fase 2: scarico le descrizioni complete ---
    # Prima scarto gia' quelle con un titolo palesemente senior,
    # cosi' non sprechiamo richieste inutili.
    candidate = []
    scartate = 0
    for o in grezze:
        pre = esperienza.valuta(o["titolo"])
        if solo_entry_level and not pre["adatta"]:
            scartate += 1
            continue
        candidate.append(o)

    candidate = candidate[: config.MAX_DETTAGLI]
    buone = []
    for i, o in enumerate(candidate):
        avvisa(0.5 + i / max(len(candidate), 1) * 0.5,
               f"Leggo l'annuncio {i + 1} di {len(candidate)}…")
        try:
            d = dettaglio(o["id"])
        except LinkedInOccupato:
            avvisa(1.0, "LinkedIn ha rallentato: salvo quello che ho raccolto.")
            break

        o.update(d)
        v = esperienza.valuta(o["titolo"], d["descrizione"], d["anzianita"])
        o["tipo_esperienza"] = v["tipo"]
        o["anni_richiesti"] = v["anni"]
        o["motivo_esperienza"] = v["motivo"]

        if solo_entry_level and not v["adatta"]:
            scartate += 1
            continue
        buone.append(o)

    avvisa(1.0, "Fatto!")
    return buone, {"cercate": len(grezze), "trovate": len(buone), "scartate": scartate}
