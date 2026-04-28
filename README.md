<<<<<<< HEAD
# hosts_manager_gtk
Hosts Graphical Manager written in python
=======
# Hosts Manager GTK\n\nUn'interfaccia grafica GTK3 per gestire in comodità e sicurezza il file `/etc/hosts` su Linux, con supporto per filtri IPv4/IPv6, attivazione/disattivazione voci e svuotamento rapido della cache DNS.\n\n## Installazione\n\n1. Copia lo script nella tua cartella `~/.local/bin` e rendilo eseguibile:\n\n```bash\nmkdir -p ~/.local/bin\ncp hosts_manager_gtk.py ~/.local/bin/\nchmod +x ~/.local/bin/hosts_manager_gtk.py\n```\n\n2. Crea il collegamento per il menu delle applicazioni lanciando questo comando nel terminale:\n\n```bash\ncat > ~/.local/share/applications/hosts-manager.desktop << 'EOF'\n[Desktop Entry]\nName=Hosts Manager\nComment=Manage /etc/hosts\nExec=/home/diegorainero/.local/bin/hosts_manager_gtk.py\nIcon=applications-system\nTerminal=false\nType=Application\nCategories=System;\nStartupNotify=true\nEOF\n```\n\n## Dipendenze\n\nAssicurati di aver installato i pacchetti necessari:\n\n```bash\nsudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 pkexec\n```
>>>>>>> 04269e9 (Inizializzazione progetto: Hosts Manager GTK)
