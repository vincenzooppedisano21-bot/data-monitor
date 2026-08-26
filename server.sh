#!/usr/bin/env bash
#
# COLLEGAMENTO TRA IL TUO MAC E IL SERVER
#
# Si lancia dal MAC. Tre comandi:
#
#   ./server.sh invia       → copia il programma sul server
#   ./server.sh scarica     → scarica sul Mac le offerte trovate dal server
#   ./server.sh stato       → mostra se il guardiano sta lavorando
#
# La prima volta, scrivi qui sotto l'indirizzo del tuo server.

# ───── CONFIGURAZIONE (da compilare una volta sola) ─────
SERVER="${JOBRADAR_SERVER:-}"          # es. root@203.0.113.45
CARTELLA_REMOTA="/opt/job-radar"
# ────────────────────────────────────────────────────────

set -euo pipefail
LOCALE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$SERVER" ]; then
    echo "❌ Devi prima indicare l'indirizzo del server."
    echo
    echo "   Apri questo file (server.sh) e scrivi il tuo server nella riga"
    echo "   SERVER=\"\"   →   SERVER=\"root@INDIRIZZO-DEL-TUO-SERVER\""
    echo
    echo "   Oppure lancialo così, una volta sola:"
    echo "   JOBRADAR_SERVER=root@1.2.3.4 ./server.sh invia"
    exit 1
fi

case "${1:-}" in

  invia)
    echo "▸ Copio il programma su $SERVER:$CARTELLA_REMOTA …"
    ssh "$SERVER" "mkdir -p $CARTELLA_REMOTA"
    rsync -avz --progress \
        --exclude '.venv' --exclude '__pycache__' --exclude '*.log' \
        --exclude 'offerte.db' --exclude 'app_step2_backup.py' \
        --exclude '.streamlit' --exclude 'com.jobradar.guardiano.plist' \
        "$LOCALE/" "$SERVER:$CARTELLA_REMOTA/"
    echo
    echo "✅ Fatto. Ora collegati al server e installa:"
    echo "   ssh $SERVER"
    echo "   cd $CARTELLA_REMOTA && bash installa_server.sh"
    ;;

  scarica)
    echo "▸ Scarico dal server le offerte trovate…"
    if [ -f "$LOCALE/offerte.db" ]; then
        cp "$LOCALE/offerte.db" "$LOCALE/offerte.db.backup"
        echo "   (copia di sicurezza dell'archivio locale salvata)"
    fi
    rsync -avz "$SERVER:$CARTELLA_REMOTA/offerte.db" "$LOCALE/offerte.db"
    echo "✅ Archivio aggiornato. Ricarica la dashboard nel browser."
    ;;

  stato)
    echo "▸ Stato del guardiano su $SERVER:"
    echo
    ssh "$SERVER" "systemctl is-active jobradar && \
                   echo '--- ultime righe del registro ---' && \
                   tail -15 $CARTELLA_REMOTA/guardiano.log"
    ;;

  *)
    echo "Uso:  ./server.sh [invia | scarica | stato]"
    echo
    echo "  invia     copia il programma sul server"
    echo "  scarica   porta sul Mac le offerte trovate dal server"
    echo "  stato     controlla che il guardiano stia lavorando"
    exit 1
    ;;
esac
