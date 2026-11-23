"""Four cooperating desktop UI windows named in the report's UML diagram."""

import tkinter as tk
from tkinter import messagebox
from datetime import date
from .domain import MetricType, NumericMetric, TimePeriod, UserProfile

BG = "#101318"
PANEL = "#1b2028"
PANEL2 = "#252c36"
FG = "#f2f4f7"
MUTED = "#9aa4b2"
GREEN = "#54d6a0"
RED = "#ff746f"


class PillButton(tk.Canvas):
    def __init__(self, parent, text, command, selected=False, width=100, height=40):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            cursor="hand2",
        )
        self.text = text
        self.command = command
        self.selected = selected
        self.bind("<Button-1>", lambda _e: self.command())
        self.bind("<Configure>", lambda _e: self.draw())
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width() or int(self["width"])
        h = self.winfo_height() or int(self["height"])
        fill = GREEN if self.selected else PANEL2
        color = "#10251c" if self.selected else FG
        r = h // 2
        self.create_oval(0, 0, h, h, fill=fill, outline=fill)
        self.create_oval(w - h, 0, w, h, fill=fill, outline=fill)
        self.create_rectangle(r, 0, w - r, h, fill=fill, outline=fill)
        self.create_text(
            w / 2,
            h / 2,
            text=self.text,
            fill=color,
            font=("TkDefaultFont", 10, "bold" if self.selected else "normal"),
        )


class ProfileWindow(tk.Toplevel):
    def __init__(self, parent, service, on_saved=None):
        super().__init__(parent)
        self.service = service
        self.on_saved = on_saved
        self.title("Профиль пользователя")
        self.geometry("720x600")
        self.minsize(640, 540)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.transient(parent)
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)
        self._form()
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _form(self):
        p = self.service.get_profile()
        form = self.body
        form.columnconfigure(0, weight=1)
        head = tk.Frame(form, bg=BG)
        head.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 20))
        avatar = tk.Canvas(head, width=68, height=68, bg=BG, highlightthickness=0)
        avatar.pack(side="left", padx=(0, 17))
        avatar.create_oval(2, 2, 66, 66, fill="#203c35", outline="#315c4e", width=2)
        initials = "".join(part[0] for part in p.name.split()[:2]).upper() or "?"
        avatar.create_text(
            34, 34, text=initials, fill=GREEN, font=("TkDefaultFont", 20, "bold")
        )
        titlebox = tk.Frame(head, bg=BG)
        titlebox.pack(side="left", fill="y", pady=5)
        tk.Label(
            titlebox,
            text="Профиль пользователя",
            font=("TkDefaultFont", 22, "bold"),
            bg=BG,
            fg=FG,
        ).pack(anchor="w")
        tk.Label(
            titlebox,
            text="Личные и биологические характеристики",
            bg=BG,
            fg=MUTED,
            font=("TkDefaultFont", 11),
        ).pack(anchor="w", pady=(5, 0))

        card = tk.Frame(form, bg=PANEL, padx=24, pady=14, highlightthickness=0, bd=0)
        card.grid(row=1, column=0, sticky="ew", padx=30)
        card.columnconfigure(1, weight=1)
        self.values = {
            k: tk.StringVar(value=str(v))
            for k, v in {
                "Имя": p.name,
                "Пол": p.gender,
                "Возраст": p.age,
                "Рост": p.height_cm,
                "Вес": p.weight_kg,
            }.items()
        }
        for row, label in enumerate(("Имя", "Пол", "Возраст", "Рост", "Вес")):
            line = tk.Frame(card, bg=PANEL)
            line.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
            line.columnconfigure(1, weight=1)
            tk.Label(
                line,
                text=label,
                bg=PANEL,
                fg="#c2cbd5",
                font=("TkDefaultFont", 11, "bold"),
                width=12,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=(0, 12))
            if label == "Пол":
                choices = tk.Frame(line, bg=PANEL)
                choices.grid(row=0, column=1, sticky="w")
                self.gender_buttons = []
                for gender in ("Женский", "Мужской", "Не указан"):
                    btn = PillButton(
                        choices,
                        gender,
                        lambda value=gender: self._select_gender(value),
                        selected=(gender == p.gender),
                        width=118,
                        height=40,
                    )
                    btn.pack(side="left", padx=(0, 7))
                    self.gender_buttons.append((gender, btn))
            else:
                unit = {"Рост": "см", "Вес": "кг", "Возраст": "лет"}.get(label, "")
                field = tk.Frame(line, bg=PANEL2, highlightthickness=0, bd=0)
                field.grid(row=0, column=1, sticky="ew")
                field.columnconfigure(0, weight=1)
                entry = tk.Entry(
                    field,
                    textvariable=self.values[label],
                    bg=PANEL2,
                    fg=FG,
                    insertbackground=FG,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    font=("TkDefaultFont", 13),
                )
                entry.grid(row=0, column=0, sticky="ew", padx=12, pady=9)
                if unit:
                    tk.Label(
                        field,
                        text=unit,
                        bg=PANEL2,
                        fg=MUTED,
                        font=("TkDefaultFont", 10),
                    ).grid(row=0, column=1, padx=12)
        footer = tk.Frame(form, bg=BG)
        footer.grid(row=2, column=0, sticky="ew", padx=30, pady=(22, 25))
        tk.Label(
            footer,
            text="Изменения сохраняются локально",
            bg=BG,
            fg=MUTED,
            font=("TkDefaultFont", 9),
        ).pack(side="left", pady=12)
        PillButton(footer, "Отмена", self.destroy, width=130, height=46).pack(
            side="right", padx=(8, 0)
        )
        PillButton(
            footer, "Сохранить", self.on_save, selected=True, width=155, height=46
        ).pack(side="right")

    def _select_gender(self, value):
        self.values["Пол"].set(value)
        for gender, button in self.gender_buttons:
            button.selected = gender == value
            button.draw()

    def on_save(self):
        try:
            name = self.values["Имя"].get().strip()
            age = int(self.values["Возраст"].get())
            height = int(self.values["Рост"].get())
            weight = int(self.values["Вес"].get())
            if not name or age < 1 or height < 50 or weight < 10:
                raise ValueError
            self.service.save_profile(
                UserProfile(name, self.values["Пол"].get(), age, height, weight)
            )
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода",
                "Проверьте имя и числовые характеристики профиля.",
                parent=self,
            )
            return
        if self.on_saved:
            self.on_saved()
        self.destroy()

    def on_edit_clicked(self):
        return self._form()

    def show_error(self, message):
        messagebox.showerror("Ошибка", message, parent=self)


class DevicesWindow(tk.Toplevel):
    def __init__(self, parent, manager, on_sync=None):
        super().__init__(parent)
        self.manager = manager
        self.on_sync = on_sync
        self.title("Носимые устройства")
        self.geometry("780x540")
        self.minsize(700, 480)
        self.configure(bg=BG)
        self.transient(parent)
        tk.Label(
            self, text="Устройства", bg=BG, fg=FG, font=("TkDefaultFont", 21, "bold")
        ).pack(anchor="w", padx=25, pady=(22, 3))
        tk.Label(
            self, text="Подключение и синхронизация носимых гаджетов", bg=BG, fg=MUTED
        ).pack(anchor="w", padx=25, pady=(0, 18))
        self.rows = tk.Frame(self, bg=BG)
        self.rows.pack(fill="both", expand=True, padx=18)
        self.refresh()
        tk.Label(
            self,
            text="В прототипе соединение и измерения симулируются.",
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", padx=25, pady=12)

    def refresh(self):
        for child in self.rows.winfo_children():
            child.destroy()
        for device in self.manager.get_devices():
            card = tk.Frame(self.rows, bg=PANEL, padx=16, pady=13)
            card.pack(fill="x", pady=6)
            left = tk.Frame(card, bg=PANEL)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(
                left,
                text=device.name,
                bg=PANEL,
                fg=FG,
                font=("TkDefaultFont", 12, "bold"),
            ).pack(anchor="w")
            tk.Label(
                left,
                text=f"{device.model}  ·  {'Подключено' if device.connected else 'Не подключено'}",
                bg=PANEL,
                fg=GREEN if device.connected else MUTED,
            ).pack(anchor="w", pady=(5, 0))
            PillButton(
                card,
                "Отключить" if device.connected else "Подключить",
                lambda d=device: self.toggle(d),
                width=130,
            ).pack(side="right", padx=5)
            if device.connected:
                PillButton(
                    card,
                    "Синхронизировать",
                    lambda d=device: self.sync(d),
                    selected=True,
                    width=160,
                ).pack(side="right", padx=5)

    def toggle(self, device):
        ok = (
            self.manager.disconnect(device)
            if device.connected
            else self.manager.connect(device)
        )
        if ok is False:
            messagebox.showerror(
                "Подключение", "Не удалось подключиться к устройству.", parent=self
            )
        self.refresh()
        if self.on_sync:
            self.on_sync()

    def on_scan_clicked(self):
        self.manager.scan_devices()
        self.refresh()

    def on_connect_clicked(self, device):
        return self.manager.connect_device(device)

    def on_disconnect_clicked(self, device):
        return self.manager.disconnect_device(device)

    def on_sync_clicked(self, device=None):
        return self.manager.synchronize(device)

    def sync(self, device):
        ok = self.manager.synchronize(device)
        if not ok:
            messagebox.showerror(
                "Синхронизация", "Не удалось получить данные устройства.", parent=self
            )
        elif self.on_sync:
            self.on_sync()


class ReportWindow(tk.Toplevel):
    def __init__(self, parent, analyzer, device_manager):
        super().__init__(parent)
        self.analyzer = analyzer
        self.device_manager = device_manager
        self.title("MyHeath — Анализ показателей")
        self.geometry("1120x760")
        self.minsize(900, 650)
        self.configure(bg=BG)
        self.metric = MetricType.HEART_RATE
        self.period = TimePeriod.WEEK
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=28, pady=(22, 12))
        tk.Label(
            top,
            text="Динамика показателей",
            bg=BG,
            fg=FG,
            font=("TkDefaultFont", 23, "bold"),
        ).pack(anchor="w", pady=(0, 14))
        pickers = tk.Frame(top, bg=BG)
        pickers.pack(fill="x")
        tk.Label(
            pickers,
            text="ПОКАЗАТЕЛЬ",
            bg=BG,
            fg=MUTED,
            font=("TkDefaultFont", 9, "bold"),
        ).pack(side="left", padx=(0, 10))
        self.metric_buttons = []
        for kind in MetricType:
            b = PillButton(
                pickers,
                kind.label,
                lambda k=kind: self.set_metric(k),
                selected=(kind == self.metric),
                width=116,
                height=42,
            )
            b.pack(side="left", padx=4)
            self.metric_buttons.append((kind, b))
        tk.Label(
            pickers, text="ПЕРИОД", bg=BG, fg=MUTED, font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(24, 10))
        self.period_buttons = []
        for period in TimePeriod.options():
            b = PillButton(
                pickers,
                period.label,
                lambda p=period: self.set_period(p),
                selected=(period == self.period),
                width=94,
                height=42,
            )
            b.pack(side="left", padx=4)
            self.period_buttons.append((period, b))
        self.canvas = tk.Canvas(self, bg=PANEL, highlightthickness=0, height=350)
        self.canvas.pack(fill="both", expand=True, padx=24, pady=10)
        self.stats = tk.Frame(self, bg=BG)
        self.stats.pack(fill="x", padx=18, pady=(0, 15))
        self.canvas.bind("<Configure>", lambda _e: self.show())
        self.show()

    def set_metric(self, kind):
        self.metric = kind
        self.on_metric_selected()
        self._select_buttons()
        self.show()

    def set_period(self, period):
        self.period = period
        self.on_period_selected()
        self._select_buttons()
        self.show()

    def on_metric_selected(self):
        pass

    def on_period_selected(self):
        pass

    def on_build_report_clicked(self):
        self.show_report(self.analyzer.build_report(self.metric, self.period))

    def show_report(self, report):
        self.report = report
        self.show()

    def _select_buttons(self):
        for kind, b in self.metric_buttons:
            b.selected = kind == self.metric
            b.draw()
        for period, b in self.period_buttons:
            b.selected = period == self.period
            b.draw()

    def show(self):
        kind = self.metric
        period = self.period
        if not any(d.connected for d in self.device_manager.get_devices()):
            self.canvas.delete("all")
            self.canvas.create_text(
                max(self.canvas.winfo_width(), 600) / 2,
                max(self.canvas.winfo_height(), 300) / 2,
                text="Подключите устройство, чтобы просматривать показатели",
                fill=FG,
                font=("TkDefaultFont", 15, "bold"),
            )
            for x in self.stats.winfo_children():
                x.destroy()
            return
        report = self.analyzer.build_report(kind, period)
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 600)
        h = max(c.winfo_height(), 300)
        left, right, top, bottom = 65, w - 24, 25, h - 45
        values = [m.value for m in report.values]
        if not values:
            c.create_text(
                w / 2,
                h / 2,
                text="Нет данных за выбранный период",
                fill=MUTED,
                font=("TkDefaultFont", 14),
            )
            return
        lo = min(values)
        hi = max(values)
        delta = max(hi - lo, 1)
        lo -= delta * 0.2
        hi += delta * 0.2
        for j in range(5):
            y = top + j * (bottom - top) / 4
            c.create_line(left, y, right, y, fill="#303743")
            c.create_text(
                left - 10,
                y,
                text=f"{hi - j * (hi - lo) / 4:.0f}",
                fill=MUTED,
                anchor="e",
            )
        if kind in (MetricType.STEPS, MetricType.CALORIES):
            bars = self._aggregate(report.values, period)
            gap = 8
            bw = max(5, (right - left) / max(1, len(bars)) - gap)
            for i, (label, value) in enumerate(bars):
                x = left + i * (right - left) / max(1, len(bars)) + (gap / 2)
                y = bottom - (value - lo) / (hi - lo) * (bottom - top)
                c.create_rectangle(
                    x, y, x + bw, bottom, fill=GREEN, outline="", width=0
                )
                if len(bars) <= 14 or i % max(1, len(bars) // 10) == 0:
                    c.create_text(
                        x + bw / 2,
                        bottom + 18,
                        text=label,
                        fill=MUTED,
                        font=("TkDefaultFont", 8),
                    )
        else:
            points = []
            for i, value in enumerate(values):
                x = left + (right - left) * i / max(1, len(values) - 1)
                y = bottom - (value - lo) / (hi - lo) * (bottom - top)
                points.extend((x, y))
            if len(values) > 1:
                c.create_line(*points, fill=GREEN, width=3, smooth=True)
            for i in range(0, len(values), max(1, len(values) // 8)):
                x, y = points[2 * i : 2 * i + 2]
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=GREEN, outline="")
                c.create_text(
                    x,
                    bottom + 18,
                    text=report.values[i].recorded_at.strftime("%d.%m"),
                    fill=MUTED,
                    font=("TkDefaultFont", 8),
                )
        for x in self.stats.winfo_children():
            x.destroy()
        for title, value in (
            ("Среднее", report.average),
            ("Минимум", report.minimum),
            ("Максимум", report.maximum),
        ):
            if value is None:
                continue
            box = tk.Frame(self.stats, bg=PANEL, padx=18, pady=12)
            box.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(box, text=title, bg=PANEL, fg=MUTED).pack(anchor="w")
            tk.Label(
                box,
                text=f"{value:.1f} {kind.unit}",
                bg=PANEL,
                fg=FG,
                font=("TkDefaultFont", 16, "bold"),
            ).pack(anchor="w", pady=(5, 0))

    def _aggregate(self, values, period):
        if period == TimePeriod.YEAR:
            groups = {}
            for item in values:
                groups.setdefault(item.recorded_at.strftime("%m.%y"), []).append(
                    item.value
                )
        else:
            groups = {item.recorded_at.strftime("%d.%m"): [] for item in values}
            for item in values:
                groups[item.recorded_at.strftime("%d.%m")].append(item.value)
        return [(key, sum(vals) / len(vals)) for key, vals in groups.items() if vals]


class MainWindow(tk.Tk):
    def __init__(self, injector):
        super().__init__()
        self.injector = injector
        self.title("MyHeath")
        self.geometry("1380x880")
        self.minsize(1080, 720)
        self.configure(bg=BG)
        self._child_windows = {}
        self._build()
        self.refresh()

    def _build(self):
        self.sidebar = tk.Frame(self, bg="#15191f", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(
            self.sidebar,
            text="●  MyHeath",
            bg="#15191f",
            fg=GREEN,
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", padx=22, pady=(28, 38))
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        for label, action in (
            ("Главная", self.refresh),
            ("Показатели", self.open_report),
            ("Устройства", self.open_devices),
            ("Профиль", self.open_profile),
        ):
            PillButton(self.sidebar, label, action, width=190, height=46).pack(
                fill="x", padx=12, pady=4
            )
        self.top = tk.Frame(self.content, bg=BG)
        self.top.pack(fill="x", padx=32, pady=(22, 8))
        tk.Label(
            self.top,
            text="Обзор здоровья",
            bg=BG,
            fg=FG,
            font=("TkDefaultFont", 25, "bold"),
        ).pack(side="left")
        self.profile_button = PillButton(
            self.top, "Профиль", self.open_profile, width=165, height=46
        )
        self.profile_button.pack(side="right")
        tk.Label(
            self.content,
            text="Сводка последних показателей и состояния подключенных устройств",
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", padx=34, pady=(0, 17))
        self.cards = tk.Frame(self.content, bg=BG)
        self.cards.pack(fill="x", padx=26)
        self.lower = tk.Frame(self.content, bg=BG)
        self.lower.pack(fill="both", expand=True, padx=32, pady=18)

    def refresh(self):
        profile = self.injector.profile_service.get_profile()
        self.profile_button.text = profile.name
        self.profile_button.draw()
        for x in self.cards.winfo_children():
            x.destroy()
        for col in range(4):
            self.cards.columnconfigure(col, weight=1)
        devices = self.injector.device_manager.get_devices()
        connected = [d for d in devices if d.connected]
        if not connected:
            empty = tk.Frame(self.cards, bg=PANEL, padx=24, pady=20)
            empty.grid(row=0, column=0, columnspan=4, sticky="ew", padx=6)
            tk.Label(
                empty,
                text="Устройство не подключено",
                bg=PANEL,
                fg=FG,
                font=("TkDefaultFont", 15, "bold"),
            ).pack(anchor="w")
            tk.Label(
                empty,
                text="Подключите браслет или часы, чтобы увидеть показатели здоровья за сегодня.",
                bg=PANEL,
                fg="#c2cbd5",
                font=("TkDefaultFont", 11),
            ).pack(anchor="w", pady=(7, 13))
            PillButton(
                empty,
                "Подключить устройство",
                self.open_devices,
                selected=True,
                width=220,
                height=48,
            ).pack(anchor="w")
        else:
            for i, kind in enumerate(MetricType):
                report = self.injector.data_analyzer.build_report(kind, TimePeriod.DAY)
                value = report.values[-1].value if report.values else 0
                box = tk.Frame(
                    self.cards,
                    bg=PANEL,
                    padx=20,
                    pady=19,
                    highlightthickness=1,
                    highlightbackground="#2a313b",
                )
                box.grid(row=0, column=i, sticky="nsew", padx=6)
                tk.Label(
                    box,
                    text=kind.label.upper(),
                    bg=PANEL,
                    fg="#c2cbd5",
                    font=("TkDefaultFont", 10, "bold"),
                ).pack(anchor="w")
                tk.Label(
                    box,
                    text=f"{value:.1f}"
                    if kind == MetricType.SLEEP
                    else f"{value:,.0f}".replace(",", " "),
                    bg=PANEL,
                    fg=FG,
                    font=("TkDefaultFont", 26, "bold"),
                ).pack(anchor="w", pady=(8, 0))
                tk.Label(box, text=kind.unit + "  ·  сегодня", bg=PANEL, fg=GREEN).pack(
                    anchor="w"
                )
        for x in self.lower.winfo_children():
            x.destroy()
        self.lower.columnconfigure(0, weight=3)
        self.lower.columnconfigure(1, weight=2)
        left = tk.Frame(self.lower, bg=PANEL, padx=22, pady=20)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(
            left,
            text="Сводка за сегодня",
            bg=PANEL,
            fg=FG,
            font=("TkDefaultFont", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left, text="Последнее обновление показателей", bg=PANEL, fg="#c2cbd5"
        ).pack(anchor="w", pady=(5, 12))
        if connected:
            tk.Label(
                left,
                text=f"Данные получены от {connected[0].name}",
                bg=PANEL,
                fg=GREEN,
                font=("TkDefaultFont", 11),
            ).pack(anchor="w")
            tk.Label(
                left,
                text="Откройте раздел «Показатели», чтобы изучить динамику по периодам.",
                bg=PANEL,
                fg="#c2cbd5",
                wraplength=560,
                justify="left",
            ).pack(anchor="w", pady=14)
            PillButton(
                left,
                "Открыть показатели",
                self.open_report,
                selected=True,
                width=210,
                height=46,
            ).pack(anchor="w")
        else:
            tk.Label(
                left,
                text="После подключения и синхронизации здесь появится сводка за текущий день.",
                bg=PANEL,
                fg="#c2cbd5",
                wraplength=560,
                justify="left",
            ).pack(anchor="w", pady=12)
        right = tk.Frame(self.lower, bg=PANEL, padx=22, pady=20)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(
            right,
            text="Подключенные\nустройства",
            bg=PANEL,
            fg=FG,
            font=("TkDefaultFont", 15, "bold"),
            justify="left",
        ).pack(anchor="w", pady=(0, 10))
        tk.Label(
            right,
            text=f"{len(connected)} подключено из {len(devices)}",
            bg=PANEL,
            fg=GREEN,
        ).pack(anchor="w")
        PillButton(
            right, "Управлять устройствами", self.open_devices, width=220, height=46
        ).pack(anchor="w", pady=(18, 10))
        PillButton(
            right,
            "Сформировать отчет",
            self.open_report,
            selected=True,
            width=220,
            height=46,
        ).pack(anchor="w")

    def _open_child(self, key, factory):
        window = self._child_windows.get(key)
        if window is not None and window.winfo_exists():
            window.deiconify()
            window.lift()
            window.focus_force()
            return window
        window = factory()
        self._child_windows[key] = window
        window.bind(
            "<Destroy>",
            lambda event, k=key, w=window: (
                self._child_windows.pop(k, None) if event.widget is w else None
            ),
            add="+",
        )
        return window

    def open_profile(self):
        return self._open_child(
            "profile", lambda: self.injector.create_profile_window(self, self.refresh)
        )

    def open_devices(self):
        return self._open_child(
            "devices", lambda: self.injector.create_devices_window(self, self.refresh)
        )

    def open_report(self):
        return self._open_child(
            "report", lambda: self.injector.create_report_window(self)
        )

    def on_sync_clicked(self):
        self.show_sync_result(self.injector.device_manager.synchronize())

    def on_open_profile_clicked(self):
        self.open_profile()

    def on_open_devices_clicked(self):
        self.open_devices()

    def on_open_report_clicked(self):
        self.open_report()

    def show_sync_result(self, success):
        if success:
            self.refresh()
