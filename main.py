import os
import json
import shutil
import subprocess
import winreg
import urllib.request
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")

CONFIG_FILE = "launcher_config.json"
SERVERS_URL = "https://snippet.host/fekqyy/raw" # ССЫЛКА НА СПИСОК СЕРВЕРОВ (МОЖЕТЕ ЗАМЕНИТЬ НА СВОЮ, СМ. В ФАЙЛЕ SERVERS.ST)

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Multiverse")
        self.geometry("950x600")
        self.resizable(False, False)
        self.configure(fg_color="#0D0E15")

        self.servers = {}
        if not self.load_remote_servers():
            messagebox.showerror("Ошибка", "Отсутсвует подключение к интернету")
            self.destroy()
            return
        
        self.saved_nicks = ["Player_Name"]
        self.selected_server = list(self.servers.keys())[0] if self.servers else "Advance Blue"
        self.saved_game_path = ""

        self.load_settings()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#121420", border_color="#1E2238", border_width=1)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_propagate(False)

        self.logo_top = ctk.CTkLabel(self.left_panel, text="Multiverse", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#FFFFFF")
        self.logo_top.pack(pady=(30, 0))
        self.logo_bot = ctk.CTkLabel(self.left_panel, text="SA-MP Launcher", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#636B93")
        self.logo_bot.pack(pady=(0, 25))

        self.line = ctk.CTkFrame(self.left_panel, height=2, fg_color="#1E2238", width=200)
        self.line.pack(pady=(0, 15))

        self.lbl_nick = ctk.CTkLabel(self.left_panel, text="Выбор или ввод никнейма", font=ctk.CTkFont(size=11, weight="bold"), text_color="#636B93")
        self.lbl_nick.pack(anchor="w", padx=30, pady=2)
        
        self.nickname_box = ctk.CTkComboBox(self.left_panel, values=self.saved_nicks, width=200, height=40, 
                                            fg_color="#16192B", border_color="#222743", text_color="#FFFFFF", corner_radius=8)
        self.nickname_box.pack(pady=(0, 15))
        self.nickname_box.set(self.saved_nicks[0])

        self.lbl_path = ctk.CTkLabel(self.left_panel, text="Директория gta_sa.exe", font=ctk.CTkFont(size=11, weight="bold"), text_color="#636B93")
        self.lbl_path.pack(anchor="w", padx=30, pady=2)
        
        self.path_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Папка не выбрана", width=200, height=35, 
                                       fg_color="#16192B", border_color="#222743", text_color="#8F96B3", font=ctk.CTkFont(size=10), corner_radius=8)
        self.path_entry.pack(pady=(0, 5))
        if self.saved_game_path:
            self.path_entry.insert(0, self.saved_game_path)
        
        self.btn_browse = ctk.CTkButton(self.left_panel, text="Выбрать путь", width=200, height=35, 
                                        fg_color="#1E2238", hover_color="#2C3252", text_color="#FFFFFF", corner_radius=8, command=self.browse_path)
        self.btn_browse.pack(pady=(0, 15))

        self.btn_vorbis = ctk.CTkButton(self.left_panel, text="Установить Vorbis", width=200, height=38, 
                                        fg_color="#2A1F3D", hover_color="#433160", text_color="#D6C4FF", 
                                        border_color="#4A3B63", border_width=1, corner_radius=8, font=ctk.CTkFont(size=11, weight="bold"),
                                        command=self.install_vorbis)
        self.btn_vorbis.pack(pady=(0, 10))

        self.btn_faq = ctk.CTkButton(self.left_panel, text="Информация / FAQ", width=200, height=38, 
                                     fg_color="#16192B", hover_color="#222743", text_color="#8F96B3", 
                                     border_color="#1E2238", border_width=1, corner_radius=8, font=ctk.CTkFont(size=11, weight="bold"),
                                     command=self.open_faq)
        self.btn_faq.pack(pady=(0, 20))

        self.lbl_ver = ctk.CTkLabel(self.left_panel, text="Multiverse launcher © 2026", font=ctk.CTkFont(size=10), text_color="#3D4260")
        self.lbl_ver.pack(side="bottom", pady=15)

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        self.header_title = ctk.CTkLabel(self.right_panel, text="Доступные сервера", font=ctk.CTkFont(size=20, weight="bold"), text_color="#FFFFFF")
        self.header_title.pack(anchor="w", pady=(10, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent", width=600, height=360)
        self.scroll_frame.pack(fill="both", expand=True)

        self.cards = {}

        for sname, sinfo in self.servers.items():
            card_frame = ctk.CTkFrame(self.scroll_frame, height=80, fg_color="#121420", corner_radius=10)
            card_frame.pack(fill="x", pady=5, padx=5)
            card_frame.pack_propagate(False)

            neon_bar = ctk.CTkFrame(card_frame, width=5, fg_color=sinfo["color"], corner_radius=4)
            neon_bar.pack(side="left", fill="y")

            info_sub = ctk.CTkFrame(card_frame, fg_color="transparent")
            info_sub.pack(side="left", padx=20, fill="y")
            
            lbl_name = ctk.CTkLabel(info_sub, text=sname, font=ctk.CTkFont(size=15, weight="bold"), text_color="#FFFFFF")
            lbl_name.pack(anchor="w", pady=(12, 0))
            
            lbl_desc = ctk.CTkLabel(info_sub, text=sinfo["desc"], font=ctk.CTkFont(size=11), text_color="#636B93")
            lbl_desc.pack(anchor="w")

            btn_select = ctk.CTkButton(card_frame, text="Выбрать", width=110, height=35, 
                                       fg_color="#1E2238", hover_color=sinfo["color"], text_color="#FFFFFF", corner_radius=6,
                                       command=lambda name=sname: self.select_server(name))
            btn_select.pack(side="right", padx=20, pady=22)

            self.cards[sname] = {"frame": card_frame, "indicator": neon_bar, "btn": btn_select}

        self.launch_bar = ctk.CTkFrame(self.right_panel, height=90, fg_color="#121420", border_color="#1E2238", border_width=1, corner_radius=12)
        self.launch_bar.pack(fill="x", pady=(15, 0))
        self.launch_bar.pack_propagate(False)

        self.selection_sub = ctk.CTkFrame(self.launch_bar, fg_color="transparent")
        self.selection_sub.pack(side="left", padx=25, fill="y")
        
        self.sel_title = ctk.CTkLabel(self.selection_sub, text="Выбранный сервер:", font=ctk.CTkFont(size=10, weight="bold"), text_color="#636B93")
        self.sel_title.pack(anchor="w", pady=(22, 0))
        
        self.sel_name = ctk.CTkLabel(self.selection_sub, text=self.selected_server, font=ctk.CTkFont(size=18, weight="bold"))
        self.sel_name.pack(anchor="w")

        self.btn_play = ctk.CTkButton(self.launch_bar, text="Войти в игру", font=ctk.CTkFont(size=14, weight="bold"), 
                                      fg_color="#00E5FF", hover_color="#00B4D8", text_color="#000000", width=240, height=50, corner_radius=8,
                                      command=self.launch_game)
        self.btn_play.pack(side="right", padx=25, pady=20)

        if self.selected_server in self.servers:
            self.select_server(self.selected_server)
        elif self.servers:
            self.select_server(list(self.servers.keys())[0])

    def load_remote_servers(self):
        try:
            req = urllib.request.Request(SERVERS_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8')
                for line in content.splitlines():
                    line = line.strip()
                    if not line or '":' not in line:
                        continue
                    parts = line.split('":', 1)
                    name = parts[0].strip('"')
                    data_str = parts[1].strip().strip('()')
                    data_str = "{" + data_str + "}"
                    server_data = json.loads(data_str)
                    self.servers[name] = server_data
                return True
        except Exception:
            return False

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.saved_nicks = data.get("nicknames", ["Player_Name"])
                    self.selected_server = data.get("selected_server", self.selected_server)
                    self.saved_game_path = data.get("game_path", "")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")

    def save_settings(self, current_nick, current_path):
        if current_nick and current_nick not in self.saved_nicks:
            self.saved_nicks.append(current_nick)

        data = {
            "nicknames": self.saved_nicks,
            "selected_server": self.selected_server,
            "game_path": current_path
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder)
            self.save_settings(self.nickname_box.get().strip(), folder)

    def select_server(self, name):
        if name not in self.servers:
            return
        self.selected_server = name
        current_color = self.servers[name]["color"]
        
        self.sel_name.configure(text=name, text_color=current_color)
        self.btn_play.configure(fg_color=current_color, hover_color=self.servers[name]["glow"])
        
        if name in ["Advance Blue", "Advance Green", "Advance Lime", "Samp RP", "MonserDM", "Trinity RP"]:
            self.btn_play.configure(text_color="#000000")
        else:
            self.btn_play.configure(text_color="#FFFFFF")

        for sname, target in self.cards.items():
            if sname == name:
                target["frame"].configure(fg_color="#1B1E30")
                target["indicator"].configure(width=12)
                target["btn"].configure(text="Выбран", fg_color=current_color, text_color="#000000" if name in ["Advance Blue", "Advance Green", "Advance Lime", "Samp RP", "MonserDM", "Trinity RP"] else "#FFFFFF")
            else:
                target["frame"].configure(fg_color="#121420")
                target["indicator"].configure(width=5)
                target["btn"].configure(text="Подключить", fg_color="#1E2238", text_color="#FFFFFF")

    def install_vorbis(self):
        game_path = self.path_entry.get().strip()
        if not game_path or not os.path.isdir(game_path):
            messagebox.showerror("Ошибка", "Сначала выберите правильный путь к игре.")
            return

        required_files = ["vorbis.dll", "vorbisFile.dll", "vorbisHooked.dll", "samp.exe", "samp.saa", "samp.dll"]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        missing_sources = [f for f in required_files if not os.path.exists(os.path.join(script_dir, f))]
        
        if missing_sources:
            messagebox.showerror("Файлы не найдены", f"Рядом с лаунчером отсутствуют:\n{', '.join(missing_sources)}")
            return

        try:
            for file_name in required_files:
                shutil.copy2(os.path.join(script_dir, file_name), os.path.join(game_path, file_name))
            messagebox.showinfo("Успех", "Файлы Vorbis ASI успешно установлены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать файлы: {e}")

    def open_faq(self):
        faq_window = ctk.CTkToplevel(self)
        faq_window.title("Технический раздел / FAQ")
        faq_window.geometry("500x420")
        faq_window.resizable(False, False)
        faq_window.configure(fg_color="#121420")
        faq_window.attributes("-topmost", True)

        title = ctk.CTkLabel(faq_window, text="Важная техническая информация", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700")
        title.pack(pady=20)

        faq_text = (
            "1. Зачем нужен Vorbis?\n"
            "Эти файлы (.dll) необходимы для интеграции мультиплеера. Без них "
            "не будут работать ASI-плагины, Cleo-скрипты, лоадеры и фиксы заходов. "
            "Установка обязательна на чистые версии игры.\n\n"
            "2. Исполнительный файл gta_sa.exe 1.0 US\n"
            "Мультиплеер SA-MP и большинство модификаций создавались строго под "
            "американскую версию gta_sa.exe 1.0. Если используется Steam-версия или "
            "европейские 1.01/2.0, игра может закрываться с ошибкой или не запускаться. "
            "Рекомендуется заменить исполняемый файл на версию '1.0 US crack'.\n\n"
            "3. Решение проблем и ошибок\n"
            "• Если игра зависает при подключении — убедитесь, что процесс корректно "
            "отображается в диспетчере задач, и проверьте папку игры на наличие конфликтующих плагинов."
        )

        text_box = ctk.CTkTextbox(faq_window, width=440, height=260, fg_color="#16192B", border_color="#1E2238", border_width=1, font=ctk.CTkFont(size=12))
        text_box.pack(padx=30, pady=5)
        text_box.insert("1.0", faq_text)
        text_box.configure(state="disabled")

        btn_close = ctk.CTkButton(faq_window, text="Закрыть", fg_color="#1E2238", hover_color="#2C3252", width=120, command=faq_window.destroy)
        btn_close.pack(pady=15)

    def launch_game(self):
        nickname = self.nickname_box.get().strip()
        game_path = self.path_entry.get().strip()
        sinfo = self.servers.get(self.selected_server)

        if not nickname:
            messagebox.showerror("Уведомление", "Пожалуйста, введите игровой никнейм.")
            return
        if not game_path or not os.path.isdir(game_path):
            messagebox.showerror("Уведомление", "Укажите корректный путь к папке игры.")
            return
        
        gta_exe = os.path.join(game_path, "gta_sa.exe")
        if not os.path.exists(gta_exe):
            messagebox.showerror("Ошибка", "Файл gta_sa.exe не найден в этой директории.")
            return

        self.save_settings(nickname, game_path)

        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\SAMP")
            winreg.SetValueEx(key, "PlayerName", 0, winreg.REG_SZ, nickname)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Лог реестра: {e}")

        try:
            os.chdir(game_path)
            subprocess.Popen([gta_exe, "-c", "-h", sinfo["ip"], "-p", sinfo["port"], "-n", nickname])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Критический сбой", f"Ошибка вызова игрового ядра:\n{e}")

if __name__ == "__main__":
    app = Main()
    if app.winfo_exists():
        app.mainloop()
