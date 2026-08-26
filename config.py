"""
IL MIO PROFILO E LE LISTE DI RICERCA.

Questo file e' scritto in italiano semplice: puoi modificarlo tu quando vuoi.
Ci sono due tipi di liste:
  - le liste "TARGET"  = le mie priorita' (compaiono con una stellina nei menu)
  - le liste complete  = tutte le opzioni selezionabili nei menu a tendina
"""

# ===============================================================
# 1. RUOLI CERCATI
# ===============================================================
RUOLI = [
    "Analyst",
    "Junior Consultant",
    "Summer Analyst",
    "Associate",
]

# ===============================================================
# 2. SETTORI
# ===============================================================

# Le mie priorita' (compaiono con la stellina nel menu)
SETTORI_TARGET = [
    "Investment Banking",
    "M&A",
    "Consulenza Strategica",
    "Venture Capital",
    "Private Equity",
]

# Tutti i settori selezionabili, raggruppati per area.
# L'emoji serve solo a riconoscere l'area a colpo d'occhio nel menu.
SETTORI_PER_AREA = {
    "💼 Finanza & Deal": [
        "Investment Banking",
        "M&A",
        "Private Equity",
        "Venture Capital",
        "Corporate Finance",
        "Leveraged Finance & Debt Advisory",
        "Restructuring",
        "Equity Research",
        "Asset Management",
        "Wealth Management & Private Banking",
        "Hedge Fund",
        "Trading & Capital Markets",
        "Real Estate Finance",
        "Infrastructure & Project Finance",
        "Fintech",
    ],
    "🧠 Consulenza": [
        "Consulenza Strategica",
        "Consulenza Direzionale",
        "Transaction Services & Deal Advisory",
        "Due Diligence",
        "Risk & Compliance",
        "Consulenza IT & Digital",
        "Operations & Supply Chain",
        "HR & Organization",
        "Sustainability & ESG",
    ],
    "📈 Business & Commerciale": [
        "Business Development",
        "Sales",
        "Account Management",
        "Marketing",
        "Growth",
        "Partnerships",
        "Customer Success",
        "Category Management",
    ],
    "💻 Tech & Dati": [
        "Data Analytics",
        "Data Science",
        "Business Intelligence",
        "Product Management",
        "Software Engineering",
        "AI & Machine Learning",
        "Cybersecurity",
        "Cloud & Infrastructure",
    ],
    "🏢 Corporate & Industria": [
        "Corporate Strategy",
        "Controlling & FP&A",
        "Amministrazione Finanza e Controllo",
        "Internal Audit",
        "Tax",
        "Legal",
        "Procurement",
        "Project Management",
        "Startup & Scale-up",
    ],
}

# Lista "piatta" di tutti i settori (generata in automatico dalla lista sopra)
SETTORI = [s for gruppo in SETTORI_PER_AREA.values() for s in gruppo]

# Da ogni settore risalgo alla sua area (serve per l'emoji nei menu)
AREA_DI_SETTORE = {
    s: area for area, gruppo in SETTORI_PER_AREA.items() for s in gruppo
}

# ===============================================================
# 3. CITTA'
# ===============================================================

# Le mie priorita' (compaiono con la stellina nel menu)
CITTA_TARGET = [
    "Milano",
    "Roma",
    "Madrid",
    "Barcellona",
    "Londra",
    "Dubai",
]

# Tutte le citta' selezionabili, raggruppate per paese.
CITTA_PER_PAESE = {
    "🇮🇹 Italia": [
        "Milano", "Roma", "Torino", "Bologna", "Firenze",
        "Padova", "Verona", "Genova", "Napoli", "Bari",
    ],
    "🇪🇸 Spagna": [
        "Madrid", "Barcellona", "Valencia", "Bilbao", "Siviglia", "Malaga",
    ],
    "🇬🇧 Regno Unito & Irlanda": [
        "Londra", "Manchester", "Edimburgo", "Birmingham", "Dublino",
    ],
    "🇦🇪 Medio Oriente": [
        "Dubai", "Abu Dhabi", "Doha", "Riyadh", "Tel Aviv",
    ],
    "🇫🇷 Francia": ["Parigi", "Lione"],
    "🇩🇪 Germania & Austria": [
        "Francoforte", "Monaco di Baviera", "Berlino", "Amburgo",
        "Dusseldorf", "Vienna",
    ],
    "🇨🇭 Svizzera": ["Zurigo", "Ginevra", "Lugano", "Basilea"],
    "🇳🇱 Benelux": ["Amsterdam", "Rotterdam", "Bruxelles", "Lussemburgo"],
    "🇸🇪 Nord Europa": ["Stoccolma", "Copenaghen", "Oslo", "Helsinki"],
    "🇵🇱 Est & Sud Europa": [
        "Varsavia", "Praga", "Budapest", "Bucarest", "Lisbona", "Atene",
    ],
    "🇺🇸 Nord America": [
        "New York", "Boston", "Chicago", "San Francisco",
        "Los Angeles", "Toronto",
    ],
    "🌏 Asia & Pacifico": ["Singapore", "Hong Kong", "Tokyo", "Sydney", "Mumbai"],
    "🏠 Altro": ["Da remoto"],
}

# Lista "piatta" di tutte le citta' (generata in automatico)
CITTA = [c for gruppo in CITTA_PER_PAESE.values() for c in gruppo]

# Da ogni citta' risalgo al suo paese (serve per la bandierina nei menu)
PAESE_DI_CITTA = {
    c: paese for paese, gruppo in CITTA_PER_PAESE.items() for c in gruppo
}

# ===============================================================
# 4. COMPETENZE CHIAVE DEL MIO CV
# Il numero e' il "peso": piu' e' alto, piu' quella parola
# fa salire il punteggio di match dell'offerta.
# ===============================================================
COMPETENZE = {
    "Financial Modelling": 3,
    "Due Diligence": 3,
    "M&A": 3,
    "Strategy": 2,
    "CCA": 2,
    "Regression Analysis": 2,
    "Valuation": 2,
    "Excel": 1,
    "PowerPoint": 1,
}


# ===============================================================
# 5. IMPOSTAZIONI DELLA RICERCA SU LINKEDIN
# ===============================================================

# LinkedIn accetta i nomi delle citta' SOLO in inglese: qui traduco.
CITTA_LINKEDIN = {
    # Italia
    "Milano": "Milan, Lombardy, Italy",
    "Roma": "Rome, Lazio, Italy",
    "Torino": "Turin, Piedmont, Italy",
    "Bologna": "Bologna, Emilia-Romagna, Italy",
    "Firenze": "Florence, Tuscany, Italy",
    "Padova": "Padua, Veneto, Italy",
    "Verona": "Verona, Veneto, Italy",
    "Genova": "Genoa, Liguria, Italy",
    "Napoli": "Naples, Campania, Italy",
    "Bari": "Bari, Apulia, Italy",
    # Spagna
    "Madrid": "Madrid, Community of Madrid, Spain",
    "Barcellona": "Barcelona, Catalonia, Spain",
    "Valencia": "Valencia, Valencian Community, Spain",
    "Bilbao": "Bilbao, Basque Country, Spain",
    "Siviglia": "Seville, Andalusia, Spain",
    "Malaga": "Malaga, Andalusia, Spain",
    # Regno Unito e Irlanda
    "Londra": "London, England, United Kingdom",
    "Manchester": "Manchester, England, United Kingdom",
    "Edimburgo": "Edinburgh, Scotland, United Kingdom",
    "Birmingham": "Birmingham, England, United Kingdom",
    "Dublino": "Dublin, County Dublin, Ireland",
    # Medio Oriente
    "Dubai": "Dubai, United Arab Emirates",
    "Abu Dhabi": "Abu Dhabi, United Arab Emirates",
    "Doha": "Doha, Qatar",
    "Riyadh": "Riyadh, Saudi Arabia",
    "Tel Aviv": "Tel Aviv, Israel",
    # Francia
    "Parigi": "Paris, Ile-de-France, France",
    "Lione": "Lyon, Auvergne-Rhone-Alpes, France",
    # Germania e Austria
    "Francoforte": "Frankfurt, Hesse, Germany",
    "Monaco di Baviera": "Munich, Bavaria, Germany",
    "Berlino": "Berlin, Germany",
    "Amburgo": "Hamburg, Germany",
    "Dusseldorf": "Dusseldorf, North Rhine-Westphalia, Germany",
    "Vienna": "Vienna, Austria",
    # Svizzera
    "Zurigo": "Zurich, Switzerland",
    "Ginevra": "Geneva, Switzerland",
    "Lugano": "Lugano, Ticino, Switzerland",
    "Basilea": "Basel, Switzerland",
    # Benelux
    "Amsterdam": "Amsterdam, North Holland, Netherlands",
    "Rotterdam": "Rotterdam, South Holland, Netherlands",
    "Bruxelles": "Brussels, Brussels Region, Belgium",
    "Lussemburgo": "Luxembourg, Luxembourg",
    # Nord Europa
    "Stoccolma": "Stockholm, Sweden",
    "Copenaghen": "Copenhagen, Denmark",
    "Oslo": "Oslo, Norway",
    "Helsinki": "Helsinki, Finland",
    # Est e Sud Europa
    "Varsavia": "Warsaw, Masovian, Poland",
    "Praga": "Prague, Czechia",
    "Budapest": "Budapest, Hungary",
    "Bucarest": "Bucharest, Romania",
    "Lisbona": "Lisbon, Portugal",
    "Atene": "Athens, Greece",
    # Nord America
    "New York": "New York, New York, United States",
    "Boston": "Boston, Massachusetts, United States",
    "Chicago": "Chicago, Illinois, United States",
    "San Francisco": "San Francisco, California, United States",
    "Los Angeles": "Los Angeles, California, United States",
    "Toronto": "Toronto, Ontario, Canada",
    # Asia e Pacifico
    "Singapore": "Singapore",
    "Hong Kong": "Hong Kong SAR",
    "Tokyo": "Tokyo, Japan",
    "Sydney": "Sydney, New South Wales, Australia",
    "Mumbai": "Mumbai, Maharashtra, India",
    # Altro
    "Da remoto": "European Union",
}

# Come cerco ogni settore su LinkedIn (le parole chiave vanno in inglese).
QUERY_PER_SETTORE = {
    # Finanza & Deal
    "Investment Banking": "Investment Banking Analyst",
    "M&A": "Mergers Acquisitions Analyst",
    "Private Equity": "Private Equity Analyst",
    "Venture Capital": "Venture Capital Analyst",
    "Corporate Finance": "Corporate Finance Analyst",
    "Leveraged Finance & Debt Advisory": "Leveraged Finance Analyst",
    "Restructuring": "Restructuring Analyst",
    "Equity Research": "Equity Research Analyst",
    "Asset Management": "Asset Management Analyst",
    "Wealth Management & Private Banking": "Private Banking Analyst",
    "Hedge Fund": "Hedge Fund Analyst",
    "Trading & Capital Markets": "Capital Markets Analyst",
    "Real Estate Finance": "Real Estate Investment Analyst",
    "Infrastructure & Project Finance": "Project Finance Analyst",
    "Fintech": "Fintech Analyst",
    # Consulenza
    "Consulenza Strategica": "Strategy Consultant",
    "Consulenza Direzionale": "Management Consultant",
    "Transaction Services & Deal Advisory": "Transaction Services Analyst",
    "Due Diligence": "Due Diligence Analyst",
    "Risk & Compliance": "Risk Compliance Analyst",
    "Consulenza IT & Digital": "Digital Technology Consultant",
    "Operations & Supply Chain": "Operations Supply Chain Analyst",
    "HR & Organization": "HR Analyst",
    "Sustainability & ESG": "ESG Sustainability Analyst",
    # Business & Commerciale
    "Business Development": "Business Development Analyst",
    "Sales": "Sales Analyst",
    "Account Management": "Account Manager Junior",
    "Marketing": "Marketing Analyst",
    "Growth": "Growth Analyst",
    "Partnerships": "Partnerships Analyst",
    "Customer Success": "Customer Success Analyst",
    "Category Management": "Category Management Analyst",
    # Tech & Dati
    "Data Analytics": "Data Analyst",
    "Data Science": "Data Scientist",
    "Business Intelligence": "Business Intelligence Analyst",
    "Product Management": "Product Analyst",
    "Software Engineering": "Software Engineer Graduate",
    "AI & Machine Learning": "Machine Learning Engineer Graduate",
    "Cybersecurity": "Cybersecurity Analyst",
    "Cloud & Infrastructure": "Cloud Engineer Graduate",
    # Corporate & Industria
    "Corporate Strategy": "Corporate Strategy Analyst",
    "Controlling & FP&A": "Financial Planning Analyst",
    "Amministrazione Finanza e Controllo": "Finance Analyst",
    "Internal Audit": "Internal Audit Analyst",
    "Tax": "Tax Analyst",
    "Legal": "Legal Analyst",
    "Procurement": "Procurement Analyst",
    "Project Management": "Project Management Analyst",
    "Startup & Scale-up": "Startup Analyst",
}

# Livelli di esperienza richiesti a LinkedIn:
# 1 = Stage/Internship, 2 = Livello base (entry level), 3 = Esperienza minima
LIVELLI_LINKEDIN = "1,2"

# Ogni quanti secondi al massimo faccio una richiesta a LinkedIn.
# Andare piano e' la chiave per non essere bloccati.
PAUSA_TRA_RICHIESTE = 2.5

# Quante offerte al massimo prendo per ogni combinazione citta' + settore
MAX_PER_RICERCA = 25

# Quante descrizioni complete scarico al massimo a ogni aggiornamento
MAX_DETTAGLI = 80

# Quanta esperienza pregressa posso avere: io sono neolaureata con una
# summer internship di 3 mesi, quindi cerco offerte a ZERO anni richiesti.
MAX_ANNI_ESPERIENZA = 0   # nessun anno di esperienza richiesto
MAX_MESI_ESPERIENZA = 3   # la durata della mia summer internship
