"""
ELENCO DELLE AZIENDE DA MONITORARE SUI LORO SITI CARRIERE.

Ogni azienda usa un portale diverso. Le piattaforme piu' diffuse
(Workday, Phenom, Greenhouse, Lever) hanno un modo standard per
consultare le offerte: per quelle il programma legge tutto da solo.

Alcune aziende (McKinsey, Bain, Kearney...) bloccano le letture
automatiche: per quelle trovi un LINK DIRETTO nella dashboard,
cosi' le controlli a mano in un clic.

Ogni voce e' stata verificata: rispondono tutte davvero.
"""

# ===============================================================
# AZIENDE LETTE AUTOMATICAMENTE
# ===============================================================
AZIENDE = [
    # --- Investment banking / M&A ---
    {
        "nome": "Houlihan Lokey",
        "etichetta": "Campus & Summer Analyst",
        "settore": "Investment Banking",
        "piattaforma": "workday",
        "host": "hl.wd1.myworkdayjobs.com", "tenant": "hl", "sito": "Campus",
    },
    {
        "nome": "Houlihan Lokey",
        "etichetta": "Posizioni aperte",
        "settore": "Investment Banking",
        "piattaforma": "workday",
        "host": "hl.wd1.myworkdayjobs.com", "tenant": "hl", "sito": "Lateral",
    },
    {
        "nome": "Rothschild & Co",
        "etichetta": "Stage",
        "settore": "M&A",
        "piattaforma": "workday",
        "host": "rothschildandco.wd3.myworkdayjobs.com",
        "tenant": "rothschildandco", "sito": "Rothschildandco_Interns",
    },
    {
        "nome": "Rothschild & Co",
        "etichetta": "Posizioni aperte",
        "settore": "M&A",
        "piattaforma": "workday",
        "host": "rothschildandco.wd3.myworkdayjobs.com",
        "tenant": "rothschildandco", "sito": "RothschildAndCo_Lateral",
    },
    {
        "nome": "PJT Partners",
        "etichetta": "Carriere",
        "settore": "M&A",
        "piattaforma": "workday",
        "host": "pjtpartners.wd1.myworkdayjobs.com",
        "tenant": "pjtpartners", "sito": "Careers",
    },
    {
        "nome": "Moelis & Company",
        "etichetta": "Carriere",
        "settore": "M&A",
        "piattaforma": "workday",
        "host": "moelis.wd1.myworkdayjobs.com",
        "tenant": "moelis", "sito": "Experienced-Hires",
    },
    {
        "nome": "Barclays",
        "etichetta": "Carriere globali",
        "settore": "Investment Banking",
        "piattaforma": "workday",
        "host": "barclays.wd3.myworkdayjobs.com",
        "tenant": "barclays", "sito": "External_Career_Site_Barclays",
    },
    {
        "nome": "Deutsche Bank",
        "etichetta": "Carriere globali",
        "settore": "Investment Banking",
        "piattaforma": "workday",
        "host": "db.wd3.myworkdayjobs.com", "tenant": "db", "sito": "DBWebsite",
    },
    {
        "nome": "Citi",
        "etichetta": "Carriere globali",
        "settore": "Investment Banking",
        "piattaforma": "workday",
        "host": "citi.wd5.myworkdayjobs.com", "tenant": "citi", "sito": "2",
    },

    # --- Consulenza / Transaction services ---
    {
        "nome": "PwC",
        "etichetta": "Carriere globali",
        "settore": "Transaction Services & Deal Advisory",
        "piattaforma": "workday",
        "host": "pwc.wd3.myworkdayjobs.com",
        "tenant": "pwc", "sito": "Global_Experienced_Careers",
    },
    {
        "nome": "Boston Consulting Group",
        "etichetta": "Carriere globali",
        "settore": "Consulenza Strategica",
        "piattaforma": "phenom",
        "host": "careers.bcg.com",
    },
]

# ===============================================================
# AZIENDE DA CONTROLLARE A MANO
# I loro siti bloccano le letture automatiche: la dashboard ti
# mostra il pulsante per aprirle direttamente.
# ===============================================================
AZIENDE_LINK_DIRETTO = [
    {"nome": "McKinsey & Company", "settore": "Consulenza Strategica",
     "url": "https://www.mckinsey.com/careers/search-jobs"},
    {"nome": "Bain & Company", "settore": "Consulenza Strategica",
     "url": "https://www.bain.com/careers/find-a-role/"},
    {"nome": "Kearney", "settore": "Consulenza Strategica",
     "url": "https://www.kearney.com/careers"},
    {"nome": "Oliver Wyman", "settore": "Consulenza Strategica",
     "url": "https://www.oliverwyman.com/careers.html"},
    {"nome": "Roland Berger", "settore": "Consulenza Strategica",
     "url": "https://www.rolandberger.com/en/Join/"},
    {"nome": "Goldman Sachs", "settore": "Investment Banking",
     "url": "https://higher.gs.com/roles"},
    {"nome": "J.P. Morgan", "settore": "Investment Banking",
     "url": "https://careers.jpmorgan.com/global/en/students"},
    {"nome": "Morgan Stanley", "settore": "Investment Banking",
     "url": "https://www.morganstanley.com/careers/students-graduates"},
    {"nome": "Lazard", "settore": "M&A",
     "url": "https://www.lazard.com/careers/"},
    {"nome": "Evercore", "settore": "M&A",
     "url": "https://www.evercore.com/careers/"},
    {"nome": "Jefferies", "settore": "Investment Banking",
     "url": "https://www.jefferies.com/careers/"},
]

# Parole chiave usate per interrogare i portali aziendali
PAROLE_RICERCA = ["analyst", "intern", "graduate", "associate", "consultant"]

# Il TITOLO dell'annuncio deve contenere almeno una di queste parole.
# Serve perche' i portali cercano anche dentro il testo: senza questo
# controllo "associate" pesca anche gli "Administrative Assistant".
RUOLI_AMMESSI = [
    "analyst", "analista", "intern", "interns", "internship", "stage",
    "stagiaire", "tirocinio", "tirocinante", "graduate", "trainee",
    "associate", "consultant", "consulente", "junior", "summer",
    "apprentice", "praktikum", "praktikant", "becario", "prácticas",
    "working student", "off-cycle", "neolaureat", "entry level",
]

# Limiti per non appesantire i siti
PAUSA_TRA_RICHIESTE = 1.2
MAX_PER_AZIENDA = 40      # annunci raccolti al massimo per ogni portale
MAX_DETTAGLI = 70         # descrizioni complete scaricate a ogni aggiornamento
