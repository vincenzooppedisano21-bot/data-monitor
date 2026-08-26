#!/usr/bin/env bash
#
# INSTALLAZIONE DEL GUARDIANO SU UN SERVER LINUX (Ubuntu / Debian)
#
# Si lancia SUL SERVER, una volta sola:
#     bash installa_server.sh
#
# Fa tutto da solo: installa Python, crea l'ambiente, installa le
# librerie e configura il guardiano perche' riparta anche dopo
# un riavvio del server.

set -euo pipefail

CARTELLA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTENTE="$(whoami)"
SERVIZIO="jobradar"

echo "════════════════════════════════════════════════"
echo "  Job Radar — installazione del guardiano"
echo "  cartella: $CARTELLA"
echo "  utente:   $UTENTE"
echo "════════════════════════════════════════════════"
echo

# ---- 1. Python e strumenti di base ----
echo "▸ 1/5  Installo Python e gli strumenti necessari…"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip tzdata rsync

# ---- 2. Fuso orario italiano (le date negli avvisi devono essere giuste) ----
echo "▸ 2/5  Imposto il fuso orario su Europa/Roma…"
sudo timedatectl set-timezone Europe/Rome || true

# ---- 3. Ambiente virtuale e librerie ----
echo "▸ 3/5  Preparo l'ambiente Python…"
cd "$CARTELLA"
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
echo "   librerie installate ✓"

# ---- 4. Controllo delle credenziali ----
echo "▸ 4/5  Verifico le credenziali email…"
if [ ! -f "$CARTELLA/segreti.env" ]; then
    echo
    echo "   ⚠️  Manca il file segreti.env con l'indirizzo Gmail e la"
    echo "      Password per le App. Crealo cosi':"
    echo
    echo "      nano segreti.env"
    echo
    echo "      e incolla queste due righe (con i tuoi dati):"
    echo "      JOBRADAR_EMAIL=tuonome@gmail.com"
    echo "      JOBRADAR_PASSWORD=abcdefghijklmnop"
    echo
    echo "      Poi salva con Ctrl+O, Invio, Ctrl+X e rilancia questo script."
    exit 1
fi
chmod 600 "$CARTELLA/segreti.env"
.venv/bin/python -c "
import impostazioni, sys
if not impostazioni.configurate():
    print('   ❌ credenziali incomplete in segreti.env'); sys.exit(1)
print('   credenziali trovate ✓')
"

# ---- 5. Il guardiano come servizio di sistema ----
echo "▸ 5/5  Configuro il guardiano come servizio permanente…"
sudo tee /etc/systemd/system/${SERVIZIO}.service > /dev/null <<UNIT
[Unit]
Description=Job Radar - guardiano delle offerte di lavoro
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${UTENTE}
WorkingDirectory=${CARTELLA}
ExecStart=${CARTELLA}/.venv/bin/python ${CARTELLA}/sorveglianza.py --continuo
Restart=always
RestartSec=60
StandardOutput=append:${CARTELLA}/guardiano.log
StandardError=append:${CARTELLA}/guardiano-errori.log

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable ${SERVIZIO}
sudo systemctl restart ${SERVIZIO}
sleep 3

echo
echo "════════════════════════════════════════════════"
if systemctl is-active --quiet ${SERVIZIO}; then
    echo "  ✅ GUARDIANO ATTIVO — lavora 24 ore su 24"
else
    echo "  ❌ Il guardiano non è partito. Controlla con:"
    echo "     sudo journalctl -u ${SERVIZIO} -n 40"
fi
echo "════════════════════════════════════════════════"
echo
echo "Comandi utili:"
echo "  sudo systemctl status ${SERVIZIO}     → come sta"
echo "  sudo systemctl restart ${SERVIZIO}    → riavvialo"
echo "  sudo systemctl stop ${SERVIZIO}       → fermalo"
echo "  tail -f ${CARTELLA}/guardiano.log     → guardalo lavorare"
