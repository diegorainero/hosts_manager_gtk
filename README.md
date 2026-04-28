# 🌐 Hosts Manager GTK

Un'interfaccia grafica GTK3 per gestire in comodità e sicurezza il file `/etc/hosts` su sistemi Linux. 
Semplifica la modifica dei record host con supporto per filtri, attivazione/disattivazione rapida delle voci e gestione della cache.

---

## ✨ Funzionalità Principali

- **🛡️ Gestione Sicura**: Modifica il file `/etc/hosts` in modo sicuro (richiede privilegi di amministratore tramite `pkexec` al momento del salvataggio).
- **🔍 Filtri Intelligenti**: Visualizza e filtra facilmente le voci per tipo (IPv4 o IPv6).
- **✅ Attiva/Disattiva Voci**: Abilita o disabilita singoli record con un semplice click, commentandoli automaticamente senza doverli cancellare.
- **🧹 Svuotamento Cache DNS**: Funzionalità rapida integrata per pulire la cache DNS del sistema.
- **🖥️ Interfaccia GTK3**: Design nativo, pulito e perfettamente integrato con il tuo ambiente desktop Linux.

---

## 📦 Dipendenze

Assicurati di aver installato i pacchetti necessari per l'esecuzione. Su sistemi basati su Debian/Ubuntu, puoi eseguire:

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 pkexec
```

---

## 🚀 Installazione

1. **Prepara l'eseguibile**  
   Copia lo script nella tua cartella `~/.local/bin` e rendilo eseguibile:

   ```bash
   mkdir -p ~/.local/bin
   cp hosts_manager_gtk.py ~/.local/bin/
   chmod +x ~/.local/bin/hosts_manager_gtk.py
   ```

2. **Crea il collegamento nel menu delle applicazioni**  
   Lancia questo comando nel terminale (sostituisci `tuoutente` con il tuo vero nome utente, oppure usa il comando così com'è per generare dinamicamente il percorso):

   ```bash
   cat > ~/.local/share/applications/hosts-manager.desktop << EOF
   [Desktop Entry]
   Name=Hosts Manager
   Comment=Gestisci facilmente il file /etc/hosts
   Exec=$HOME/.local/bin/hosts_manager_gtk.py
   Icon=applications-system
   Terminal=false
   Type=Application
   Categories=System;Settings;
   StartupNotify=true
   EOF
   ```

---

## 💡 Utilizzo

Dopo aver completato l'installazione, potrai avviare **Hosts Manager** direttamente dal menu delle applicazioni del tuo sistema. 

In alternativa, puoi lanciarlo da terminale:
```bash
~/.local/bin/hosts_manager_gtk.py
```

*Nota: Quando tenterai di salvare le modifiche apportate al file `/etc/hosts`, ti verrà richiesta la password di amministratore per autorizzare l'operazione di scrittura.*

---

## 🛠️ Contribuire

Sentiti libero di aprire una *Issue* per segnalare bug o proporre nuove funzionalità, e di inviare *Pull Request* per migliorare il progetto!
