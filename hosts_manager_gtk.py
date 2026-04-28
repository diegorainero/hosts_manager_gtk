#!/usr/bin/env python3
# ~/.local/bin/hosts_manager_gtk.py

import subprocess
import os
import sys

if len(sys.argv) > 1 and sys.argv[1] == "--root-helper":
    while True:
        cmd = sys.stdin.readline()
        if not cmd:
            break
        cmd = cmd.strip()
        if cmd == "WRITE":
            length_str = sys.stdin.readline().strip()
            try:
                length = int(length_str)
                data = sys.stdin.read(length)
                with open("/etc/hosts", "w") as f:
                    f.write(data)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
            sys.stdout.flush()
        elif cmd == "FLUSH_DNS":
            try:
                if subprocess.run(["which", "resolvectl"], capture_output=True).returncode == 0:
                    subprocess.run(["resolvectl", "flush-caches"])
                elif subprocess.run(["which", "systemd-resolve"], capture_output=True).returncode == 0:
                    subprocess.run(["systemd-resolve", "--flush-caches"])
                else:
                    subprocess.run(["systemctl", "restart", "systemd-resolved"], stderr=subprocess.DEVNULL)
                    subprocess.run(["systemctl", "restart", "nscd"], stderr=subprocess.DEVNULL)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
            sys.stdout.flush()
    sys.exit(0)

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib, Gdk
except ImportError:
    print("Installa: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
    sys.exit(1)

class HostsManager:
    def __init__(self):
        self.root_proc = None
        self.window = Gtk.Window(title="Hosts Manager")
        self.window.set_default_size(800, 400)
        self.window.connect("destroy", self.on_destroy)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.window.add(vbox)

        # Toolbar
        toolbar = Gtk.Toolbar()
        vbox.pack_start(toolbar, False, False, 0)

        # Pulsanti
        refresh_btn = Gtk.ToolButton(label="Aggiorna")
        refresh_btn.connect("clicked", self.on_refresh)
        toolbar.insert(refresh_btn, 0)

        edit_btn = Gtk.ToolButton(label="Modifica")
        edit_btn.connect("clicked", self.on_edit)
        toolbar.insert(edit_btn, 1)

        save_btn = Gtk.ToolButton(label="Salva")
        save_btn.connect("clicked", self.on_save)
        toolbar.insert(save_btn, 2)

        add_btn = Gtk.ToolButton(label="Aggiungi")
        add_btn.connect("clicked", self.on_add)
        toolbar.insert(add_btn, 3)

        enable_all_btn = Gtk.ToolButton(label="Abilita tutti")
        enable_all_btn.connect("clicked", self.on_enable_all)
        toolbar.insert(enable_all_btn, 4)

        disable_all_btn = Gtk.ToolButton(label="Disabilita tutti")
        disable_all_btn.connect("clicked", self.on_disable_all)
        toolbar.insert(disable_all_btn, 5)

        flush_dns_btn = Gtk.ToolButton(label="Svuota DNS")
        flush_dns_btn.connect("clicked", self.on_flush_dns)
        toolbar.insert(flush_dns_btn, 6)

        # Filter area above list
        filter_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        filter_hbox.set_margin_start(5)
        filter_hbox.set_margin_end(5)
        filter_hbox.set_margin_top(5)
        filter_hbox.set_margin_bottom(5)

        filter_label = Gtk.Label(label="Filtra per tipo di IP:")
        filter_hbox.pack_start(filter_label, False, False, 0)

        self.current_filter = "ipv4"
        filter_combo = Gtk.ComboBoxText()
        filter_combo.append("all", "Tutti gli IP")
        filter_combo.append("ipv4", "Solo IPv4")
        filter_combo.append("ipv6", "Solo IPv6")
        filter_combo.set_active_id("ipv4")
        filter_combo.connect("changed", self.on_filter_changed)
        filter_hbox.pack_start(filter_combo, False, False, 0)

        vbox.pack_start(filter_hbox, False, False, 0)

        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)

        # Listbox
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.listbox)

        # Hosts data
        self.hosts = []
        self.hosts_file = "/etc/hosts"

        self.load_hosts()
        self.window.show_all()

    def load_hosts(self, *args):
        # Pulisci lista
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        self.hosts = []
        self.file_lines = []

        try:
            result = subprocess.run(["cat", self.hosts_file], capture_output=True, text=True)
            for orig_line in result.stdout.splitlines():
                line = orig_line.strip()

                is_active = True
                if line.startswith("#"):
                    is_active = False
                    parsed_line = line.lstrip("#").strip()
                else:
                    parsed_line = line

                if not parsed_line or "localhost" in parsed_line:
                    self.file_lines.append({"type": "raw", "text": orig_line})
                    continue

                parts = parsed_line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    if "." not in ip and ":" not in ip:
                        self.file_lines.append({"type": "raw", "text": orig_line})
                        continue

                    host_obj = {"type": "host", "parts": parts, "is_active": is_active, "checkbox": None}
                    self.file_lines.append(host_obj)

                    if self.current_filter == "ipv4" and ":" in ip:
                        continue
                    if self.current_filter == "ipv6" and "." in ip:
                        continue

                    row = Gtk.ListBoxRow()
                    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    hbox.set_margin_top(5)
                    hbox.set_margin_bottom(5)
                    hbox.set_margin_start(10)
                    hbox.set_margin_end(10)

                    # Checkbox per abilitare/disabilitare
                    checkbox = Gtk.CheckButton()
                    checkbox.set_active(is_active)
                    checkbox.connect("toggled", self.on_toggle, parts)
                    hbox.pack_start(checkbox, False, False, 0)

                    host_obj["checkbox"] = checkbox

                    # Label con IP e hostname
                    label = Gtk.Label(label=f"{parts[0]} → {' '.join(parts[1:])}")
                    label.set_halign(Gtk.Align.START)
                    hbox.pack_start(label, True, True, 0)

                    row.add(hbox)
                    self.listbox.add(row)
                    self.hosts.append({"parts": parts, "checkbox": checkbox})
                else:
                    self.file_lines.append({"type": "raw", "text": orig_line})

            self.listbox.show_all()
        except Exception as e:
            self.show_error(f"Errore caricamento: {e}")

    def on_filter_changed(self, combo):
        self.current_filter = combo.get_active_id()
        self.load_hosts()

    def on_destroy(self, widget):
        if self.root_proc is not None:
            try:
                self.root_proc.terminate()
            except:
                pass
        Gtk.main_quit()

    def _write_hosts(self, content):
        if self.root_proc is None or self.root_proc.poll() is not None:
            script_path = os.path.abspath(__file__)
            self.root_proc = subprocess.Popen(
                ["pkexec", sys.executable, script_path, "--root-helper"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        self.root_proc.stdin.write("WRITE\n")
        self.root_proc.stdin.write(f"{len(content)}\n")
        self.root_proc.stdin.write(content)
        self.root_proc.stdin.flush()

        resp = self.root_proc.stdout.readline().strip()
        if resp != "OK":
            raise Exception(f"Errore: {resp}")

    def _flush_dns(self):
        if self.root_proc is None or self.root_proc.poll() is not None:
            script_path = os.path.abspath(__file__)
            self.root_proc = subprocess.Popen(
                ["pkexec", sys.executable, script_path, "--root-helper"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        self.root_proc.stdin.write("FLUSH_DNS\n")
        self.root_proc.stdin.flush()

        resp = self.root_proc.stdout.readline().strip()
        if resp != "OK":
            raise Exception(f"Errore: {resp}")

    def on_flush_dns(self, button):
        try:
            self._flush_dns()
            self.show_message("✅ Cache DNS svuotata con successo!")
        except Exception as e:
            self.show_error(f"❌ Errore nello svuotamento DNS: {e}")

    def on_toggle(self, checkbox, parts):
        pass  # Lo stato viene salvato al click su "Salva"

    def on_refresh(self, button):
        self.load_hosts()

    def on_add(self, button):
        dialog = Gtk.Dialog(title="Aggiungi Host", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        ip_entry = Gtk.Entry(placeholder_text="Indirizzo IP (es. 192.168.1.10)")
        host_entry = Gtk.Entry(placeholder_text="Hostname (es. miopc.local)")

        box.add(ip_entry)
        box.add(host_entry)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            ip = ip_entry.get_text().strip()
            host = host_entry.get_text().strip()
            if ip and host:
                new_line = f"{ip} {host}\n"

                try:
                    with open(self.hosts_file, 'r') as orig:
                        content = orig.read()
                    if content and not content.endswith("\n"):
                        content += "\n"
                    content += new_line

                    self._write_hosts(content)
                    self.load_hosts()
                except Exception as e:
                    self.show_error(f"❌ Errore nell'aggiunta del nuovo host: {e}")

        dialog.destroy()

    def on_edit(self, button):
        subprocess.Popen(["pkexec", "gnome-text-editor", self.hosts_file])

    def on_enable_all(self, button):
        for host in self.hosts:
            host["checkbox"].set_active(True)

    def on_disable_all(self, button):
        for host in self.hosts:
            host["checkbox"].set_active(False)

    def on_save(self, button):
        lines = []
        for item in self.file_lines:
            if item["type"] == "raw":
                lines.append(item["text"])
            else:
                line = " ".join(item["parts"])

                # Determina lo stato: dalla UI se disponibile, altrimenti originale
                is_active = item["is_active"]
                if item["checkbox"] is not None:
                    is_active = item["checkbox"].get_active()

                if not is_active:
                    line = "# " + line
                lines.append(line)

        new_content = "\n".join(lines) + "\n"

        try:
            self._write_hosts(new_content)
            self.show_message("✅ Hosts salvati con successo!")
            self.load_hosts()
        except Exception as e:
            self.show_error(f"❌ Errore nel salvataggio: {e}")

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=message
        )
        dialog.run()
        dialog.destroy()

    def show_message(self, message):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=message
        )
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = HostsManager()
    Gtk.main()
