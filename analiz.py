import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, Listbox, Menu, messagebox, Toplevel
import os
import re
from datetime import datetime
import webbrowser
from pyvis.network import Network
from pygments import lex
from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.token import Token

class ProjeAnalizAraci:
    ANALIZ_DESENI = re.compile(r"""
        (?:include|require|require_once)\s*\(?\s*['"]([^'"]+)['"]\s*\)?|
        (?:href|src|action)\s*=\s*['"]([^'"]+)['"]|
        header\s*\(\s*['"]Location:\s*([^'"]+)['"]\s*\)|
        url\s*\(\s*['"]?([^'")]+)['"]?\s*\)
    """, re.VERBOSE | re.IGNORECASE)
    TAHMIN_DESENI = re.compile(r"""
        ['"]([^'"]+\.(?:php|html|css|js|jpg|png|gif|svg))['"]
    """, re.VERBOSE | re.IGNORECASE)
    GIRIS_NOKTALARI = ('index.php', 'index.html', 'main.js', 'app.js', 'style.css', 'main.css')
    KESIN_AKTIF_DOSYALAR = ('config.php', 'wp-config.php', 'database.php', 'db.php', 'functions.php', 'helpers.php', 'init.php', 'autoload.php', '.env')

    def __init__(self, root):
        self.root = root
        self.root.title("Proje Bağımlılık Analiz Aracı (v5.4 Vurgulu Sekmeler)")
        self.root.geometry("1200x850")

        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Segoe UI', 10))
        style.map("TNotebook.Tab", 
            background=[("selected", "#d1e7ff")],
            foreground=[("selected", "#00539c")]
        )

        self.translations = self.get_full_translations()
        self.current_language = tk.StringVar(value='tr')
        self.current_language.trace("w", self.change_language)
        self.proje_koku, self.tum_dosyalar = "", set()
        self.dosya_haritasi, self.aktif_dosyalar, self.bostaki_dosyalar, self.dosya_koku_haritasi = {}, set(), [], {}
        
        self.menu_bar = Menu(root); root.config(menu=self.menu_bar)
        self.dil_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Dil", menu=self.dil_menu)
        self.dil_menu.add_radiobutton(label="Türkçe", variable=self.current_language, value='tr')
        self.dil_menu.add_radiobutton(label="English", variable=self.current_language, value='en')
        self.dil_menu.add_radiobutton(label="中文", variable=self.current_language, value='zh')
        self.dil_menu.add_radiobutton(label="Русский", variable=self.current_language, value='ru')
        self.yardim_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Yardım", menu=self.yardim_menu)
        self.yardim_menu.add_command(label="Hakkında", command=self.show_about_dialog)
        
        self.ana_cerceve = tk.Frame(self.root, padx=10, pady=10)
        self.ana_cerceve.pack(fill=tk.BOTH, expand=True)
        self.kontrol_cerceve = ttk.LabelFrame(self.ana_cerceve, padding=10)
        self.kontrol_cerceve.pack(fill=tk.X)
        
        self.sec_buton = tk.Button(self.kontrol_cerceve, command=self.analizi_baslat)
        self.sec_buton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.export_button = tk.Button(self.kontrol_cerceve, command=self.export_results, state='disabled')
        self.export_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.graph_button = tk.Button(self.kontrol_cerceve, command=self.generate_graph, state='disabled')
        self.graph_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.etiket_bilgi = tk.Label(self.kontrol_cerceve)
        self.etiket_bilgi.grid(row=0, column=3, padx=10, pady=5, sticky='w')

        self.manuel_aktif_etiket = ttk.Label(self.kontrol_cerceve)
        self.manuel_aktif_etiket.grid(row=1, column=0, columnspan=4, padx=5, pady=(10, 0), sticky='w')
        self.manuel_aktif_girdisi = tk.Entry(self.kontrol_cerceve, font=("Courier New", 9))
        self.manuel_aktif_girdisi.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky='we')
        self.haric_tut_etiket = ttk.Label(self.kontrol_cerceve)
        self.haric_tut_etiket.grid(row=3, column=0, columnspan=4, padx=5, pady=(10, 0), sticky='w')
        self.haric_tut_girdisi = tk.Entry(self.kontrol_cerceve, font=("Courier New", 9))
        self.haric_tut_girdisi.insert(0, "node_modules, vendor, .git, cache, build, dist")
        self.haric_tut_girdisi.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='we')

        self.notebook = ttk.Notebook(self.ana_cerceve)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        self.rapor_tabi = tk.Frame(self.notebook); self.bostaki_dosyalar_tabi = tk.Frame(self.notebook)
        self.notebook.add(self.rapor_tabi); self.notebook.add(self.bostaki_dosyalar_tabi)
        self.rapor_alani = scrolledtext.ScrolledText(self.rapor_tabi, wrap=tk.WORD, font=("Courier New", 10))
        self.rapor_alani.pack(fill=tk.BOTH, expand=True)
        self.yatay_panel = ttk.PanedWindow(self.bostaki_dosyalar_tabi, orient=tk.HORIZONTAL)
        self.yatay_panel.pack(fill=tk.BOTH, expand=True)
        self.bostaki_liste_cerceve = tk.Frame(self.yatay_panel)
        self.bostaki_dosya_listesi = Listbox(self.bostaki_liste_cerceve, font=("Courier New", 10))
        self.bostaki_dosya_listesi.pack(fill=tk.BOTH, expand=True); self.bostaki_dosya_listesi.bind('<<ListboxSelect>>', self.dosyayi_incele)
        self.yatay_panel.add(self.bostaki_liste_cerceve, weight=1)
        self.inceleme_paneli = ttk.PanedWindow(self.yatay_panel, orient=tk.VERTICAL)
        self.yatay_panel.add(self.inceleme_paneli, weight=3)
        self.ust_inceleme_cerceve = ttk.Frame(self.inceleme_paneli); self.alt_inceleme_cerceve = ttk.Frame(self.inceleme_paneli)
        self.inceleme_alani = scrolledtext.ScrolledText(self.ust_inceleme_cerceve, wrap=tk.WORD, font=("Courier New", 10))
        self.inceleme_alani.pack(fill=tk.BOTH, expand=True); self.inceleme_paneli.add(self.ust_inceleme_cerceve, weight=1)
        self.dosya_icerik_alani = scrolledtext.ScrolledText(self.alt_inceleme_cerceve, wrap=tk.WORD, font=("Courier New", 10))
        self.dosya_icerik_alani.pack(fill=tk.BOTH, expand=True); self.inceleme_paneli.add(self.alt_inceleme_cerceve, weight=1)
        self.durum_cerceve = tk.Frame(self.ana_cerceve); self.durum_cerceve.pack(fill=tk.X, pady=(5,0))
        self.durum_etiketi = tk.Label(self.durum_cerceve); self.durum_etiketi.pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(self.durum_cerceve, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)
        self.configure_syntax_highlighting_tags()
        self.update_ui_text()

    def _t(self, key): return self.translations[self.current_language.get()][key]
    def change_language(self, *args): self.update_ui_text()
    def show_about_dialog(self):
        about_window = Toplevel(self.root)
        about_window.title(self._t('about_title'))
        about_window.geometry("500x350"); about_window.resizable(False, False); about_window.transient(self.root)
        text_area = scrolledtext.ScrolledText(about_window, wrap=tk.WORD, font=("Arial", 10), padx=10, pady=10)
        text_area.pack(fill=tk.BOTH, expand=True)
        about_content = (f"{self._t('about_what_it_does_title')}\n{self._t('about_what_it_does_text')}\n\n"
                         f"{self._t('about_supported_files_title')}\n{self._t('about_supported_files_text')}\n\n"
                         f"{self._t('about_developer_title')}\n{self._t('about_developer_text')}")
        text_area.insert(tk.END, about_content); text_area.config(state='disabled')
    def update_ui_text(self):
        self.root.title(self._t('app_title'))
        self.menu_bar.entryconfig(1, label=self._t('menu_language'))
        self.menu_bar.entryconfig(2, label=self._t('menu_help'))
        self.yardim_menu.entryconfig(0, label=self._t('menu_about'))
        self.kontrol_cerceve.config(text=self._t('control_panel'))
        self.sec_buton.config(text=self._t('select_folder_button'))
        self.export_button.config(text=self._t('export_button'))
        self.graph_button.config(text=self._t('graph_button'))
        self.etiket_bilgi.config(text=self._t('select_folder_label'))
        self.manuel_aktif_etiket.config(text=self._t('manual_files_label'))
        self.haric_tut_etiket.config(text=self._t('ignore_files_label'))
        self.notebook.tab(0, text=self._t('tab_summary_map'))
        # Analiz sonuçları varsa sekme başlığını sayıyla güncelle, yoksa normal bırak
        if self.bostaki_dosyalar or not self.proje_koku:
             self.notebook.tab(1, text=f"{self._t('tab_orphan_analysis')} ({len(self.bostaki_dosyalar)})")
        else:
            self.notebook.tab(1, text=self._t('tab_orphan_analysis'))
        self.durum_etiketi.config(text=self._t('status_waiting'))
    def configure_syntax_highlighting_tags(self):
        self.dosya_icerik_alani.tag_configure(str(Token.Keyword), foreground='#CC7A00')
        self.dosya_icerik_alani.tag_configure(str(Token.Name.Function), foreground='#C42DA8')
        self.dosya_icerik_alani.tag_configure(str(Token.Name.Class), foreground='#C42DA8')
        self.dosya_icerik_alani.tag_configure(str(Token.Name.Tag), foreground='#0075C4')
        self.dosya_icerik_alani.tag_configure(str(Token.Name.Attribute), foreground='#996E00')
        self.dosya_icerik_alani.tag_configure(str(Token.String), foreground='#23A853')
        self.dosya_icerik_alani.tag_configure(str(Token.Comment), foreground='#A6A6A6')
        self.dosya_icerik_alani.tag_configure(str(Token.Operator), foreground='#CC7A00')
        self.dosya_icerik_alani.tag_configure(str(Token.Number), foreground='#23A853')
        self.dosya_icerik_alani.tag_configure(str(Token.Punctuation), foreground='#808080')
    def analizi_baslat(self):
        self.export_button.config(state='disabled'); self.graph_button.config(state='disabled')
        self.notebook.tab(1, text=self._t('tab_orphan_analysis'))
        klasor_yolu = filedialog.askdirectory()
        if not klasor_yolu: return
        onay = messagebox.askokcancel(title=self._t('warning_title'), message=self._t('warning_message'))
        if not onay: self.etiket_bilgi.config(text=self._t('analysis_cancelled')); return
        self.proje_koku = klasor_yolu
        self.etiket_bilgi.config(text=f"{self._t('selected_folder')}: {self.proje_koku}")
        self.rapor_alani.delete('1.0', tk.END); self.bostaki_dosya_listesi.delete(0, tk.END); self.inceleme_alani.delete('1.0', tk.END); self.dosya_icerik_alani.delete('1.0', tk.END)
        self.tum_dosyalar.clear(); self.dosya_haritasi.clear(); self.aktif_dosyalar.clear(); self.bostaki_dosyalar.clear(); self.dosya_koku_haritasi.clear()
        self.root.after(100, self.analiz_surecini_calistir)
    def analiz_surecini_calistir(self):
        self.durum_etiketi.config(text=self._t('status_listing')); self.root.update_idletasks()
        ignore_list = [d.strip() for d in self.haric_tut_girdisi.get().strip().split(',') if d.strip()]
        for root, dirs, files in os.walk(self.proje_koku):
            dirs[:] = [d for d in dirs if d not in ignore_list]
            for file_adi in files:
                tam_yol = os.path.normcase(os.path.normpath(os.path.join(root, file_adi)))
                self.tum_dosyalar.add(tam_yol)
        toplam_dosya = len(self.tum_dosyalar)
        self.progress_bar["maximum"] = toplam_dosya; self.progress_bar["value"] = 0
        for i, dosya_yolu in enumerate(self.tum_dosyalar):
            yuzde = int(((i + 1) / toplam_dosya) * 100) if toplam_dosya > 0 else 0
            self.durum_etiketi.config(text=f"{self._t('status_analyzing')} ({i+1}/{toplam_dosya}) [{yuzde}%]")
            self.progress_bar["value"] = i + 1
            self.root.update_idletasks()
            self.dosya_icerigini_analiz_et(dosya_yolu)
        self.raporu_olustur()
        self.durum_etiketi.config(text=f"{self._t('status_done')}! {toplam_dosya} {self._t('files_scanned')}.")
    def dosya_icerigini_analiz_et(self, dosya_yolu):
        try:
            with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f: icerik = f.read()
        except Exception: return
        bulunan_yollar = set()
        for desen in [self.ANALIZ_DESENI, self.TAHMIN_DESENI]:
            bulunanlar = desen.findall(icerik)
            for eslesme in bulunanlar:
                hedef_yol = next((s for s in eslesme if isinstance(s, str) and s), None) if isinstance(eslesme, tuple) else eslesme
                if hedef_yol: bulunan_yollar.add(hedef_yol)
        if not bulunan_yollar: return
        gecerli_dizin = os.path.dirname(dosya_yolu)
        for hedef_dosya_yolu_relatif in bulunan_yollar:
            if hedef_dosya_yolu_relatif.startswith(('http:', 'https:', '//', 'data:', '#', 'mailto:', 'tel:')): continue
            hedef_dosya_yolu_mutlak = os.path.normcase(os.path.normpath(os.path.abspath(os.path.join(gecerli_dizin, hedef_dosya_yolu_relatif))))
            if os.path.isfile(hedef_dosya_yolu_mutlak) and hedef_dosya_yolu_mutlak in self.tum_dosyalar:
                if dosya_yolu != hedef_dosya_yolu_mutlak:
                    self.dosya_haritasi.setdefault(dosya_yolu, []).append(hedef_dosya_yolu_mutlak)
                    self.aktif_dosyalar.add(dosya_yolu); self.aktif_dosyalar.add(hedef_dosya_yolu_mutlak)
        for taranan_dosya in self.tum_dosyalar:
            dosya_adi = os.path.basename(taranan_dosya)
            dosya_koku, _ = os.path.splitext(dosya_adi)
            if dosya_koku and (f"'{dosya_koku}'" in icerik or f'"{dosya_koku}"' in icerik):
                self.dosya_koku_haritasi.setdefault(taranan_dosya, []).append(dosya_yolu)
                self.aktif_dosyalar.add(dosya_yolu); self.aktif_dosyalar.add(taranan_dosya)
    def raporu_olustur(self):
        manuel_aktifler = set()
        manuel_girdi = self.manuel_aktif_girdisi.get().strip()
        if manuel_girdi:
            manuel_dosyalar = [dosya.strip() for dosya in manuel_girdi.split(',')]
            for dosya in self.tum_dosyalar:
                if os.path.basename(dosya) in manuel_dosyalar: manuel_aktifler.add(dosya)
        for dosya in self.tum_dosyalar:
            if os.path.basename(dosya).lower() in self.GIRIS_NOKTALARI: self.aktif_dosyalar.add(dosya)
            if os.path.basename(dosya).lower() in self.KESIN_AKTIF_DOSYALAR: self.aktif_dosyalar.add(dosya)
        self.aktif_dosyalar.update(manuel_aktifler)
        self.bostaki_dosyalar = sorted(list(self.tum_dosyalar - self.aktif_dosyalar))
        self.rapor_alani.delete('1.0', tk.END)
        self.rapor_alani.insert(tk.END, f"--- {self._t('summary_title')} ---\n")
        self.rapor_alani.insert(tk.END, f"{self._t('total_files_scanned')}: {len(self.tum_dosyalar)}\n")
        self.rapor_alani.insert(tk.END, f"{self._t('active_files')}: {len(self.aktif_dosyalar)}\n")
        self.rapor_alani.insert(tk.END, f"  - {self._t('manually_added')}: {len(manuel_aktifler)}\n")
        self.rapor_alani.insert(tk.END, f"{self._t('orphan_files_estimated')}: {len(self.bostaki_dosyalar)}\n\n")
        self.rapor_alani.insert(tk.END, f"--- {self._t('dependency_map_title')} ---\n")
        baglanti_bulan_dosyalar = [dosya for dosya, baglilar in self.dosya_haritasi.items() if baglilar]
        if not baglanti_bulan_dosyalar: self.rapor_alani.insert(tk.END, self._t('no_links_found') + "\n")
        else:
            for ana_dosya in sorted(baglanti_bulan_dosyalar):
                bagli_dosyalar = sorted(list(set(self.dosya_haritasi[ana_dosya])))
                self.rapor_alani.insert(tk.END, f"FILE: {os.path.relpath(ana_dosya, self.proje_koku)}\n")
                for bagli_dosya in bagli_dosyalar: self.rapor_alani.insert(tk.END, f"  -> {os.path.relpath(bagli_dosya, self.proje_koku)}\n")
                self.rapor_alani.insert(tk.END, "\n")
        self.notebook.tab(1, text=f"{self._t('tab_orphan_analysis')} ({len(self.bostaki_dosyalar)})")
        self.bostaki_dosya_listesi.delete(0, tk.END)
        for dosya in self.bostaki_dosyalar: self.bostaki_dosya_listesi.insert(tk.END, os.path.relpath(dosya, self.proje_koku))
        self.export_button.config(state='normal')
        if any(self.dosya_haritasi.values()): self.graph_button.config(state='normal')
        self.notebook.select(self.rapor_tabi)
    def dosyayi_incele(self, event):
        secili_indeksler = self.bostaki_dosya_listesi.curselection()
        if not secili_indeksler: return
        secili_dosya_relatif = self.bostaki_dosya_listesi.get(secili_indeksler[0])
        secili_dosya_mutlak = os.path.normcase(os.path.normpath(os.path.join(self.proje_koku, secili_dosya_relatif)))
        self.inceleme_alani.delete('1.0', tk.END)
        self.inceleme_alani.insert(tk.END, f"--- {self._t('file_inspection')}: {secili_dosya_relatif} ---\n\n")
        self.inceleme_alani.insert(tk.END, f"{self._t('status')}: {self._t('marked_as_orphan')}.\n")
        self.inceleme_alani.insert(tk.END, f"{self._t('reason')}: {self._t('reason_no_direct_link')}.\n\n")
        self.inceleme_alani.insert(tk.END, f"--- {self._t('related_files')} ---\n")
        bahseden_dosyalar = self.dosya_koku_haritasi.get(secili_dosya_mutlak)
        if bahseden_dosyalar:
            self.inceleme_alani.insert(tk.END, self._t('related_files_found') + ":\n")
            for dosya in bahseden_dosyalar: self.inceleme_alani.insert(tk.END, f"- {os.path.relpath(dosya, self.proje_koku)}\n")
        else: self.inceleme_alani.insert(tk.END, self._t('related_files_not_found') + ".\n")
        self.inceleme_alani.insert(tk.END, "\n")
        self.inceleme_alani.insert(tk.END, f"--- {self._t('outbound_links')} ---\n")
        verdigi_linkler = self.dosya_haritasi.get(secili_dosya_mutlak)
        if verdigi_linkler:
            for link in verdigi_linkler: self.inceleme_alani.insert(tk.END, f"-> {os.path.relpath(link, self.proje_koku)}\n")
        else: self.inceleme_alani.insert(tk.END, self._t('no_outbound_links') + ".\n")
        self.dosya_icerik_alani.config(state=tk.NORMAL)
        self.dosya_icerik_alani.delete('1.0', tk.END)
        try:
            with open(secili_dosya_mutlak, 'r', encoding='utf-8', errors='ignore') as f: icerik = f.read()
            lexer = get_lexer_for_filename(secili_dosya_mutlak, stripall=True)
            for token, text in lex(icerik, lexer): self.dosya_icerik_alani.insert(tk.END, text, str(token))
        except Exception as e:
            self.dosya_icerik_alani.insert(tk.END, f"{self._t('file_read_error')}.\n\n{self._t('error')}: {e}")
        self.dosya_icerik_alani.config(state=tk.DISABLED)
    def export_results(self):
        if not self.tum_dosyalar: messagebox.showwarning(self._t('export_error_title'), self._t('export_error_no_data')); return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[(self._t('text_files'), "*.txt"), (self._t('all_files'), "*.*")], initialfile=self._t('export_default_filename'), title=self._t('export_dialog_title'))
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"{self._t('app_title')}\n{'='*50}\n"); f.write(f"{self._t('export_report_date')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{self._t('selected_folder')}: {self.proje_koku}\n{'='*50}\n\n"); f.write(self.rapor_alani.get('1.0', tk.END)); f.write("\n\n")
                f.write(f"{'='*50}\n--- {self._t('orphan_files_list_title')} ---\n{'='*50}\n\n")
                if self.bostaki_dosyalar:
                    for dosya in self.bostaki_dosyalar: f.write(f"- {os.path.relpath(dosya, self.proje_koku)}\n")
                else: f.write(self._t('no_orphan_files_found'))
            messagebox.showinfo(self._t('export_success_title'), f"{self._t('export_success_message')}\n{filepath}")
        except Exception as e: messagebox.showerror(self._t('export_error_title'), f"{self._t('export_error_generic')}\n{e}")
    def generate_graph(self):
        if not self.dosya_haritasi: messagebox.showwarning(self._t('graph_error_title'), self._t('graph_error_no_data')); return
        filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Dosyası", "*.html")], initialfile=self._t('graph_default_filename'), title=self._t('graph_dialog_title'))
        if not filepath: return
        net = Network(height="100vh", width="100%", directed=True, notebook=False, cdn_resources='local')
        net.barnes_hut(gravity=-8000, central_gravity=0.1, spring_length=250, spring_strength=0.005, damping=0.09, overlap=0.1)
        aktif_dugumler = set()
        for ana_dosya, bagli_dosyalar in self.dosya_haritasi.items():
            if bagli_dosyalar:
                aktif_dugumler.add(ana_dosya)
                for bagli in bagli_dosyalar: aktif_dugumler.add(bagli)
        for dugum in aktif_dugumler:
            label = os.path.basename(dugum)
            title = os.path.relpath(dugum, self.proje_koku)
            net.add_node(dugum, label=label, title=title)
        for ana_dosya, bagli_dosyalar in self.dosya_haritasi.items():
            for bagli in bagli_dosyalar:
                if ana_dosya in aktif_dugumler and bagli in aktif_dugumler: net.add_edge(ana_dosya, bagli)
        net.show_buttons(filter_=['physics'])
        try:
            net.save_graph(filepath)
            webbrowser.open('file://' + os.path.realpath(filepath))
            messagebox.showinfo(self._t('graph_success_title'), f"{self._t('graph_success_message')}\n{filepath}")
        except Exception as e: messagebox.showerror(self._t('graph_error_title'), f"{self._t('graph_error_generic')}\n{e}")

    def get_full_translations(self):
        return {
            'tr': {'app_title': "Proje Analiz Aracı (v5.4 Final)", 'menu_language': "Dil", 'menu_help': "Yardım", 'menu_about': "Hakkında", 'control_panel': "Kontrol Paneli", 'select_folder_button': "Proje Klasörünü Seç", 'export_button': "Dışarı Aktar (.txt)", 'graph_button': "Görsel Harita Oluştur", 'select_folder_label': "Analiz edilecek klasörü seçin.", 'manual_files_label': "Manuel Aktif Dosyalar (virgülle ayırın):", 'ignore_files_label': "Hariç Tutulacak Klasörler (virgülle ayırın):", 'tab_summary_map': "Özet ve Bağımlılık Haritası", 'tab_orphan_analysis': "Boştaki Dosyalar Analizi", 'status_waiting': "Durum: Bekleniyor...", 'warning_title': "Uyarı ve Sorumluluk Reddi", 'warning_message': "Bu uygulama test aşamasındadır ve statik kod analizi yapar. Analiz %100 isabetli olmayabilir.\n\nDevam etmeden önce proje dosyalarınızı yedeklemeniz önemle tavsiye edilir.\n\nBu uygulamanın kullanımından doğabilecek herhangi bir veri kaybı veya sorundan geliştirici sorumlu tutulamaz. Devam etmek istiyor musunuz?", 'analysis_cancelled': "Analiz iptal edildi.", 'selected_folder': "Seçilen Klasör", 'status_listing': "Durum: Dosyalar listeleniyor...", 'status_analyzing': "Durum: Analiz ediliyor...", 'status_done': "Durum: Analiz tamamlandı", 'files_scanned': "dosya incelendi", 'summary_title': "SEZGİSEL ANALİZ ÖZETİ", 'total_files_scanned': "Toplam İncelenen Dosya", 'active_files': "Bağlantılı (Aktif) Dosya", 'manually_added': "Manuel Olarak Eklendi", 'orphan_files_estimated': "Boşta (Yetim) Dosya Tahmini", 'dependency_map_title': "PROJE BAĞIMLILIK HARİTASI", 'no_links_found': "Dosyalar arasında doğrudan bir bağlantı bulunamadı.", 'file_inspection': "DOSYA İNCELEME", 'status': "DURUM", 'marked_as_orphan': "Boşta (Yetim) Olarak İşaretlendi", 'reason': "NEDEN", 'reason_no_direct_link': "Bu dosyaya doğrudan bir link ('include', 'href' vb.) bulunamadı", 'related_files': "İLGİLİ OLABİLECEK DOSYALAR", 'related_files_found': "Bu dosyanın adı/kökü şu dosyalarda metin olarak bulundu", 'related_files_not_found': "Bu dosyanın adı/kökü başka bir dosyada metin olarak bulunamadı", 'outbound_links': "BU DOSYANIN VERDİĞİ BAĞLANTILAR", 'no_outbound_links': "Bu dosya başka bir dosyaya doğrudan link vermiyor", 'file_read_error': "Dosya içeriği okunamadı", 'error': "Hata", 'about_title': "Hakkında: Proje Analiz Aracı", 'about_what_it_does_title': "Bu Uygulama Ne Yapar?", 'about_what_it_does_text': "Bu araç, seçilen bir proje klasöründeki dosyaları tarayarak aralarındaki bağlantıları (include, href, src vb.) ve olası dinamik kullanımları tespit eder. Amacı, projedeki hiçbir yerden çağrılmayan, 'boşta' veya 'yetim' kalmış dosyaları bularak kod temizliğine yardımcı olmaktır.", 'about_supported_files_title': "Desteklenen Analiz Türleri", 'about_supported_files_text': "PHP (include, require), HTML (href, src, action), CSS (url()), JavaScript (dosya adı içeren metinler) ve diğer metin tabanlı dosyalar arasındaki ilişkileri analiz eder.", 'about_developer_title': "Geliştirici", 'about_developer_text': "Bu uygulama Rıza Mert AKÇA tarafından hazırlanmıştır.", 'export_default_filename': "proje_analiz_raporu", 'export_dialog_title': "Raporu Farklı Kaydet", 'export_report_date': "Rapor Tarihi", 'orphan_files_list_title': "BOŞTA (YETİM) DOSYALARIN LİSTESİ", 'no_orphan_files_found': "Boşta duran dosya bulunamadı.", 'export_success_title': "Başarılı", 'export_success_message': "Rapor başarıyla kaydedildi:", 'export_error_title': "Dışarı Aktarma Hatası", 'export_error_no_data': "Dışarı aktarılacak analiz verisi bulunmuyor.", 'export_error_generic': "Dosya kaydedilirken bir hata oluştu:", 'text_files': "Metin Dosyaları", 'all_files': "Tüm Dosyalar", 'graph_error_title': "Grafik Hatası", 'graph_error_no_data': "Grafik oluşturmak için bağlantı verisi bulunmuyor.", 'graph_default_filename': "proje_haritasi.html", 'graph_dialog_title': "Grafik Haritasını Kaydet", 'graph_success_title': "Başarılı", 'graph_success_message': "Grafik başarıyla oluşturuldu ve tarayıcıda açıldı:", 'graph_error_generic': "Grafik oluşturulurken bir hata oluştu:"},
            'en': {'app_title': "Project Analysis Tool (v5.4 Final)",'menu_language': "Language",'menu_help': "Help",'menu_about': "About",'control_panel': "Control Panel",'select_folder_button': "Select Project Folder",'export_button': "Export (.txt)",'graph_button': "Generate Visual Map",'select_folder_label': "Select a folder to analyze.",'manual_files_label': "Manual Active Files (comma-separated):",'ignore_files_label': "Folders to Exclude (comma-separated):",'tab_summary_map': "Summary & Dependency Map",'tab_orphan_analysis': "Orphan File Analysis",'status_waiting': "Status: Waiting...",'warning_title': "Warning & Disclaimer",'warning_message': "This application is in a testing phase and performs static code analysis. The analysis may not be 100% accurate.\n\nIt is strongly recommended to back up your project files before proceeding.\n\nThe developer cannot be held responsible for any data loss or issues that may arise from the use of this application. Do you want to continue?",'analysis_cancelled': "Analysis cancelled.",'selected_folder': "Selected Folder",'status_listing': "Status: Listing files...",'status_analyzing': "Status: Analyzing...",'status_done': "Status: Analysis complete",'files_scanned': "files scanned",'summary_title': "HEURISTIC ANALYSIS SUMMARY",'total_files_scanned': "Total Files Scanned",'active_files': "Linked (Active) Files",'manually_added': "Manually Added",'orphan_files_estimated': "Orphan (Unused) Files Estimate",'dependency_map_title': "PROJECT DEPENDENCY MAP",'no_links_found': "No direct links were found between files.",'file_inspection': "FILE INSPECTION",'status': "STATUS",'marked_as_orphan': "Marked as Orphan",'reason': "REASON",'reason_no_direct_link': "No direct link ('include', 'href', etc.) to this file was found",'related_files': "POSSIBLY RELATED FILES",'related_files_found': "This file's name/root was found as text in the following files",'related_files_not_found': "This file's name/root was not found as text in any other file",'outbound_links': "OUTBOUND LINKS FROM THIS FILE",'no_outbound_links': "This file does not directly link to any other file",'file_read_error': "Could not read file content",'error': "Error",'about_title': "About: Project Analysis Tool",'about_what_it_does_title': "What Does This Application Do?",'about_what_it_does_text': "This tool scans files in a selected project folder to identify connections (include, href, src, etc.) and potential dynamic usages. Its purpose is to help with code cleanup by finding 'orphan' files that are not called from anywhere in the project.",'about_supported_files_title': "Supported Analysis Types",'about_supported_files_text': "It analyzes relationships between PHP (include, require), HTML (href, src, action), CSS (url()), JavaScript (text containing filenames), and other text-based files.",'about_developer_title': "Developer",'about_developer_text': "This application was prepared by Rıza Mert AKÇA.",'export_default_filename': "project_analysis_report",'export_dialog_title': "Save Report As",'export_report_date': "Report Date",'orphan_files_list_title': "LIST OF ORPHAN (UNUSED) FILES",'no_orphan_files_found': "No orphan files found.",'export_success_title': "Success",'export_success_message': "Report saved successfully:",'export_error_title': "Export Error",'export_error_no_data': "No analysis data to export.",'export_error_generic': "An error occurred while saving the file:",'text_files': "Text Files",'all_files': "All Files",'graph_error_title': "Graph Error",'graph_error_no_data': "No link data available to generate a graph.",'graph_default_filename': "project_map.html",'graph_dialog_title': "Save Graph Map",'graph_success_title': "Success",'graph_success_message': "Graph successfully generated and opened in browser:",'graph_error_generic': "An error occurred while generating the graph:"},
            'zh': {'app_title': "项目分析工具 (v5.4 最终版)",'menu_language': "语言",'menu_help': "帮助",'menu_about': "关于",'control_panel': "控制面板",'select_folder_button': "选择项目文件夹",'export_button': "导出 (.txt)",'graph_button': "生成可视化图",'select_folder_label': "请选择要分析的文件夹。",'manual_files_label': "手动激活的文件 (用逗号分隔):",'ignore_files_label': "要排除的文件夹 (用逗号分隔):",'tab_summary_map': "摘要和依赖图",'tab_orphan_analysis': "孤立文件分析",'status_waiting': "状态: 等待中...",'warning_title': "警告与免责声明",'warning_message': "此应用程序处于测试阶段，执行静态代码分析。分析可能不是100%准确。\n\n强烈建议在继续操作前备份您的项目文件。\n\n对于因使用此应用程序而可能产生的任何数据丢失或问题，开发者概不负责。您要继续吗？",'analysis_cancelled': "分析已取消。",'selected_folder': "选定的文件夹",'status_listing': "状态: 正在列出文件...",'status_analyzing': "状态: 正在分析...",'status_done': "状态: 分析完成",'files_scanned': "个文件已扫描",'summary_title': "启发式分析摘要",'total_files_scanned': "扫描的文件总数",'active_files': "链接的 (活动) 文件",'manually_added': "手动添加",'orphan_files_estimated': "孤立 (未使用) 文件估计",'dependency_map_title': "项目依赖图",'no_links_found': "在文件之间未找到直接链接。",'file_inspection': "文件检查",'status': "状态",'marked_as_orphan': "标记为孤立",'reason': "原因",'reason_no_direct_link': "未找到指向此文件的直接链接 ('include', 'href' 等)",'related_files': "可能相关的文件",'related_files_found': "在以下文件中找到了该文件的名称/根作为文本",'related_files_not_found': "在任何其他文件中均未找到该文件的名称/根作为文本",'outbound_links': "从此文件出站的链接",'no_outbound_links': "此文件不直接链接到任何其他文件",'file_read_error': "无法读取文件内容",'error': "错误",'about_title': "关于: 项目分析工具",'about_what_it_does_title': "这个应用程序做什么？",'about_what_it_does_text': "该工具扫描所选项目文件夹中的文件，以识别连接（include, href, src 等）和潜在的动态用法。其目的是通过查找项目中任何地方都未调用的“孤立”文件来帮助进行代码清理。",'about_supported_files_title': "支持的分析类型",'about_supported_files_text': "它分析 PHP (include, require), HTML (href, src, action), CSS (url()), JavaScript (包含文件名的文本) 和其他基于文本的文件之间的关系。",'about_developer_title': "开发者",'about_developer_text': "此应用程序由 Rıza Mert AKÇA 编写。",'export_default_filename': "项目分析报告",'export_dialog_title': "报告另存为",'export_report_date': "报告日期",'orphan_files_list_title': "孤立 (未使用) 文件列表",'no_orphan_files_found': "未找到孤立文件。",'export_success_title': "成功",'export_success_message': "报告已成功保存:",'export_error_title': "导出错误",'export_error_no_data': "没有可导出的分析数据。",'export_error_generic': "保存文件时发生错误:",'text_files': "文本文件",'all_files': "所有文件",'graph_error_title': "图表错误",'graph_error_no_data': "没有可用于生成图表的链接数据。",'graph_default_filename': "项目图.html",'graph_dialog_title': "保存图表",'graph_success_title': "成功",'graph_success_message': "图表已成功生成并在浏览器中打开:",'graph_error_generic': "生成图表时发生错误:"},
            'ru': {'app_title': "Инструмент анализа проектов (v5.4 Финальная)",'menu_language': "Язык",'menu_help': "Помощь",'menu_about': "О программе",'control_panel': "Панель управления",'select_folder_button': "Выбрать папку проекта",'export_button': "Экспорт (.txt)",'graph_button': "Создать визуальную карту",'select_folder_label': "Выберите папку для анализа.",'manual_files_label': "Активные файлы вручную (через запятую):",'ignore_files_label': "Папки для исключения (через запятую):",'tab_summary_map': "Сводка и карта зависимостей",'tab_orphan_analysis': "Анализ изолированных файлов",'status_waiting': "Статус: Ожидание...",'warning_title': "Предупреждение и отказ от ответственности",'warning_message': "Это приложение находится на стадии тестирования и выполняет статический анализ кода. Анализ может быть не на 100% точным.\n\nНастоятельно рекомендуется сделать резервную копию файлов вашего проекта перед продолжением.\n\nРазработчик не несет ответственности за любую потерю данных или проблемы, которые могут возникнуть в результате использования этого приложения. Вы хотите продолжить?",'analysis_cancelled': "Анализ отменен.",'selected_folder': "Выбранная папка",'status_listing': "Статус: Составление списка файлов...",'status_analyzing': "Статус: Анализ...",'status_done': "Статус: Анализ завершен",'files_scanned': "файлов отсканировано",'summary_title': "СВОДКА ЭВРИСТИЧЕСКОГО АНАЛИЗА",'total_files_scanned': "Всего отсканировано файлов",'active_files': "Связанные (активные) файлы",'manually_added': "Добавлено вручную",'orphan_files_estimated': "Предположительно изолированные (неиспользуемые) файлы",'dependency_map_title': "КАРТА ЗАВИСИМОСТЕЙ ПРОЕКТА",'no_links_found': "Прямые ссылки между файлами не найдены.",'file_inspection': "ПРОВЕРКА ФАЙЛА",'status': "СТАТУС",'marked_as_orphan': "Помечен как изолированный",'reason': "ПРИЧИНА",'reason_no_direct_link': "Прямая ссылка на этот файл ('include', 'href' и т.д.) не найдена",'related_files': "ВОЗМОЖНО СВЯЗАННЫЕ ФАЙЛЫ",'related_files_found': "Имя/корень этого файла найден как текст в следующих файлах",'related_files_not_found': "Имя/корень этого файла не найден как текст в других файлах",'outbound_links': "ИСХОДЯЩИЕ ССЫЛКИ ИЗ ЭТОГО ФАЙЛА",'no_outbound_links': "Этот файл не ссылается напрямую на другие файлы",'file_read_error': "Не удалось прочитать содержимое файла",'error': "Ошибка",'about_title': "О программе: Инструмент анализа проектов",'about_what_it_does_title': "Что делает это приложение?",'about_what_it_does_text': "Этот инструмент сканирует файлы в выбранной папке проекта для выявления связей (include, href, src и т.д.) и потенциальных динамических использований. Его цель - помочь в очистке кода путем поиска 'изолированных' файлов, которые нигде не вызываются в проекте.",'about_supported_files_title': "Поддерживаемые типы анализа",'about_supported_files_text': "Анализирует отношения между файлами PHP (include, require), HTML (href, src, action), CSS (url()), JavaScript (текст, содержащий имена файлов) и другими текстовыми файлами.",'about_developer_title': "Разработчик",'about_developer_text': "Это приложение было подготовлено Rıza Mert AKÇA.",'export_default_filename': "отчет_анализа_проекта",'export_dialog_title': "Сохранить отчет как",'export_report_date': "Дата отчета",'orphan_files_list_title': "СПИСОК ИЗОЛИРОВАННЫХ (НЕИСПОЛЬЗУЕМЫХ) ФАЙЛОВ",'no_orphan_files_found': "Изолированные файлы не найдены.",'export_success_title': "Успех",'export_success_message': "Отчет успешно сохранен:",'export_error_title': "Ошибка экспорта",'export_error_no_data': "Нет данных анализа для экспорта.",'export_error_generic': "Произошла ошибка при сохранении файла:",'text_files': "Текстовые файлы",'all_files': "Все файлы",'graph_error_title': "Ошибка графика",'graph_error_no_data': "Нет данных о связях для создания графика.",'graph_default_filename': "карта_проекта.html",'graph_dialog_title': "Сохранить карту графика",'graph_success_title': "Успех",'graph_success_message': "График успешно создан и открыт в браузере:",'graph_error_generic': "Произошла ошибка при создании графика:"}
        }

if __name__ == "__main__":
    root = tk.Tk()
    uygulama = ProjeAnalizAraci(root)
    root.mainloop()