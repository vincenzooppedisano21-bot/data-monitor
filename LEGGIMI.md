# 🎯 Job Radar — manuale d'uso

Piattaforma locale per il monitoraggio delle offerte di lavoro entry level
in Investment Banking, M&A, Consulenza Strategica, Venture Capital e Private Equity.

Tutto gira **sul tuo Mac**. Nessun dato esce dal computer, tranne le email
che il programma manda a te stessa.

---

## Avviare la dashboard

Apri il Terminale e incolla:

```bash
cd ~/job-radar && .venv/bin/streamlit run app.py
```

Si apre da sola nel browser. Per chiuderla: `Ctrl` + `C` nel Terminale.

---

## Le tre parti del sistema

| Parte | Cosa fa | Quando lavora |
|---|---|---|
| **Dashboard** | Ti mostra le offerte, i filtri, i link per candidarti | Quando la apri tu |
| **Ricerca manuale** | Pulsante «🔍 Cerca ora» nella barra laterale | Quando la premi tu |
| **Guardiano** | Controlla da solo e ti manda l'email | Ogni 15 minuti, anche a dashboard chiusa |

---

## Il guardiano (avvisi email)

Si accende e si spegne dalla barra laterale, sezione **📧 Avvisi email**.

Serve una **Password per le App** di Google (non la tua password normale):

1. `myaccount.google.com/security` → attiva la **Verifica in due passaggi**
2. `myaccount.google.com/apppasswords` → nome «Job Radar» → **Crea**
3. Copia le **16 lettere** e incollale nella dashboard
4. Premi **💾 Salva e invia email di prova**
5. Se l'email arriva, premi **▶️ Attiva il guardiano**

La password finisce nel **Portachiavi di macOS**, mai in un file.
Puoi revocarla in qualsiasi momento dalla stessa pagina di Google.

### Comandi da Terminale (se preferisci)

```bash
# vedere se il guardiano è acceso
launchctl list | grep jobradar

# fare subito un giro di controllo, senza aspettare
cd ~/job-radar && .venv/bin/python sorveglianza.py

# leggere cosa ha fatto
tail -20 ~/job-radar/guardiano.log

# spegnerlo
launchctl bootout gui/$(id -u)/com.jobradar.guardiano
```

> ⚠️ Il guardiano funziona solo a **Mac acceso e non spento del tutto**.
> Con il coperchio chiuso il Mac dorme e i controlli riprendono al risveglio.

---

## Personalizzare il profilo

Tutto sta nel file **`config.py`**, scritto in italiano. Puoi cambiare:

- `RUOLI` — i ruoli che cerchi
- `CITTA_TARGET` / `SETTORI_TARGET` — le tue priorità (quelle con la ⭐)
- `COMPETENZE` — le parole del tuo CV e quanto pesano nel punteggio di match
- `MAX_ANNI_ESPERIENZA` / `MAX_MESI_ESPERIENZA` — quanta esperienza accetti

Dopo una modifica basta ricaricare la pagina: l'archivio si riallinea da solo,
**senza rifare le ricerche**.

Per aggiungere aziende da monitorare: file **`aziende.py`**.

---

## Come vengono filtrate le offerte

Tu non hai esperienza lavorativa oltre una summer internship di 3 mesi,
quindi il programma tiene solo ciò che è davvero alla tua portata:

1. Chiede a LinkedIn solo *Stage* e *Livello base*
2. Scarta i titoli senior (Manager, Director, Head of, VP…)
3. Legge l'annuncio completo e cerca gli anni richiesti in 6 lingue
4. Distingue **richiesto** da **gradito**: «1 anno è un plus» non ti esclude
5. Confronta i mesi richiesti con i tuoi 3

Ogni offerta riceve un'etichetta:

- 🎓 **Internship** — stage, nessuna esperienza richiesta
- **Entry level** — graduate, junior, zero anni
- **Da verificare** — l'annuncio non dichiara nulla: controlla a mano

---

## I file del progetto

| File | A cosa serve |
|---|---|
| `app.py` | La dashboard |
| `config.py` | **Il tuo profilo** — modificabile |
| `aziende.py` | **Le aziende monitorate** — modificabile |
| `esperienza.py` | Le regole del filtro entry level |
| `linkedin.py` | Raccolta da LinkedIn |
| `siti_aziende.py` | Raccolta dai portali aziendali |
| `database.py` | L'archivio delle offerte |
| `notifiche.py` | Le email |
| `sorveglianza.py` | Un giro di controllo |
| `guardiano.py` | Accensione/spegnimento della sorveglianza |
| `offerte.db` | L'archivio vero e proprio |
| `impostazioni.json` | Le tue preferenze sulle notifiche |
| `guardiano.log` | Cosa ha fatto il guardiano |

---

## Se qualcosa non funziona

**«LinkedIn sta limitando le richieste»** — normale se hai cercato molto.
Aspetta 10-15 minuti. Il programma rallenta già da solo.

**L'email non parte** — quasi sempre è la password: deve essere quella
di 16 lettere generata da Google, non la tua password abituale.

**Il guardiano non manda niente** — se non ci sono offerte *nuove* non
scrive: è il comportamento giusto. Controlla `guardiano.log` per conferma.

**Il Mac chiede l'accesso al Portachiavi** — clicca **«Consenti sempre»**,
altrimenti il guardiano non riesce a leggere la password.
