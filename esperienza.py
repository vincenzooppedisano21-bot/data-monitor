"""
FILTRO ESPERIENZA.

Il mio profilo: neolaureata con una summer internship di 3 mesi.
Quindi cerco SOLO offerte che non richiedono esperienza lavorativa
pregressa: internship, stage, graduate programme, entry level puro.

Il modulo legge titolo e descrizione dell'annuncio e distingue:

  - requisito RIGIDO   -> "richiesti 2 anni di esperienza"      = SCARTA
  - requisito GRADITO  -> "1 anno di esperienza è un plus"      = TIENE
  - mesi invece di anni -> "6 mesi di esperienza"               = confronta
                                                                  con i miei 3
"""

import re

import config

# Limiti presi dal profilo (modificabili in config.py)
MAX_ANNI = config.MAX_ANNI_ESPERIENZA     # 0 = nessuna esperienza richiesta
MAX_MESI = config.MAX_MESI_ESPERIENZA     # 3 = la mia summer internship

# ---------------------------------------------------------------
# Parole che indicano un ruolo TROPPO SENIOR
# ---------------------------------------------------------------
PAROLE_SENIOR = [
    "senior", "sr", "lead", "team lead", "head of", "director", "direttore",
    "manager", "managing", "principal", "vice president", "vp", "chief",
    "partner", "executive", "dirigente", "responsabile", "capo",
    "expert", "esperto", "staff", "mid-level", "experienced",
]

# ---------------------------------------------------------------
# Parole che confermano STAGE / ENTRY LEVEL
# ---------------------------------------------------------------
# Nel TITOLO basta la parola: e' un segnale forte
PAROLE_STAGE_TITOLO = [
    "intern", "interns", "internship", "stage", "stagiaire", "tirocinio",
    "tirocinante", "praktikum", "becario", "prácticas", "practicas",
    "apprentice", "apprendistato", "summer analyst", "off-cycle",
    "working student", "summer intern",
]
# Nel TESTO uso solo espressioni non ambigue
PAROLE_STAGE_TESTO = [
    "internship", "internships", "tirocinio", "stage curricolare",
    "stage extracurricolare", "summer internship", "programma di stage",
    "contratto di stage", "praktikum",
]

PAROLE_ENTRY_TITOLO = [
    "junior", "jr", "graduate", "trainee", "entry level", "entry-level",
    "new grad", "campus", "neolaureati", "neolaureato", "neolaureata",
]
PAROLE_ENTRY_TESTO = [
    "entry level", "entry-level", "graduate programme", "graduate program",
    "neolaureat", "recent graduate", "fresh graduate", "no experience",
    "nessuna esperienza", "primo impiego", "early career", "school leaver",
    "starting your career", "laureandi", "new graduate",
]

# ---------------------------------------------------------------
# Livelli di anzianita' dichiarati da LinkedIn
# ---------------------------------------------------------------
ANZIANITA_OK = {
    "stage", "tirocinio", "internship", "livello base", "entry level",
    "praktikum", "prácticas", "apprendistato",
}
# Nota: "Associate" NON e' qui dentro di proposito. In PwC, KPMG o EY
# l'Associate e' il ruolo d'ingresso per neolaureati, mentre in McKinsey
# e' un ruolo post-MBA. Non posso scartarlo a priori: lascio decidere
# alla descrizione dell'annuncio.
ANZIANITA_NO = {
    "livello medio-alto", "mid-senior level", "direttore", "director",
    "dirigente", "executive", "esperto",
}

# ---------------------------------------------------------------
# Riconoscimento della durata richiesta
# ---------------------------------------------------------------
NUMERI_A_PAROLE = {
    "zero": 0, "one": 1, "uno": 1, "un": 1, "due": 2, "two": 2, "dos": 2,
    "tre": 3, "three": 3, "tres": 3, "quattro": 4, "four": 4,
    "cinque": 5, "five": 5, "sei": 6, "six": 6, "sette": 7, "seven": 7,
    "otto": 8, "eight": 8, "dieci": 10, "ten": 10,
}
_NUM = r"(?:\d{1,2}|" + "|".join(NUMERI_A_PAROLE) + r")"

REGEX_ANNI = re.compile(
    rf"\b({_NUM})\s*(?:\+|plus)?\s*(?:[-–/]|to|a|au)?\s*(?:\d{{1,2}})?\s*(?:\+)?\s*"
    r"(?:years?|yrs?|anni|anno|años|año|ans|jahre?)\b",
    re.IGNORECASE,
)
REGEX_MESI = re.compile(
    rf"\b({_NUM})\s*(?:\+)?\s*(?:[-–/]|to|a)?\s*(?:\d{{1,2}})?\s*(?:\+)?\s*"
    r"(?:months?|mesi|mese|meses|mois|monate)\b",
    re.IGNORECASE,
)

# La cifra conta solo se nella stessa frase si parla di esperienza
PAROLE_ESPERIENZA = [
    "experience", "esperienza", "experiencia", "expérience", "erfahrung",
    "background", "track record", "seniority", "working in", "worked in",
]

# Frasi che dicono "non serve esperienza"
PAROLE_ZERO_ESPERIENZA = [
    "no experience", "no prior experience", "without experience",
    "no previous experience", "nessuna esperienza", "senza esperienza",
    "non è richiesta esperienza", "non e' richiesta esperienza",
    "no se requiere experiencia", "sin experiencia",
]

# Se la cifra parla di studi (non di lavoro) va ignorata
PAROLE_STUDI = [
    "degree", "laurea", "università", "universita", "university", "bachelor",
    "master", "studies", "studi", "diploma", "corso di", "programme lasts",
    "durata", "carrera", "contratto di", "internship lasts", "lo stage dura",
]

# Il requisito e' solo GRADITO, non obbligatorio
PAROLE_GRADITO = [
    "is a plus", "a plus", "nice to have", "preferred", "preferable",
    "preferably", "desirable", "welcome", "bonus", "advantage",
    "gradito", "gradita", "preferibile", "preferibilmente", "apprezzata",
    "apprezzato", "costituisce titolo preferenziale", "titolo preferenziale",
    "valore aggiunto", "considerado un plus", "valorable",
]

# Se dopo "preferibilmente" arriva una preposizione, la parola si riferisce
# a un settore o a un luogo, non agli anni di esperienza. Esempio:
#   "Esperienza tra 1 e 3 anni, preferibilmente in consulenza"
#    -> gli anni RESTANO obbligatori, il "preferibilmente" riguarda il settore.
DOPO_GRADITO_NON_VALE = [
    "in ", "nel ", "nella ", "presso ", "per ", "su ", "con ", "en ",
    "dans ", "im ", "at ", "within ", "from ",
]


def _e_davvero_gradito(intorno: str) -> bool:
    """
    Controlla se il requisito e' davvero facoltativo.
    Scarta i casi in cui "preferibilmente" si riferisce al settore
    invece che agli anni di esperienza.
    """
    for parola in PAROLE_GRADITO:
        posizione = intorno.find(parola)
        if posizione == -1:
            continue
        seguito = intorno[posizione + len(parola):].lstrip(" ,;:")
        if any(seguito.startswith(x) for x in DOPO_GRADITO_NON_VALE):
            continue  # riguarda il settore, non gli anni
        return True
    return False


def contiene(testo: str, parole: list[str]) -> str | None:
    """
    Cerca le parole come PAROLE INTERE, non come pezzi di altre parole.
    Cosi' "intern" non viene trovato dentro "international" o "internal".
    Restituisce la prima parola trovata, oppure None.
    """
    if not testo:
        return None
    testo = testo.lower()
    for parola in parole:
        schema = r"\b" + re.escape(parola.lower()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(schema, testo):
            return parola
    return None


def _numero(testo: str) -> int | None:
    testo = testo.strip().lower()
    if testo.isdigit():
        return int(testo)
    return NUMERI_A_PAROLE.get(testo)


def _frasi(descrizione: str) -> list[str]:
    testo = re.sub(r"\s+", " ", descrizione.lower())
    return re.split(r"[.;•\n\r]|•", testo)


def analizza_requisiti(descrizione: str) -> dict:
    """
    Legge la descrizione e restituisce:
      anni_rigidi / mesi_rigidi   -> requisiti obbligatori (i piu' bassi trovati)
      anni_graditi                -> requisiti indicati come "preferenziali"
      zero_esperienza             -> True se l'annuncio dice che non serve esperienza
    """
    vuoto = {"anni_rigidi": None, "mesi_rigidi": None,
             "anni_graditi": None, "zero_esperienza": False}
    if not descrizione:
        return vuoto

    testo = re.sub(r"\s+", " ", descrizione.lower())
    if any(p in testo for p in PAROLE_ZERO_ESPERIENZA):
        vuoto["zero_esperienza"] = True
        return vuoto

    anni_rigidi, anni_graditi, mesi_rigidi = [], [], []

    for frase in _frasi(descrizione):
        if not any(p in frase for p in PAROLE_ESPERIENZA):
            continue
        for regex, lista_rigidi in ((REGEX_ANNI, anni_rigidi), (REGEX_MESI, mesi_rigidi)):
            for m in regex.finditer(frase):
                vicino = frase[max(0, m.start() - 45): m.end() + 45]
                if any(p in vicino for p in PAROLE_STUDI):
                    continue  # parla di studi, non di lavoro

                # "gradito/preferenziale" conta solo se sta vicino alla cifra,
                # non in un altro punto della frase
                intorno = frase[max(0, m.start() - 70): m.end() + 70]
                gradito = _e_davvero_gradito(intorno)
                n = _numero(m.group(1))
                if n is None or not (0 <= n <= 20):
                    continue
                if gradito and regex is REGEX_ANNI:
                    anni_graditi.append(n)
                elif gradito:
                    continue
                else:
                    lista_rigidi.append(n)

    return {
        "anni_rigidi": min(anni_rigidi) if anni_rigidi else None,
        "mesi_rigidi": min(mesi_rigidi) if mesi_rigidi else None,
        "anni_graditi": min(anni_graditi) if anni_graditi else None,
        "zero_esperienza": False,
    }


def valuta(titolo: str, descrizione: str = "", anzianita: str = "") -> dict:
    """
    Decide se l'offerta e' compatibile con un profilo SENZA esperienza.

    Restituisce:
      adatta -> True/False
      tipo   -> "Internship", "Entry level" o "Da verificare"
      anni   -> anni di esperienza richiesti (None se non indicati)
      motivo -> spiegazione in italiano
    """
    t = (titolo or "").lower()
    d = (descrizione or "").lower()
    anz = (anzianita or "").strip().lower()

    e_stage = bool(contiene(t, PAROLE_STAGE_TITOLO) or contiene(d, PAROLE_STAGE_TESTO))
    e_entry = bool(contiene(t, PAROLE_ENTRY_TITOLO) or contiene(d, PAROLE_ENTRY_TESTO))

    req = analizza_requisiti(descrizione)
    anni = 0 if req["zero_esperienza"] else req["anni_rigidi"]

    # ---------------- Motivi per SCARTARE ----------------
    senior_nel_titolo = contiene(t, PAROLE_SENIOR)
    if senior_nel_titolo and not e_stage:
        return {"adatta": False, "tipo": "Senior", "anni": anni,
                "motivo": f"Titolo da ruolo con esperienza («{senior_nel_titolo.strip()}»)"}

    if anz in ANZIANITA_NO and not e_stage:
        return {"adatta": False, "tipo": "Senior", "anni": anni,
                "motivo": f"LinkedIn la classifica come «{anzianita}»"}

    if req["anni_rigidi"] is not None and req["anni_rigidi"] > MAX_ANNI:
        n = req["anni_rigidi"]
        return {"adatta": False, "tipo": "Con esperienza", "anni": n,
                "motivo": f"Richiede {n} anno di esperienza"
                          if n == 1 else f"Richiede {n} anni di esperienza"}

    if req["mesi_rigidi"] is not None and req["mesi_rigidi"] > MAX_MESI:
        n = req["mesi_rigidi"]
        return {"adatta": False, "tipo": "Con esperienza", "anni": anni,
                "motivo": f"Richiede {n} mesi di esperienza (tu ne hai {MAX_MESI})"}

    # ---------------- Motivi per TENERE ----------------
    if e_stage:
        tipo = "Internship"
    elif e_entry or anz in ANZIANITA_OK or req["zero_esperienza"]:
        tipo = "Entry level"
    else:
        tipo = "Da verificare"

    if req["zero_esperienza"]:
        motivo = "L'annuncio dice esplicitamente che non serve esperienza"
    elif req["anni_graditi"] is not None:
        n = req["anni_graditi"]
        motivo = (f"{n} anno di esperienza gradito ma non obbligatorio" if n == 1
                  else f"{n} anni di esperienza graditi ma non obbligatori")
    elif req["mesi_rigidi"] is not None:
        motivo = f"Richiede {req['mesi_rigidi']} mesi: compatibile con la tua internship"
    elif tipo == "Internship":
        motivo = "Stage / internship: nessuna esperienza richiesta"
    elif tipo == "Entry level":
        motivo = "Indicata come entry level / graduate"
    else:
        motivo = "L'annuncio non dichiara requisiti di esperienza: da controllare"

    return {"adatta": True, "tipo": tipo, "anni": anni, "motivo": motivo}
