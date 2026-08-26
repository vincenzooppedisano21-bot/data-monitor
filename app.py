"""
JOB RADAR — Dashboard locale per il monitoraggio delle offerte di lavoro.
STEP 3a: offerte reali raccolte da LinkedIn, filtrate per entry level.

Per avviarla:  .venv/bin/streamlit run app.py
"""

import html
import json
import subprocess
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import aziende
import config
import database
import esperienza
import guardiano
import impostazioni
import linkedin
import notifiche
import siti_aziende

st.set_page_config(
    page_title="Job Radar",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# STILE GRAFICO
# ---------------------------------------------------------------
STILE = """
<style>
:root{
  --jr-card:#fbfbfd; --jr-border:rgba(16,24,40,.10);
  --jr-track:rgba(16,24,40,.10); --jr-muted:rgba(16,24,40,.62);
  --jr-shadow:0 12px 32px rgba(16,24,40,.10);
}
@media (prefers-color-scheme: dark){
  :root{
    --jr-card:#171a21; --jr-border:rgba(255,255,255,.12);
    --jr-track:rgba(255,255,255,.12); --jr-muted:rgba(255,255,255,.60);
    --jr-shadow:0 12px 32px rgba(0,0,0,.45);
  }
}

.jr-hero{ padding:.25rem 0 1.1rem 0; }
.jr-hero h1{
  font-size:2.5rem; font-weight:800; letter-spacing:-.03em; margin:0;
  background:linear-gradient(92deg,#6366f1 0%,#0ea5e9 45%,#14b8a6 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.jr-hero p{ margin:.35rem 0 0 0; color:var(--jr-muted); font-size:.95rem; }

.jr-kpis{ display:flex; gap:.75rem; flex-wrap:wrap; margin:.2rem 0 1.4rem 0; }
.jr-kpi{
  flex:1 1 150px; background:var(--jr-card); border:1px solid var(--jr-border);
  border-radius:14px; padding:.85rem 1.05rem; transition:border-color .2s, transform .2s;
}
.jr-kpi:hover{ transform:translateY(-2px); border-color:#6366f1; }
.jr-kpi .lab{ font-size:.72rem; text-transform:uppercase; letter-spacing:.08em;
  color:var(--jr-muted); font-weight:600; }
.jr-kpi .val{ font-size:1.85rem; font-weight:800; letter-spacing:-.02em; line-height:1.25; }

.jr-card{
  position:relative; overflow:hidden; background:var(--jr-card);
  border:1px solid var(--jr-border); border-radius:18px;
  padding:1.15rem 1.35rem 1.15rem 1.6rem; margin-bottom:.35rem;
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.jr-card::before{ content:""; position:absolute; left:0; top:0; bottom:0;
  width:4px; background:var(--accent); }
.jr-card:hover{ transform:translateY(-3px); box-shadow:var(--jr-shadow);
  border-color:var(--accent); }
.jr-row{ display:flex; gap:1.4rem; align-items:flex-start; flex-wrap:wrap; }
.jr-main{ flex:1 1 340px; min-width:0; }
.jr-side{ display:flex; flex-direction:column; align-items:center; gap:.6rem; }

.jr-title{ font-size:1.2rem; font-weight:700; letter-spacing:-.015em; margin:.45rem 0 .2rem 0; }
.jr-company{ font-size:.92rem; font-weight:600; }
.jr-company .sep{ color:var(--jr-muted); font-weight:400; }
.jr-desc{ font-size:.88rem; color:var(--jr-muted); margin:.55rem 0 .7rem 0; line-height:1.5; }
.jr-exp{ font-size:.82rem; margin:.15rem 0 .6rem 0; font-weight:600; color:var(--accent); }

.jr-badges{ display:flex; gap:.4rem; flex-wrap:wrap; align-items:center; }
.jr-badge{ font-size:.7rem; font-weight:700; letter-spacing:.03em; text-transform:uppercase;
  padding:.24rem .6rem; border-radius:999px; background:color-mix(in srgb,var(--accent) 14%,transparent);
  color:var(--accent); border:1px solid color-mix(in srgb,var(--accent) 30%,transparent); }
.jr-badge.neutral{ background:var(--jr-track); color:var(--jr-muted); border-color:transparent; }
.jr-badge.nuova{ background:#f43f5e; color:#fff; border-color:transparent; }
.jr-badge.stage{ background:color-mix(in srgb,#8b5cf6 16%,transparent); color:#7c3aed;
  border-color:color-mix(in srgb,#8b5cf6 32%,transparent); }
@media (prefers-color-scheme: dark){ .jr-badge.stage{ color:#c4b5fd; } }

.jr-chips{ display:flex; gap:.35rem; flex-wrap:wrap; }
.jr-chip{ font-size:.75rem; font-weight:600; padding:.22rem .58rem; border-radius:8px;
  background:color-mix(in srgb,#14b8a6 13%,transparent); color:#0d9488;
  border:1px solid color-mix(in srgb,#14b8a6 28%,transparent); }
@media (prefers-color-scheme: dark){ .jr-chip{ color:#5eead4; } }

.jr-ring{ width:68px; height:68px; border-radius:50%; display:grid; place-items:center;
  background:conic-gradient(var(--accent) calc(var(--pct)*1%), var(--jr-track) 0); }
.jr-ring-in{ width:55px; height:55px; border-radius:50%; background:var(--jr-card);
  display:grid; place-items:center; font-weight:800; font-size:1.02rem; color:var(--accent); }
.jr-ring-lab{ font-size:.66rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.09em; color:var(--jr-muted); }

.jr-apply{ display:inline-block; text-decoration:none !important; font-size:.85rem; font-weight:700;
  padding:.48rem 1.05rem; border-radius:10px; color:#fff !important; white-space:nowrap;
  background:linear-gradient(135deg,#6366f1,#0ea5e9); transition:filter .18s, transform .18s;
  box-shadow:0 4px 14px rgba(99,102,241,.32); }
.jr-apply:hover{ filter:brightness(1.1); transform:translateY(-1px); }

.jr-linkbox{ display:flex; gap:.55rem; flex-wrap:wrap; margin:.3rem 0 .2rem 0; }
.jr-linkbox a{ text-decoration:none !important; font-size:.85rem; font-weight:600;
  padding:.55rem .9rem; border-radius:12px; background:var(--jr-card);
  border:1px solid var(--jr-border); color:inherit !important;
  transition:transform .15s, border-color .15s, box-shadow .15s; }
.jr-linkbox a:hover{ transform:translateY(-2px); border-color:#6366f1;
  box-shadow:0 6px 18px rgba(99,102,241,.18); }
.jr-linkbox a small{ display:block; font-weight:500; font-size:.72rem;
  color:var(--jr-muted); margin-top:.12rem; }

.jr-empty{ text-align:center; padding:3rem 1rem; border:1px dashed var(--jr-border);
  border-radius:18px; color:var(--jr-muted); }
.jr-empty .ico{ font-size:2.6rem; }
</style>
"""
st.markdown(STILE, unsafe_allow_html=True)


# ---------------------------------------------------------------
# FUNZIONI DI SUPPORTO
# ---------------------------------------------------------------
def etichetta_citta(citta: str) -> str:
    bandiera = config.PAESE_DI_CITTA.get(citta, "").split(" ")[0]
    stella = "⭐ " if citta in config.CITTA_TARGET else ""
    return f"{stella}{bandiera} {citta}"


def etichetta_settore(settore: str) -> str:
    emoji = config.AREA_DI_SETTORE.get(settore, "").split(" ")[0]
    stella = "⭐ " if settore in config.SETTORI_TARGET else ""
    return f"{stella}{emoji} {settore}"


def analizza(titolo: str, descrizione: str) -> tuple[int, list[str]]:
    """Punteggio 0-100 e competenze trovate, confrontando con il mio CV."""
    testo = f"{titolo} {descrizione}".lower()
    trovate = [c for c in config.COMPETENZE if c.lower() in testo]
    massimo = sum(config.COMPETENZE.values())
    punti = sum(config.COMPETENZE[c] for c in trovate)
    return (round(punti / massimo * 100) if massimo else 0), trovate


def colore(match: int) -> str:
    if match >= 45:
        return "#10b981"
    if match >= 25:
        return "#f59e0b"
    return "#64748b"


def data_leggibile(iso: str) -> str:
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y")
    except ValueError:
        return iso[:10]


# ---------------------------------------------------------------
# CARICO LE OFFERTE DALL'ARCHIVIO
# ---------------------------------------------------------------
offerte = []
scartate_ora = 0
for o in database.leggi():
    o["match"], o["competenze"] = analizza(o["titolo"], o["descrizione"])

    # Rivaluto l'esperienza con le regole attuali: se ho cambiato i limiti
    # in config.py, le offerte non più adatte spariscono senza dover
    # rifare la ricerca su LinkedIn.
    v = esperienza.valuta(o["titolo"], o["descrizione"], o.get("anzianita", ""))
    o["tipo_esperienza"] = v["tipo"]
    o["anni_richiesti"] = v["anni"]
    o["motivo_esperienza"] = v["motivo"]
    if not v["adatta"]:
        scartate_ora += 1
        continue
    offerte.append(o)

df = pd.DataFrame(offerte) if offerte else pd.DataFrame(
    columns=["id", "titolo", "azienda", "citta", "settore", "fonte", "descrizione",
             "link", "data_pubblicazione", "tipo_esperienza", "anni_richiesti",
             "motivo_esperienza", "match", "competenze", "trovata_il"]
)


# ---------------------------------------------------------------
# BARRA LATERALE
# ---------------------------------------------------------------
CHIAVI = ["f_citta", "f_settori", "f_fonti", "f_tipi", "f_match", "f_ordine", "f_testo"]


def azzera_filtri():
    for k in CHIAVI:
        st.session_state.pop(k, None)


def applica_target():
    st.session_state["f_citta"] = list(config.CITTA_TARGET)
    st.session_state["f_settori"] = list(config.SETTORI_TARGET)


with st.sidebar:
    st.markdown("### 🔎 Filtri di ricerca")

    st.button("⭐ Applica i miei target", width="stretch",
              on_click=applica_target,
              help="Seleziona in un clic le mie 6 città e i miei 5 settori prioritari.")

    citta_scelte = st.multiselect(
        f"Città  ·  {len(config.CITTA)} disponibili",
        options=config.CITTA, format_func=etichetta_citta,
        placeholder="Tutte le città", key="f_citta",
        help="Scrivi per cercare. ⭐ = le tue priorità.",
    )

    settori_scelti = st.multiselect(
        f"Settore  ·  {len(config.SETTORI)} disponibili",
        options=config.SETTORI, format_func=etichetta_settore,
        placeholder="Tutti i settori", key="f_settori",
        help="Scrivi per cercare. ⭐ = le tue priorità.",
    )

    st.markdown("**Tipo di offerta**")
    tipi_scelti = st.pills(
        "Tipo", options=["Internship", "Entry level", "Da verificare"],
        selection_mode="multi", default=["Internship", "Entry level"],
        key="f_tipi", label_visibility="collapsed",
        help="«Da verificare» = l'annuncio non dichiara requisiti di esperienza. "
             "Attivalo per vedere anche quelle.",
    )

    match_minimo = st.slider("Match minimo", 0, 100, 0, 5, key="f_match")

    testo_cercato = st.text_input("Cerca nel testo",
                                  placeholder="es. Valuation, Deutsche Bank…", key="f_testo")

    ordine = st.selectbox(
        "Ordina per",
        ["Più recenti", "Match più alto", "Match più basso", "Azienda (A-Z)", "Città (A-Z)"],
        key="f_ordine",
    )

    st.button("↺ Azzera filtri", width="stretch", on_click=azzera_filtri)

    # -----------------------------------------------------------
    # PANNELLO DI AGGIORNAMENTO DA LINKEDIN
    # -----------------------------------------------------------
    st.divider()
    st.markdown("### 🔄 Cerca nuove offerte")

    dove_cercare = st.radio(
        "Dove cerco",
        ["Entrambi", "Solo LinkedIn", "Solo siti aziendali"],
        horizontal=False, label_visibility="collapsed",
        captions=[
            "LinkedIn + portali ufficiali",
            "Annunci pubblici di LinkedIn",
            f"{len(aziende.AZIENDE)} portali di {len(set(a['nome'] for a in aziende.AZIENDE))} aziende",
        ],
    )

    citta_ricerca = citta_scelte or list(config.CITTA_TARGET)
    settori_ricerca = settori_scelti or list(config.SETTORI_TARGET)
    combinazioni = len(citta_ricerca) * len(settori_ricerca)

    giorni = st.select_slider(
        "Offerte pubblicate negli ultimi",
        options=[1, 3, 7, 14, 30], value=7,
        format_func=lambda g: f"{g} giorno" if g == 1 else f"{g} giorni",
    )

    solo_entry = st.toggle(
        "Solo offerte senza esperienza richiesta", value=True,
        help="Scarta le offerte che richiedono esperienza lavorativa pregressa. "
             f"Tollerati al massimo {config.MAX_MESI_ESPERIENZA} mesi, "
             "cioè la tua summer internship.",
    )

    secondi = 0
    if dove_cercare != "Solo siti aziendali":
        secondi += (combinazioni * 2 + config.MAX_DETTAGLI) * config.PAUSA_TRA_RICHIESTE
    if dove_cercare != "Solo LinkedIn":
        portali = len([a for a in aziende.AZIENDE if a["settore"] in settori_ricerca]) or 1
        secondi += (portali * len(aziende.PAROLE_RICERCA) * 2
                    + aziende.MAX_DETTAGLI) * aziende.PAUSA_TRA_RICHIESTE
    minuti = max(1, round(secondi / 60))

    st.caption(
        f"{combinazioni} combinazioni ({len(citta_ricerca)} città × "
        f"{len(settori_ricerca)} settori) — circa **{minuti} minuti**."
    )
    if combinazioni > 40:
        st.warning("Sono tante combinazioni: la ricerca sarà lunga. "
                   "Meglio selezionare meno città o settori.", icon="⏳")

    avvia = st.button("🔍 Cerca ora", type="primary", width="stretch")
    spazio_avanzamento = st.empty()

    ultimo = database.ultimo_aggiornamento()
    st.caption(f"Ultimo aggiornamento: **{data_leggibile(ultimo)}**" if ultimo
               else "Archivio ancora vuoto.")

    # -----------------------------------------------------------
    # NOTIFICHE EMAIL E GUARDIANO
    # -----------------------------------------------------------
    st.divider()
    conf = impostazioni.leggi()
    guardiano_attivo = guardiano.attivo()
    pronta = impostazioni.configurate()

    stato = "🟢 Configurate" if pronta else "🔴 Da configurare"
    st.markdown(f"### 📧 Avvisi email — {stato}")

    with st.expander("Configura le notifiche", expanded=not pronta):

        st.markdown("**1. Il tuo indirizzo Gmail**")
        indirizzo = st.text_input("Gmail", value=conf["email"],
                                  placeholder="nome.cognome@gmail.com",
                                  label_visibility="collapsed")

        st.markdown("**2. La Password per le App**")
        with st.popover("❓ Come si ottiene", width="stretch"):
            st.markdown("""
**Perché serve.** Google non permette ai programmi di usare la tua password
normale. Ti fa generare una password *dedicata*, lunga 16 lettere, che vale
**solo** per inviare email da questo programma e che puoi revocare quando
vuoi senza toccare il tuo account.

**Passo per passo:**

1. Vai su **myaccount.google.com/security**
2. Attiva la **Verifica in due passaggi** (se non è già attiva).
   È obbligatoria: senza, Google non mostra l'opzione successiva
3. Torna nella stessa pagina e cerca **"Password per le app"**.
   Se non la trovi, vai diretta a **myaccount.google.com/apppasswords**
4. Alla richiesta del nome scrivi **Job Radar** e premi **Crea**
5. Google mostra **16 lettere** divise in 4 gruppi, tipo `abcd efgh ijkl mnop`
6. **Copiale e incollale qui sotto.** Gli spazi non contano.
   Google non te le mostrerà mai più: se le perdi, ne generi un'altra

🔒 La password viene salvata nel **Portachiavi di macOS**, non in un file.
                        """)

        password = st.text_input("Password per le App", type="password",
                                 placeholder="abcd efgh ijkl mnop",
                                 label_visibility="collapsed",
                                 help="16 lettere generate da Google, non la tua password abituale.")

        if st.button("💾 Salva e invia email di prova", width="stretch", type="primary"):
            if not indirizzo or "@" not in indirizzo:
                st.error("Inserisci un indirizzo Gmail valido.")
            elif not password and not impostazioni.leggi_password(indirizzo):
                st.error("Inserisci la Password per le App.")
            else:
                if password:
                    impostazioni.salva_password(indirizzo, password)
                impostazioni.salva({"email": indirizzo})
                try:
                    notifiche.invia_prova(indirizzo,
                                          impostazioni.leggi_password(indirizzo) or "")
                except notifiche.EmailNonInviata as errore:
                    st.error(str(errore))
                else:
                    st.success(f"Email di prova inviata a {indirizzo}. Controlla la posta!")

        st.divider()
        st.markdown("**3. Cosa farti sapere**")
        tipi_email = st.multiselect(
            "Avvisami per", options=["Internship", "Entry level", "Da verificare"],
            default=conf["tipi_da_notificare"],
            help="«Da verificare» sono annunci che non dichiarano i requisiti.")
        soglia_email = st.slider("Solo con match almeno", 0, 100,
                                 conf["match_minimo"], 5)
        solo_target = st.toggle(
            "Controlla solo le mie città e settori prioritari",
            value=conf["solo_target"],
            help="Disattivalo per sorvegliare tutte le 64 città e i 49 settori: "
                 "ogni giro diventa molto più lungo.")

        if st.button("Salva preferenze", width="stretch"):
            impostazioni.salva({"tipi_da_notificare": tipi_email,
                                "match_minimo": soglia_email,
                                "solo_target": solo_target})
            st.success("Preferenze salvate.")

    # ---- Stato del guardiano ----
    st.divider()
    st.markdown("### 🛰 Guardiano")

    @st.cache_data(ttl=90, show_spinner=False)
    def stato_su_github():
        """Chiede a GitHub quando ha lavorato il guardiano l'ultima volta."""
        try:
            esito = subprocess.run(
                ["gh", "run", "list", "--workflow=guardiano.yml", "--limit", "6",
                 "--json", "createdAt,conclusion,status,event"],
                capture_output=True, text=True, timeout=20,
                cwd=str(Path(__file__).parent))
            if esito.returncode != 0:
                return None
            return json.loads(esito.stdout or "[]")
        except Exception:
            return None

    giri = stato_su_github()

    if giri is None:
        st.warning("Non riesco a contattare GitHub per sapere come sta il guardiano. "
                   "Controlla la connessione.", icon="📡")
    elif not giri:
        st.warning("Il guardiano è configurato su GitHub ma non ha ancora "
                   "eseguito nessun controllo.", icon="⏳")
    else:
        ultimo = giri[0]
        andato_bene = ultimo.get("conclusion") == "success"
        in_corso = ultimo.get("status") in ("in_progress", "queued")

        if in_corso:
            st.info("🔄 **Controllo in corso proprio adesso** su GitHub.")
        elif andato_bene:
            st.success("🟢 **Attivo su GitHub** — controlla ogni 15 minuti, "
                       "anche a Mac spento.", icon="✅")
        else:
            st.error(f"🔴 L'ultimo controllo è fallito ({ultimo.get('conclusion')}). "
                     "Apri la scheda Actions su GitHub per capire perché.")

        quando = ultimo["createdAt"]
        st.caption(f"Ultimo controllo: **{quando[8:10]}/{quando[5:7]} alle "
                   f"{quando[11:16]}** (ora di Londra)")

        with st.expander("📜 Ultimi controlli"):
            for g in giri:
                icona = {"success": "✅", "failure": "❌", "cancelled": "⚪"}.get(
                    g.get("conclusion"), "🔄")
                tipo = "automatico" if g.get("event") == "schedule" else "manuale"
                st.write(f"{icona} {g['createdAt'][11:16]} — {tipo}")

    colonna_a, colonna_b = st.columns(2)
    with colonna_a:
        if st.button("🔄 Controlla adesso", width="stretch",
                     help="Lancia subito un controllo su GitHub senza aspettare."):
            esito = subprocess.run(
                ["gh", "workflow", "run", "guardiano.yml"],
                capture_output=True, text=True, cwd=str(Path(__file__).parent))
            stato_su_github.clear()
            if esito.returncode == 0:
                st.success("Controllo avviato. Tra un paio di minuti avrai l'esito.")
            else:
                st.error("Non sono riuscita ad avviarlo: " + esito.stderr[:120])
    with colonna_b:
        if st.button("⬇️ Scarica le offerte", width="stretch",
                     help="Porta sul Mac le offerte trovate da GitHub."):
            esito = subprocess.run(["git", "pull", "--rebase", "--autostash"],
                                   capture_output=True, text=True,
                                   cwd=str(Path(__file__).parent))
            if esito.returncode == 0:
                st.success("Archivio aggiornato.")
                st.rerun()
            else:
                st.error(esito.stderr[:150])

    # ---- Guardiano di riserva sul Mac (normalmente spento) ----
    with st.expander("⚙️ Guardiano di riserva sul Mac (avanzato)"):
        st.caption(
            "Il tuo Mac può fare da guardiano al posto di GitHub. "
            "**Tienilo spento**: con entrambi accesi riceveresti email doppie, "
            "perché ognuno tiene un elenco separato di ciò che ti ha già segnalato."
        )
        if guardiano_attivo:
            st.warning("⚠️ Il guardiano locale è ACCESO insieme a quello di GitHub.",
                       icon="⚠️")
            if st.button("⏸ Spegni il guardiano locale", type="primary", width="stretch"):
                ok, messaggio = guardiano.spegni()
                impostazioni.salva({"notifiche_attive": False})
                (st.success if ok else st.error)(messaggio)
                st.rerun()
        else:
            st.caption("Stato attuale: **spento** ✔︎ (corretto)")
            minuti = st.select_slider("Se lo accendessi, controllerebbe ogni",
                                      options=[5, 10, 15, 30, 60],
                                      value=conf["frequenza_minuti"],
                                      format_func=lambda m: f"{m} minuti" if m < 60 else "1 ora")
            if st.button("▶️ Accendi comunque il guardiano locale", width="stretch"):
                database.segna_tutte_inviate()
                impostazioni.salva({"notifiche_attive": True, "frequenza_minuti": minuti})
                ok, messaggio = guardiano.accendi(minuti)
                (st.success if ok else st.error)(messaggio)
                st.rerun()

    st.divider()
    with st.expander("👤 Il mio profilo"):
        st.caption("**Ruoli cercati**")
        st.write(" · ".join(config.RUOLI))
        st.caption("**⭐ Settori prioritari**")
        st.write(" · ".join(config.SETTORI_TARGET))
        st.caption("**⭐ Città prioritarie**")
        st.write(" · ".join(config.CITTA_TARGET))
        st.caption("**Competenze chiave**")
        st.write(" · ".join(config.COMPETENZE))
        st.caption("Tutto modificabile nel file `config.py`")


# ---------------------------------------------------------------
# ESECUZIONE DELLA RICERCA
# ---------------------------------------------------------------
if avvia:
    barra = spazio_avanzamento.progress(0.0, text="Avvio della ricerca…")

    def aggiorna_barra(frazione, messaggio):
        barra.progress(min(max(frazione, 0.0), 1.0), text=messaggio)

    trovate, esaminati, scartati, problemi = [], 0, 0, []

    # --- LinkedIn ---
    if dove_cercare != "Solo siti aziendali":
        try:
            parziali, stat = linkedin.raccogli(
                citta_scelte=citta_ricerca, settori_scelti=settori_ricerca,
                giorni=giorni, solo_entry_level=solo_entry,
                avanzamento=lambda f, m: aggiorna_barra(
                    f * (0.5 if dove_cercare == "Entrambi" else 1.0), f"LinkedIn · {m}"),
            )
        except Exception as errore:
            problemi.append(f"LinkedIn: {errore}")
        else:
            trovate += parziali
            esaminati += stat["cercate"]
            scartati += stat["scartate"]

    # --- Siti carriere aziendali ---
    if dove_cercare != "Solo LinkedIn":
        inizio = 0.5 if dove_cercare == "Entrambi" else 0.0
        ampiezza = 0.5 if dove_cercare == "Entrambi" else 1.0
        try:
            parziali, stat = siti_aziende.raccogli(
                citta_scelte=citta_ricerca, settori_scelti=settori_ricerca,
                giorni=giorni, solo_entry_level=solo_entry,
                avanzamento=lambda f, m: aggiorna_barra(inizio + f * ampiezza, m),
            )
        except Exception as errore:
            problemi.append(f"Siti aziendali: {errore}")
        else:
            trovate += parziali
            esaminati += stat["cercate"]
            scartati += stat["scartate"]

    for o in trovate:
        o["match"], o["competenze"] = analizza(o["titolo"], o.get("descrizione", ""))
    nuove = database.salva(trovate)
    spazio_avanzamento.empty()

    if problemi and not trovate:
        st.session_state["esito"] = ("errore", "Ricerca non riuscita. " + " · ".join(problemi))
    else:
        messaggio = (
            f"Ricerca completata: **{esaminati}** annunci esaminati, "
            f"**{scartati}** scartati perché richiedono esperienza, "
            f"**{len(trovate)}** adatti a te — di cui **{nuove} nuovi**."
        )
        if problemi:
            messaggio += "  ⚠️ " + " · ".join(problemi)
        st.session_state["esito"] = ("ok", messaggio)
    st.rerun()


# ---------------------------------------------------------------
# FILTRI
# ---------------------------------------------------------------
vis = df.copy()
if not vis.empty:
    if citta_scelte:
        vis = vis[vis["citta"].isin(citta_scelte)]
    if settori_scelti:
        vis = vis[vis["settore"].isin(settori_scelti)]
    if tipi_scelti:
        vis = vis[vis["tipo_esperienza"].isin(tipi_scelti)]
    if testo_cercato:
        cerca = testo_cercato.lower()
        vis = vis[vis.apply(
            lambda r: cerca in f"{r['titolo']} {r['azienda']} {r['citta']} "
                               f"{r['descrizione']}".lower(), axis=1)]
    vis = vis[vis["match"] >= match_minimo]

    if ordine == "Match più alto":
        vis = vis.sort_values("match", ascending=False)
    elif ordine == "Match più basso":
        vis = vis.sort_values("match", ascending=True)
    elif ordine == "Azienda (A-Z)":
        vis = vis.sort_values("azienda")
    elif ordine == "Città (A-Z)":
        vis = vis.sort_values("citta")
    else:
        vis = vis.sort_values(["data_pubblicazione", "match"], ascending=[False, False])


# ---------------------------------------------------------------
# PAGINA PRINCIPALE
# ---------------------------------------------------------------
st.markdown(
    """
    <div class="jr-hero">
      <h1>Job Radar</h1>
      <p>Solo offerte senza esperienza richiesta — internship, graduate ed entry level</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "esito" in st.session_state:
    tipo, messaggio = st.session_state.pop("esito")
    (st.success if tipo == "ok" else st.error)(messaggio, icon="✅" if tipo == "ok" else "⚠️")

if scartate_ora:
    st.caption(
        f"🧹 {scartate_ora} offerte già in archivio sono state nascoste perché "
        f"richiedono esperienza pregressa."
    )

media = f"{vis['match'].mean():.0f}%" if len(vis) else "—"
n_stage = int((vis["tipo_esperienza"] == "Internship").sum()) if len(vis) else 0
oggi = date.today().isoformat()
n_nuove = int(vis["trovata_il"].astype(str).str.startswith(oggi).sum()) if len(vis) else 0

st.markdown(
    f"""
    <div class="jr-kpis">
      <div class="jr-kpi"><div class="lab">Offerte visibili</div><div class="val">{len(vis)}</div></div>
      <div class="jr-kpi"><div class="lab">Trovate oggi</div><div class="val">{n_nuove}</div></div>
      <div class="jr-kpi"><div class="lab">Internship</div><div class="val">{n_stage}</div></div>
      <div class="jr-kpi"><div class="lab">Match medio</div><div class="val">{media}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        """
        <div class="jr-empty">
          <div class="ico">📡</div>
          <p><b>L'archivio è ancora vuoto.</b><br>
          Vai nella barra laterale, sezione <b>«🔄 Aggiorna da LinkedIn»</b>,
          e premi <b>«🔍 Cerca ora su LinkedIn»</b>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
elif vis.empty:
    st.markdown(
        """
        <div class="jr-empty">
          <div class="ico">🔍</div>
          <p><b>Nessuna offerta corrisponde ai filtri.</b><br>
          Prova ad allargare la ricerca o premi «Azzera filtri».</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for _, o in vis.iterrows():
        acc = colore(o["match"])
        e_nuova = str(o["trovata_il"]).startswith(oggi)

        chips = "".join(
            f'<span class="jr-chip">{html.escape(c)}</span>' for c in (o["competenze"] or [])
        ) or '<span class="jr-chip" style="opacity:.55">nessuna competenza rilevata</span>'

        badge_tipo = ""
        if o["tipo_esperienza"] == "Internship":
            badge_tipo = '<span class="jr-badge stage">🎓 Internship</span>'
        elif o["tipo_esperienza"] == "Entry level":
            badge_tipo = '<span class="jr-badge neutral">Entry level</span>'
        elif o["tipo_esperienza"] == "Da verificare":
            badge_tipo = '<span class="jr-badge neutral">Da verificare</span>'

        estratto = (o["descrizione"] or "")[:230]
        if len(o["descrizione"] or "") > 230:
            estratto += "…"

        pubblicata = f" · 🗓 {data_leggibile(o['data_pubblicazione'])}" if o["data_pubblicazione"] else ""

        st.markdown(
            f"""
            <div class="jr-card" style="--accent:{acc}">
              <div class="jr-row">
                <div class="jr-main">
                  <div class="jr-badges">
                    {'<span class="jr-badge nuova">🆕 Nuova</span>' if e_nuova else ''}
                    {badge_tipo}
                    <span class="jr-badge">{html.escape(o['settore'] or '')}</span>
                    <span class="jr-badge neutral">{html.escape(o['fonte'] or '')}</span>
                  </div>
                  <div class="jr-title">{html.escape(o['titolo'] or '')}</div>
                  <div class="jr-company">{html.escape(o['azienda'] or '')}
                    <span class="sep">· 📍 {html.escape(o['luogo_esteso'] or o['citta'] or '')}{pubblicata}</span></div>
                  <div class="jr-exp">⏱ {html.escape(o['motivo_esperienza'] or '')}</div>
                  <div class="jr-desc">{html.escape(estratto)}</div>
                  <div class="jr-chips">{chips}</div>
                </div>
                <div class="jr-side">
                  <div class="jr-ring" style="--pct:{o['match']}">
                    <div class="jr-ring-in">{o['match']}%</div>
                  </div>
                  <div class="jr-ring-lab">Match</div>
                  <a class="jr-apply" href="{html.escape(o['link'] or '#', quote=True)}"
                     target="_blank" rel="noopener">Candidati →</a>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if o["descrizione"]:
            with st.expander("Leggi l'annuncio completo"):
                st.write(o["descrizione"])


# ---------------------------------------------------------------
# AZIENDE DA CONTROLLARE A MANO
# I loro siti bloccano le letture automatiche: qui trovi il link
# per aprirle direttamente, gia' sulla pagina delle offerte.
# ---------------------------------------------------------------
st.divider()
with st.expander(f"🏢 Altre {len(aziende.AZIENDE_LINK_DIRETTO)} aziende da controllare a mano"):
    st.caption(
        "Questi portali bloccano la lettura automatica, quindi non posso "
        "raccogliere le loro offerte. Clicca per aprirli: sono già sulla "
        "pagina delle posizioni aperte."
    )
    pulsanti = "".join(
        f'<a href="{html.escape(a["url"], quote=True)}" target="_blank" rel="noopener">'
        f'{html.escape(a["nome"])}<small>{html.escape(a["settore"])}</small></a>'
        for a in aziende.AZIENDE_LINK_DIRETTO
    )
    st.markdown(f'<div class="jr-linkbox">{pulsanti}</div>', unsafe_allow_html=True)

with st.expander(f"📡 {len(aziende.AZIENDE)} portali letti automaticamente"):
    righe = [{"Azienda": a["nome"], "Sezione": a["etichetta"],
              "Settore": a["settore"], "Piattaforma": a["piattaforma"].title()}
             for a in aziende.AZIENDE]
    st.dataframe(pd.DataFrame(righe), width="stretch", hide_index=True)
