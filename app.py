import os
import csv
import math
import datetime
import warnings
from threading import Thread

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages

from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

warnings.filterwarnings("ignore")

if not os.path.exists("outputs"):
    os.makedirs("outputs")

# ══════════════════════════════════════════════════════════════════════════
#  BRANDING
# ══════════════════════════════════════════════════════════════════════════
APP_NAME     = "ExamGenius AI"
APP_TAGLINE  = "AI-Powered Intelligent Examination Management Platform"
APP_VERSION  = "v2.0"

# ══════════════════════════════════════════════════════════════════════════
#  DOMAIN CONSTANTS  (unchanged from the original engine)
# ══════════════════════════════════════════════════════════════════════════
DOMAINS = [
    "Computer Science",
    "Artificial Intelligence",
    "Business Analytics",
    "Software Engineering",
    "Electrical Engineering",
]
BATCHES = [19, 20, 21, 22, 23]
DEFAULT_TOTAL_STUDENTS = 2450
DEFAULT_ROOM_COUNT = 30

DEFAULT_DOMAIN_COUNTS = {
    "Computer Science": 550,
    "Artificial Intelligence": 500,
    "Business Analytics": 400,
    "Software Engineering": 450,
    "Electrical Engineering": 550,
}

FACULTY_NAMES = {
    "Computer Science":        ["Dr. Fayyaz Ahmed",   "Prof. Alisha Tariq", "Dr. Hashim Raza"],
    "Artificial Intelligence": ["Dr. Zainab Ahmed",    "Prof. Kamran Iqbal", "Dr. Farrukh Shah", "Prof. Malik Saeed"],
    "Business Analytics":      ["Dr. Rehan Qureshi",   "Prof. Ayesha Awan",  "Dr. Tahir Hussain"],
    "Software Engineering":    ["Dr. Ali Hassan",      "Prof. Saba Naseem",  "Dr. Usman Tariq"],
    "Electrical Engineering":  ["Dr. Tariq Mehmood",   "Prof. Sadia Kiran",  "Dr. Kashif Anwar"],
}

DOMAIN_COLORS = {
    "Computer Science":        "#4f46e5",
    "Artificial Intelligence": "#06b6d4",
    "Business Analytics":      "#f59e0b",
    "Software Engineering":    "#10b981",
    "Electrical Engineering":  "#ef4444",
}

# ══════════════════════════════════════════════════════════════════════════
#  MODERN THEME / DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg":          "#f1f4fb",   # app background
    "surface":     "#ffffff",   # card background
    "surface_alt": "#f8fafc",
    "sidebar":     "#131a3a",   # deep indigo navy
    "sidebar_hi":  "#1f2a5c",
    "primary":     "#4f46e5",   # indigo
    "primary_dk":  "#3730a3",
    "secondary":   "#06b6d4",   # cyan
    "success":     "#10b981",
    "warning":     "#f59e0b",
    "danger":      "#ef4444",
    "purple":      "#8b5cf6",
    "text":        "#0f172a",
    "text_muted":  "#64748b",
    "text_light":  "#94a3b8",
    "border":      "#e2e8f0",
    "white":       "#ffffff",
}

FONT_FAMILY = "Segoe UI"


def F(size=10, weight="normal", slant="roman"):
    return (FONT_FAMILY, size, weight, slant) if slant != "roman" else (FONT_FAMILY, size, weight)


# ──────────────────────────────────────────────────────────────────────────
#  Reusable modern widgets
# ──────────────────────────────────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    """A canvas-based button with rounded corners and a hover effect."""

    def __init__(self, parent, text, command=None, bg=COLORS["primary"],
                 hover_bg=None, fg="white", width=180, height=42,
                 font=None, radius=10, icon=""):
        super().__init__(parent, width=width, height=height,
                          bg=parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else COLORS["bg"],
                          highlightthickness=0, bd=0)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg or self._shade(bg, -14)
        self.fg_color = fg
        self.radius = radius
        self.width = width
        self.height = height
        self.text = f"{icon}  {text}" if icon else text
        self.font = font or F(11, "bold")

        self._draw(self.bg_color)
        self.bind("<Enter>", lambda e: self._draw(self.hover_color))
        self.bind("<Leave>", lambda e: self._draw(self.bg_color))
        self.bind("<Button-1>", self._on_click)

    @staticmethod
    def _shade(hex_color, amt):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + amt))
        g = max(0, min(255, g + amt))
        b = max(0, min(255, b + amt))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                  x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.create_polygon(points, smooth=True, **kw)

    def _draw(self, color):
        self.delete("all")
        self._round_rect(1, 1, self.width - 1, self.height - 1, self.radius,
                          fill=color, outline="")
        self.create_text(self.width / 2, self.height / 2, text=self.text,
                          fill=self.fg_color, font=self.font)

    def _on_click(self, _event=None):
        if self.command:
            self.command()

    def set_enabled(self, enabled):
        if enabled:
            self.bind("<Button-1>", self._on_click)
            self._draw(self.bg_color)
        else:
            self.unbind("<Button-1>")
            self._draw(COLORS["text_light"])


class Card(tk.Frame):
    """A white rounded-look card container with a subtle border."""

    def __init__(self, parent, **kw):
        pad = kw.pop("pad", 16)
        super().__init__(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, bd=0, **kw)
        self._pad = pad


class StatCard(tk.Frame):
    """Dashboard statistic card: icon, big value, label, optional trend note."""

    def __init__(self, parent, icon, label, value, color, note=""):
        super().__init__(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, width=210, height=118)
        self.pack_propagate(False)

        top = tk.Frame(self, bg=COLORS["surface"])
        top.pack(fill="x", padx=16, pady=(14, 0))

        badge = tk.Label(top, text=icon, font=F(16), bg=color, fg="white", width=2, height=1)
        badge.pack(side=tk.LEFT)

        tk.Label(top, text=label, font=F(9, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(10, 0))

        self.value_var = tk.StringVar(value=str(value))
        tk.Label(self, textvariable=self.value_var, font=F(24, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", padx=16, pady=(6, 0))

        if note:
            tk.Label(self, text=note, font=F(8), bg=COLORS["surface"],
                     fg=COLORS["text_light"]).pack(anchor="w", padx=16)

    def set(self, value):
        self.value_var.set(str(value))


class InfoTile(tk.Frame):
    """Small tile used on Educational Impact / AI Insights pages."""

    def __init__(self, parent, icon, title, body, color=COLORS["primary"]):
        super().__init__(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, width=280, height=150)
        self.pack_propagate(False)
        head = tk.Frame(self, bg=COLORS["surface"])
        head.pack(fill="x", padx=14, pady=(14, 6))
        tk.Label(head, text=icon, font=F(15), bg=color, fg="white", width=2).pack(side=tk.LEFT)
        tk.Label(head, text=title, font=F(11, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"], wraplength=190, justify="left").pack(side=tk.LEFT, padx=8)
        tk.Label(self, text=body, font=F(9), bg=COLORS["surface"], fg=COLORS["text_muted"],
                 wraplength=248, justify="left").pack(anchor="w", padx=14, pady=(0, 10))


class NavButton(tk.Frame):
    """Sidebar navigation entry with active / hover states."""

    def __init__(self, parent, icon, label, command):
        super().__init__(parent, bg=COLORS["sidebar"], height=44)
        self.pack_propagate(False)
        self.command = command
        self.active = False

        self.lbl = tk.Label(self, text=f"  {icon}   {label}", font=F(10, "bold"),
                             bg=COLORS["sidebar"], fg="#c7cdf0", anchor="w")
        self.lbl.pack(fill="both", expand=True, padx=6, pady=4)

        for w in (self, self.lbl):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", lambda e: self.command())

    def _on_enter(self, _e=None):
        if not self.active:
            self.config(bg=COLORS["sidebar_hi"])
            self.lbl.config(bg=COLORS["sidebar_hi"], fg="white")

    def _on_leave(self, _e=None):
        if not self.active:
            self.config(bg=COLORS["sidebar"])
            self.lbl.config(bg=COLORS["sidebar"], fg="#c7cdf0")

    def set_active(self, active):
        self.active = active
        bg = COLORS["primary"] if active else COLORS["sidebar"]
        self.config(bg=bg)
        self.lbl.config(bg=bg, fg="white" if active else "#c7cdf0")


# ══════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════
class ExamGeniusApp:
    """ExamGenius AI — main application controller."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} — {APP_TAGLINE}")
        self.root.geometry("1480x860")
        self.root.minsize(1200, 720)
        self.root.configure(bg=COLORS["bg"])

        # ── Data state ──────────────────────────────────────────────────
        self.student_df    = None
        self.room_df       = None
        self.faculty_df    = None
        self.seating_df    = None
        self.allocation_df = None
        self.insights       = {}
        self.pipeline_running = False
        self.activity_log = []

        self._configure_styles()
        self._build_shell()
        self.show_page("dashboard")

    # ── ttk styling ─────────────────────────────────────────────────────
    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview", font=F(9), rowheight=26,
                         background="white", fieldbackground="white",
                         bordercolor=COLORS["border"])
        style.configure("Treeview.Heading", font=F(9, "bold"),
                         background=COLORS["primary"], foreground="white")
        style.map("Treeview.Heading", background=[("active", COLORS["primary_dk"])])
        style.map("Treeview", background=[("selected", COLORS["primary"])],
                  foreground=[("selected", "white")])

        style.configure("Modern.Horizontal.TProgressbar",
                         troughcolor=COLORS["surface_alt"], background=COLORS["primary"],
                         bordercolor=COLORS["surface_alt"], lightcolor=COLORS["primary"],
                         darkcolor=COLORS["primary"], thickness=14)

        style.configure("TCombobox", font=F(10))
        style.configure("TEntry", font=F(10))

    # ── App shell: sidebar + content area ──────────────────────────────
    def _build_shell(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=232)
        self.sidebar.pack(side=tk.LEFT, fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=COLORS["sidebar"], height=90)
        brand.pack(fill="x")
        brand.pack_propagate(False)
        tk.Label(brand, text="🎓  ExamGenius", font=F(15, "bold"),
                 bg=COLORS["sidebar"], fg="white").pack(anchor="w", padx=18, pady=(20, 0))
        tk.Label(brand, text="AI", font=F(15, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["secondary"]).place(x=140, y=20)
        tk.Label(brand, text=APP_TAGLINE, font=F(7), bg=COLORS["sidebar"],
                 fg="#8993c9", wraplength=200, justify="left").pack(anchor="w", padx=18)

        tk.Frame(self.sidebar, bg=COLORS["sidebar_hi"], height=1).pack(fill="x", pady=8)

        self.nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("input",     "⚙️", "Configuration"),
            ("classroom", "🪑", "Visual Classroom"),
            ("faculty",   "👩‍🏫", "Faculty"),
            ("analytics", "📊", "Analytics"),
            ("insights",  "🧠", "AI Insights"),
            ("impact",    "🎯", "Educational Impact"),
            ("how_ai",    "🤖", "How AI Works"),
            ("search",    "🔎", "Global Search"),
            ("report",    "📄", "Report & Export"),
        ]
        self.nav_buttons = {}
        for key, icon, label in self.nav_items:
            btn = NavButton(self.sidebar, icon, label, command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        footer = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        footer.pack(side=tk.BOTTOM, fill="x", pady=14)
        tk.Label(footer, text=f"{APP_NAME} {APP_VERSION}", font=F(8), bg=COLORS["sidebar"],
                 fg="#697099").pack()
        tk.Label(footer, text="Powered by K-Means AI", font=F(7), bg=COLORS["sidebar"],
                 fg="#4b5389").pack()

        # Content area
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(side=tk.LEFT, fill="both", expand=True)

        topbar = tk.Frame(outer, bg=COLORS["surface"], height=56,
                           highlightbackground=COLORS["border"], highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.page_title_var = tk.StringVar(value="Dashboard")
        tk.Label(topbar, textvariable=self.page_title_var, font=F(14, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=20)

        self.ai_status_var = tk.StringVar(value="● AI Engine Idle")
        tk.Label(topbar, textvariable=self.ai_status_var, font=F(9, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side=tk.RIGHT, padx=20)

        self.container = tk.Frame(outer, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)

        # Build all pages (frames), stacked with tkraise for SPA-style nav
        self.pages = {}
        self._build_dashboard_page()
        self._build_input_page()
        self._build_classroom_page()
        self._build_faculty_page()
        self._build_analytics_page()
        self._build_insights_page()
        self._build_impact_page()
        self._build_how_ai_page()
        self._build_search_page()
        self._build_report_page()

        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_page(self, key):
        titles = {k: label for k, _, label in self.nav_items}
        self.page_title_var.set(titles.get(key, key.title()))
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)
        self.pages[key].tkraise()

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: DASHBOARD
    # ══════════════════════════════════════════════════════════════════
    def _build_dashboard_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["dashboard"] = page

        scroll = self._scrollable(page)

        hero = tk.Frame(scroll, bg=COLORS["primary"], height=118)
        hero.pack(fill="x", padx=24, pady=(20, 16))
        hero.pack_propagate(False)
        tk.Label(hero, text="Welcome to ExamGenius AI", font=F(20, "bold"),
                 bg=COLORS["primary"], fg="white").pack(anchor="w", padx=26, pady=(18, 2))
        tk.Label(hero, text="Automating examination management for schools & universities "
                             "with Artificial Intelligence — fair seating, balanced clusters, "
                             "and zero manual errors.",
                 font=F(10), bg=COLORS["primary"], fg="#dbe0ff",
                 wraplength=900, justify="left").pack(anchor="w", padx=26)

        # Stat cards
        stats_frame = tk.Frame(scroll, bg=COLORS["bg"])
        stats_frame.pack(fill="x", padx=24)
        self.stat_cards = {}
        stat_defs = [
            ("students",    "👥", "Total Students",   "0",    COLORS["primary"]),
            ("rooms",       "🏫", "Rooms",             "0",    COLORS["secondary"]),
            ("faculty",     "👩‍🏫", "Faculty",           "0",    COLORS["success"]),
            ("clusters",    "🧩", "AI Clusters",       "0",    COLORS["purple"]),
            ("utilization", "📈", "Utilization",       "0%",   COLORS["warning"]),
            ("ai_status",   "🤖", "AI Status",         "Idle", COLORS["danger"]),
        ]
        for i, (key, icon, label, default, color) in enumerate(stat_defs):
            card = StatCard(stats_frame, icon, label, default, color)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="w")
            self.stat_cards[key] = card

        # Pipeline progress card
        prog_card = Card(scroll, pad=18)
        prog_card.pack(fill="x", padx=24, pady=(12, 10))
        tk.Label(prog_card, text="Pipeline Progress", font=F(12, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", padx=18, pady=(14, 4))

        prog_row = tk.Frame(prog_card, bg=COLORS["surface"])
        prog_row.pack(fill="x", padx=18, pady=(0, 6))
        self.progress_bar = ttk.Progressbar(prog_row, style="Modern.Horizontal.TProgressbar",
                                             mode="determinate", maximum=6, length=600)
        self.progress_bar.pack(side=tk.LEFT, fill="x", expand=True)
        self.spinner_var = tk.StringVar(value="")
        tk.Label(prog_row, textvariable=self.spinner_var, font=F(12), bg=COLORS["surface"],
                 fg=COLORS["primary"], width=3).pack(side=tk.LEFT, padx=10)

        self.step_labels = {}
        steps_row = tk.Frame(prog_card, bg=COLORS["surface"])
        steps_row.pack(fill="x", padx=18, pady=(6, 14))
        step_names = ["Students", "Rooms", "Faculty", "K-Means", "Seating", "Allocation"]
        for i, name in enumerate(step_names):
            lbl = tk.Label(steps_row, text=f"○ {name}", font=F(9), bg=COLORS["surface"],
                            fg=COLORS["text_light"])
            lbl.grid(row=0, column=i, padx=10)
            self.step_labels[i] = lbl

        run_row = tk.Frame(scroll, bg=COLORS["bg"])
        run_row.pack(fill="x", padx=24, pady=(0, 10))
        RoundedButton(run_row, "Run AI Pipeline", command=self.run_pipeline,
                      bg=COLORS["success"], icon="▶", width=220, height=46).pack(side=tk.LEFT)
        tk.Label(run_row, text="Generates students, rooms & faculty, then runs K-Means "
                                "clustering to build seating & invigilation plans.",
                 font=F(9), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=14)

        # Recent activity log
        log_card = Card(scroll, pad=18)
        log_card.pack(fill="both", expand=True, padx=24, pady=(6, 24))
        tk.Label(log_card, text="Recent Activity", font=F(12, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=18, pady=(14, 4))
        self.status_text = tk.Text(log_card, height=13, font=("Consolas", 9), bg="#0f172a",
                                    fg="#a5f3fc", relief="flat", padx=12, pady=10)
        self.status_text.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    def _scrollable(self, parent):
        """Return a scrollable inner frame packed into parent."""
        canvas = tk.Canvas(parent, bg=COLORS["bg"], highlightthickness=0)
        vbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLORS["bg"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=1230)
        canvas.configure(yscrollcommand=vbar.set)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        vbar.pack(side=tk.RIGHT, fill="y")

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", lambda e: _wheel(e))
        return inner

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: CONFIGURATION (Input)
    # ══════════════════════════════════════════════════════════════════
    def _build_input_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["input"] = page
        scroll = self._scrollable(page)

        tk.Label(scroll, text="Exam Configuration", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(scroll, text="Configure student volume, domain distribution and room "
                              "capacity. ExamGenius AI will handle the rest.",
                 font=F(9), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(anchor="w", padx=24, pady=(0, 14))

        body = tk.Frame(scroll, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=24)

        # Left: parameters card
        cfg = Card(body, pad=18, width=430)
        cfg.pack(side=tk.LEFT, fill="y", padx=(0, 14))
        cfg.pack_propagate(False)

        tk.Label(cfg, text="Parameters", font=F(12, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 10))

        tk.Label(cfg, text="Total Students", bg=COLORS["surface"], font=F(9, "bold"),
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=18)
        self.student_count_var = tk.StringVar(value=str(DEFAULT_TOTAL_STUDENTS))
        tk.Entry(cfg, textvariable=self.student_count_var, font=F(11), relief="solid", bd=1,
                 highlightbackground=COLORS["border"]).pack(fill="x", padx=18, pady=(2, 2))
        tk.Label(cfg, text="↑ Changing total auto-redistributes domain counts", bg=COLORS["surface"],
                 font=F(8), fg=COLORS["text_light"]).pack(anchor="w", padx=18, pady=(0, 10))

        tk.Label(cfg, text="Domain Distribution", bg=COLORS["surface"], font=F(9, "bold"),
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=18)
        tk.Label(cfg, text="(edit freely — total syncs to their sum)", bg=COLORS["surface"],
                 font=F(8), fg=COLORS["text_light"]).pack(anchor="w", padx=18, pady=(0, 6))

        self.domain_vars = {}
        dom_frame = tk.Frame(cfg, bg=COLORS["surface"])
        dom_frame.pack(fill="x", padx=18)
        for i, domain in enumerate(DOMAINS):
            row = tk.Frame(dom_frame, bg=COLORS["surface"])
            row.pack(fill="x", pady=3)
            dot = tk.Label(row, text="●", fg=DOMAIN_COLORS[domain], bg=COLORS["surface"], font=F(10))
            dot.pack(side=tk.LEFT)
            tk.Label(row, text=domain, bg=COLORS["surface"], font=F(9),
                     fg=COLORS["text"]).pack(side=tk.LEFT, padx=6)
            var = tk.StringVar(value=str(DEFAULT_DOMAIN_COUNTS[domain]))
            self.domain_vars[domain] = var
            tk.Entry(row, textvariable=var, width=8, font=F(9), relief="solid", bd=1
                     ).pack(side=tk.RIGHT)

        self.sum_label_var = tk.StringVar(value=f"Domain sum: {DEFAULT_TOTAL_STUDENTS}  ✓")
        self.sum_label = tk.Label(cfg, textvariable=self.sum_label_var, bg=COLORS["surface"],
                                   font=F(9, "bold"), fg=COLORS["success"])
        self.sum_label.pack(anchor="w", padx=18, pady=(8, 10))

        tk.Label(cfg, text="Number of Rooms", bg=COLORS["surface"], font=F(9, "bold"),
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=18)
        self.room_count_var = tk.StringVar(value=str(DEFAULT_ROOM_COUNT))
        tk.Entry(cfg, textvariable=self.room_count_var, font=F(11), relief="solid", bd=1
                 ).pack(fill="x", padx=18, pady=(2, 16))

        RoundedButton(cfg, "Run AI Pipeline", command=self.run_pipeline, icon="▶",
                      bg=COLORS["success"], width=380, height=44).pack(padx=18, pady=(0, 18))

        self._attach_sync_traces()

        # Right: preview card
        prev = Card(body, pad=12)
        prev.pack(side=tk.LEFT, fill="both", expand=True)
        tk.Label(prev, text="Student Data Preview", font=F(12, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 6))

        tree_frame = tk.Frame(prev, bg=COLORS["surface"])
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.preview_tree = ttk.Treeview(tree_frame, height=18)
        sb2 = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=sb2.set)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.pack(fill="both", expand=True)

    def _attach_sync_traces(self):
        self._syncing = False
        self.student_count_var.trace_add("write", self._on_total_changed)
        for var in self.domain_vars.values():
            var.trace_add("write", self._on_domain_changed)

    def _on_total_changed(self, *_):
        if self._syncing:
            return
        try:
            new_total = int(self.student_count_var.get())
        except ValueError:
            return
        if new_total <= 0:
            return
        self._syncing = True
        try:
            raw = {}
            for d in DOMAINS:
                try:
                    raw[d] = max(1, int(self.domain_vars[d].get()))
                except ValueError:
                    raw[d] = DEFAULT_DOMAIN_COUNTS[d]
            raw_sum = sum(raw.values())
            new_counts = {d: round(raw[d] / raw_sum * new_total) for d in DOMAINS}
            diff = new_total - sum(new_counts.values())
            new_counts[DOMAINS[0]] += diff
            for d in DOMAINS:
                self.domain_vars[d].set(str(new_counts[d]))
            self._refresh_sum_label(new_total, new_total)
        finally:
            self._syncing = False

    def _on_domain_changed(self, *_):
        if self._syncing:
            return
        try:
            domain_sum = sum(int(self.domain_vars[d].get()) for d in DOMAINS)
        except ValueError:
            return
        self._syncing = True
        try:
            self.student_count_var.set(str(domain_sum))
            self._refresh_sum_label(domain_sum, domain_sum)
        finally:
            self._syncing = False

    def _refresh_sum_label(self, domain_sum, total):
        if domain_sum == total:
            self.sum_label_var.set(f"Domain sum: {domain_sum}  ✓")
            self.sum_label.config(fg=COLORS["success"])
        else:
            self.sum_label_var.set(f"Domain sum: {domain_sum}  ✗  (total = {total})")
            self.sum_label.config(fg=COLORS["danger"])

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: VISUAL CLASSROOM (Seating)
    # ══════════════════════════════════════════════════════════════════
    def _build_classroom_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["classroom"] = page

        top = tk.Frame(page, bg=COLORS["bg"])
        top.pack(fill="x", padx=24, pady=(18, 8))
        tk.Label(top, text="Visual Classroom", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(side=tk.LEFT)

        sel = tk.Frame(page, bg=COLORS["bg"])
        sel.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(sel, text="Room:", bg=COLORS["bg"], font=F(10)).pack(side=tk.LEFT)
        self.room_combo = ttk.Combobox(sel, width=10, font=F(10), state="readonly")
        self.room_combo.pack(side=tk.LEFT, padx=(6, 20))
        self.room_combo.bind("<<ComboboxSelected>>", self._on_room_select)

        tk.Label(sel, text="Shift:", bg=COLORS["bg"], font=F(10)).pack(side=tk.LEFT)
        self.shift_combo = ttk.Combobox(sel, width=6, font=F(10), state="readonly")
        self.shift_combo.pack(side=tk.LEFT, padx=(6, 20))
        self.shift_combo.bind("<<ComboboxSelected>>", self._on_room_select)

        tk.Label(sel, text="🟩 Occupied    ⬜ Empty    🟦 Selected", bg=COLORS["bg"],
                 font=F(9), fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=10)

        body = tk.Frame(page, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        grid_card = Card(body, pad=10)
        grid_card.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 14))
        tk.Label(grid_card, text="Seat Map", font=F(11, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 4))
        self.seat_canvas = tk.Canvas(grid_card, bg=COLORS["surface_alt"], highlightthickness=0)
        self.seat_canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        info_card = Card(body, pad=14, width=290)
        info_card.pack(side=tk.LEFT, fill="y")
        info_card.pack_propagate(False)
        tk.Label(info_card, text="Seat Details", font=F(11, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 10))

        self.seat_info_vars = {}
        for field in ["Student Name", "Roll Number", "Department", "Batch", "Cluster", "Seat"]:
            row = tk.Frame(info_card, bg=COLORS["surface"])
            row.pack(fill="x", padx=16, pady=6)
            tk.Label(row, text=field, font=F(8, "bold"), bg=COLORS["surface"],
                     fg=COLORS["text_light"]).pack(anchor="w")
            var = tk.StringVar(value="—")
            self.seat_info_vars[field] = var
            tk.Label(row, textvariable=var, font=F(11, "bold"), bg=COLORS["surface"],
                     fg=COLORS["text"]).pack(anchor="w")

        tk.Label(info_card, text="Click any seat in the grid to view student details.",
                 font=F(8), bg=COLORS["surface"], fg=COLORS["text_light"],
                 wraplength=250, justify="left").pack(anchor="w", padx=16, pady=(20, 0))

        # legacy table view (kept for completeness / accessibility)
        table_card = Card(page, pad=10)
        table_card.pack(fill="x", padx=24, pady=(0, 20))
        tk.Label(table_card, text="Table View", font=F(10, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=14, pady=(10, 4))
        tf = tk.Frame(table_card, bg=COLORS["surface"])
        tf.pack(fill="x", padx=14, pady=(0, 12))
        self.seating_tree = ttk.Treeview(tf, height=6)
        sb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.seating_tree.yview)
        self.seating_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.seating_tree.pack(fill="x", expand=True)

    def _draw_seat_grid(self, subset, capacity):
        canvas = self.seat_canvas
        canvas.delete("all")
        canvas.update_idletasks()
        cw = max(canvas.winfo_width(), 500)
        ch = max(canvas.winfo_height(), 360)

        cols = max(1, math.ceil(math.sqrt(capacity)))
        rows = max(1, math.ceil(capacity / cols))

        margin = 20
        cell_w = min(58, (cw - 2 * margin) / cols)
        cell_h = min(50, (ch - 2 * margin) / rows)
        cell = max(20, min(cell_w, cell_h))
        gap = 6

        occupied = {int(r["seat_number"]): r for _, r in subset.iterrows()}

        grid_w = cols * (cell + gap) - gap
        grid_h = rows * (cell + gap) - gap
        ox = max(margin, (cw - grid_w) / 2)
        oy = margin

        canvas.create_rectangle(ox - 14, oy - 22, ox + grid_w + 14, oy - 4,
                                 fill=COLORS["text"], outline="")
        canvas.create_text(ox + grid_w / 2, oy - 13, text="⟸  FRONT / INVIGILATOR DESK  ⟹",
                            fill="white", font=F(8, "bold"))

        seat_no = 1
        for r in range(rows):
            for c in range(cols):
                if seat_no > capacity:
                    break
                x1 = ox + c * (cell + gap)
                y1 = oy + 20 + r * (cell + gap)
                x2, y2 = x1 + cell, y1 + cell
                info = occupied.get(seat_no)
                color = DOMAIN_COLORS.get(info["domain"], COLORS["success"]) if info is not None else "#e2e8f0"
                rect = canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                                outline="white", width=2, tags=(f"seat{seat_no}",))
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(seat_no),
                                    fill="white" if info is not None else COLORS["text_light"],
                                    font=F(8, "bold"), tags=(f"seat{seat_no}",))
                canvas.tag_bind(f"seat{seat_no}", "<Button-1>",
                                 lambda e, sn=seat_no, i=info: self._on_seat_click(sn, i))
                seat_no += 1

    def _on_seat_click(self, seat_no, info):
        if info is None:
            for k in self.seat_info_vars:
                self.seat_info_vars[k].set("—")
            self.seat_info_vars["Seat"].set(str(seat_no))
            return
        self.seat_info_vars["Student Name"].set(f"Student {info['student_id']}")
        self.seat_info_vars["Roll Number"].set(str(info["student_id"]))
        self.seat_info_vars["Department"].set(str(info["domain"]))
        self.seat_info_vars["Batch"].set(str(info["batch"]))
        self.seat_info_vars["Cluster"].set(str(info["cluster"]))
        self.seat_info_vars["Seat"].set(str(seat_no))

    def _on_room_select(self, _event=None):
        room, shift = self.room_combo.get(), self.shift_combo.get()
        if room and shift:
            self._show_room_seating(room, shift)

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: FACULTY
    # ══════════════════════════════════════════════════════════════════
    def _build_faculty_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["faculty"] = page
        tk.Label(page, text="Faculty Allocation", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(18, 10))
        card = Card(page, pad=10)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        tf = tk.Frame(card, bg=COLORS["surface"])
        tf.pack(fill="both", expand=True, padx=14, pady=14)
        self.faculty_tree = ttk.Treeview(tf, height=22)
        sb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.faculty_tree.yview)
        self.faculty_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.faculty_tree.pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: ANALYTICS (Charts)
    # ══════════════════════════════════════════════════════════════════
    def _build_analytics_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["analytics"] = page
        tk.Label(page, text="Analytics", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(18, 10))

        cn = ttk.Notebook(page)
        cn.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.domain_chart_frame  = tk.Frame(cn, bg=COLORS["surface"])
        self.util_chart_frame    = tk.Frame(cn, bg=COLORS["surface"])
        self.cluster_chart_frame = tk.Frame(cn, bg=COLORS["surface"])
        self.batch_chart_frame   = tk.Frame(cn, bg=COLORS["surface"])
        self.workload_chart_frame = tk.Frame(cn, bg=COLORS["surface"])
        self.heatmap_chart_frame  = tk.Frame(cn, bg=COLORS["surface"])

        cn.add(self.domain_chart_frame,   text="  Students by Department  ")
        cn.add(self.batch_chart_frame,    text="  Students by Batch  ")
        cn.add(self.cluster_chart_frame,  text="  Cluster Distribution  ")
        cn.add(self.util_chart_frame,     text="  Room Utilization  ")
        cn.add(self.workload_chart_frame, text="  Faculty Workload  ")
        cn.add(self.heatmap_chart_frame,  text="  Occupancy Heatmap  ")

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: AI INSIGHTS
    # ══════════════════════════════════════════════════════════════════
    def _build_insights_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["insights"] = page
        scroll = self._scrollable(page)

        tk.Label(scroll, text="AI Insights", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(scroll, text="Automatically generated insights from the K-Means clustering "
                              "engine and the seating / faculty allocation results.",
                 font=F(9), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(anchor="w", padx=24, pady=(0, 14))

        conf_card = Card(scroll, pad=16)
        conf_card.pack(fill="x", padx=24, pady=(0, 14))
        row = tk.Frame(conf_card, bg=COLORS["surface"])
        row.pack(fill="x", padx=18, pady=16)
        tk.Label(row, text="🎯", font=F(26), bg=COLORS["surface"]).pack(side=tk.LEFT)
        col = tk.Frame(row, bg=COLORS["surface"])
        col.pack(side=tk.LEFT, padx=14)
        tk.Label(col, text="AI Confidence Score", font=F(10, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w")
        self.confidence_var = tk.StringVar(value="—")
        tk.Label(col, textvariable=self.confidence_var, font=F(22, "bold"), bg=COLORS["surface"],
                 fg=COLORS["success"]).pack(anchor="w")

        self.insight_grid = tk.Frame(scroll, bg=COLORS["bg"])
        self.insight_grid.pack(fill="x", padx=24)

        rec_card = Card(scroll, pad=16)
        rec_card.pack(fill="both", expand=True, padx=24, pady=(14, 24))
        tk.Label(rec_card, text="AI Recommendations", font=F(12, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", padx=18, pady=(14, 6))
        self.recommendations_text = tk.Text(rec_card, height=10, font=F(10), bg=COLORS["surface_alt"],
                                             relief="flat", padx=14, pady=12, wrap="word")
        self.recommendations_text.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: EDUCATIONAL IMPACT
    # ══════════════════════════════════════════════════════════════════
    def _build_impact_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["impact"] = page
        scroll = self._scrollable(page)

        tk.Label(scroll, text="Educational Impact", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(scroll, text="ExamGenius AI isn't just about seating students — it's about "
                              "helping educational institutions run fair, transparent, and "
                              "efficient examinations at scale.",
                 font=F(9), bg=COLORS["bg"], fg=COLORS["text_muted"], wraplength=1000,
                 justify="left").pack(anchor="w", padx=24, pady=(0, 14))

        grid = tk.Frame(scroll, bg=COLORS["bg"])
        grid.pack(fill="x", padx=24, pady=(0, 24))
        tiles = [
            ("⏱️", "Time Saved", "What used to take administrators days of manual "
             "spreadsheet work now takes seconds — freeing staff to focus on students.", COLORS["primary"]),
            ("⚖️", "Fair Seat Allocation", "K-Means clustering balances students across rooms "
             "objectively, removing human bias from the seating process.", COLORS["secondary"]),
            ("🛡️", "Reduced Exam Errors", "Automated capacity checks and shift management "
             "eliminate double-bookings and overcrowded rooms.", COLORS["danger"]),
            ("👩‍🏫", "Better Faculty Management", "Round-robin invigilator allocation keeps "
             "workload balanced across every faculty member.", COLORS["success"]),
            ("🔍", "Improved Transparency", "Every student can see exactly which room, seat "
             "and shift they are assigned to, reducing confusion on exam day.", COLORS["purple"]),
            ("🤝", "Reduced Manual Work", "One click replaces hours of spreadsheet juggling, "
             "letting exam cells scale to thousands of students effortlessly.", COLORS["warning"]),
            ("🧠", "AI-Assisted Decisions", "Data-driven insights help administrators spot "
             "issues — like an overcrowded room — before exam day.", COLORS["primary"]),
            ("🏫", "Built for Schools", "Scales down easily for smaller institutions with "
             "fewer students, rooms, and staff.", COLORS["secondary"]),
            ("🎓", "Built for Universities", "Handles thousands of students across multiple "
             "departments, batches and exam shifts with ease.", COLORS["success"]),
        ]
        for i, (icon, title, body, color) in enumerate(tiles):
            tile = InfoTile(grid, icon, title, body, color)
            tile.grid(row=i // 3, column=i % 3, padx=8, pady=8)

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: HOW AI WORKS
    # ══════════════════════════════════════════════════════════════════
    def _build_how_ai_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["how_ai"] = page
        scroll = self._scrollable(page)

        tk.Label(scroll, text="How AI Works", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(scroll, text="A simple visual walkthrough of the ExamGenius AI pipeline — "
                              "from raw student data to a finished, fair exam plan.",
                 font=F(9), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(anchor="w", padx=24, pady=(0, 14))

        card = Card(scroll, pad=20)
        card.pack(fill="x", padx=24, pady=(0, 24))
        self.pipeline_canvas = tk.Canvas(card, bg=COLORS["surface"], highlightthickness=0, height=560)
        self.pipeline_canvas.pack(fill="x", padx=20, pady=20)
        self.root.after(80, self._draw_pipeline_diagram)

    def _draw_pipeline_diagram(self):
        c = self.pipeline_canvas
        c.delete("all")
        c.update_idletasks()
        w = max(c.winfo_width(), 900)

        steps = [
            ("📋", "Student Data", "Batches, departments & IDs generated", COLORS["primary"]),
            ("🔢", "Encoding", "Categorical features (domain, batch) → numbers", COLORS["secondary"]),
            ("📏", "Feature Scaling", "StandardScaler normalizes feature ranges", COLORS["warning"]),
            ("🧩", "K-Means Clustering", "Groups students into balanced clusters", COLORS["purple"]),
            ("✅", "Optimized Groups", "Each cluster ≈ one exam room's worth of students", COLORS["success"]),
            ("🏫", "Room Allocation", "Clusters mapped to rooms respecting capacity", COLORS["primary"]),
            ("👩‍🏫", "Faculty Assignment", "Invigilators matched to domains present per room", COLORS["danger"]),
            ("📊", "Reports", "Charts, insights & exports generated automatically", COLORS["secondary"]),
        ]
        box_w, box_h = min(760, w - 80), 56
        x0 = (w - box_w) / 2
        y = 14
        gap = 14
        for icon, title, desc, color in steps:
            c.create_rectangle(x0, y, x0 + box_w, y + box_h, fill=color, outline="")
            c.create_text(x0 + 34, y + box_h / 2, text=icon, font=F(16), fill="white")
            c.create_text(x0 + 70, y + box_h / 2 - 9, text=title, font=F(11, "bold"),
                          fill="white", anchor="w")
            c.create_text(x0 + 70, y + box_h / 2 + 10, text=desc, font=F(8),
                          fill="#e8ebff", anchor="w")
            y += box_h + gap
            if title != "Reports":
                c.create_line(x0 + box_w / 2, y - gap, x0 + box_w / 2, y - 2,
                              fill=COLORS["text_light"], width=2, arrow=tk.LAST)
        c.configure(scrollregion=c.bbox("all"))

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: GLOBAL SEARCH
    # ══════════════════════════════════════════════════════════════════
    def _build_search_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["search"] = page

        tk.Label(page, text="Global Search", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(18, 8))

        bar = tk.Frame(page, bg=COLORS["bg"])
        bar.pack(fill="x", padx=24)
        self.search_var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=self.search_var, font=F(11), relief="solid", bd=1)
        entry.pack(side=tk.LEFT, fill="x", expand=True, ipady=6)
        entry.bind("<Return>", lambda e: self._run_search())
        RoundedButton(bar, "Search", command=self._run_search, icon="🔎",
                      width=140, height=36).pack(side=tk.LEFT, padx=10)
        tk.Label(page, text="Search by Roll Number, Student ID, Department, Faculty, Room, "
                             "or Seat Number.", font=F(8), bg=COLORS["bg"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=24, pady=(4, 10))

        card = Card(page, pad=10)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        tf = tk.Frame(card, bg=COLORS["surface"])
        tf.pack(fill="both", expand=True, padx=14, pady=14)
        cols = ["type", "id", "name_or_domain", "room", "shift", "extra"]
        self.search_tree = ttk.Treeview(tf, columns=cols, show="headings", height=20)
        heads = ["Type", "ID", "Name / Domain", "Room", "Shift", "Details"]
        widths = [90, 110, 220, 80, 70, 260]
        for col, h, w in zip(cols, heads, widths):
            self.search_tree.heading(col, text=h)
            self.search_tree.column(col, width=w)
        sb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.pack(fill="both", expand=True)

    def _run_search(self):
        query = self.search_var.get().strip().lower()
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        if not query or self.student_df is None:
            return

        results = []
        # Students / seating
        if self.seating_df is not None:
            mask = (
                self.seating_df["student_id"].astype(str).str.lower().str.contains(query) |
                self.seating_df["domain"].astype(str).str.lower().str.contains(query) |
                self.seating_df["room_assigned"].astype(str).str.lower().str.contains(query) |
                self.seating_df["seat_number"].astype(str).str.lower().str.contains(query)
            )
            for _, r in self.seating_df[mask].head(200).iterrows():
                results.append(("Student", r["student_id"], r["domain"], r["room_assigned"],
                                 r["exam_shift"], f"Batch {r['batch']} · Seat {r['seat_number']} · "
                                                   f"Cluster {r['cluster']}"))
        # Faculty
        if self.allocation_df is not None:
            mask = (
                self.allocation_df["room_id"].astype(str).str.lower().str.contains(query) |
                self.allocation_df["faculty_names"].astype(str).str.lower().str.contains(query) |
                self.allocation_df["dominant_domain"].astype(str).str.lower().str.contains(query)
            )
            for _, r in self.allocation_df[mask].head(200).iterrows():
                results.append(("Faculty", r["room_id"], r["faculty_names"], r["room_id"],
                                 "—", f"{r['students']} students · {r['dominant_domain']}"))
        # Rooms
        if self.room_df is not None:
            mask = self.room_df["room_id"].astype(str).str.lower().str.contains(query)
            for _, r in self.room_df[mask].head(200).iterrows():
                results.append(("Room", r["room_id"], "—", r["room_id"], "—",
                                 f"Capacity {r['capacity']}"))

        for row in results[:400]:
            self.search_tree.insert("", "end", values=row)

    # ══════════════════════════════════════════════════════════════════
    #  PAGE: REPORT & EXPORT
    # ══════════════════════════════════════════════════════════════════
    def _build_report_page(self):
        page = tk.Frame(self.container, bg=COLORS["bg"])
        self.pages["report"] = page

        tk.Label(page, text="Report & Export", font=F(16, "bold"), bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=24, pady=(18, 10))

        card = Card(page, pad=10)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        self.report_text = tk.Text(card, font=("Consolas", 9), relief="flat", padx=16, pady=14)
        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.pack(fill="both", expand=True, padx=(14, 0), pady=14)

        btns = tk.Frame(page, bg=COLORS["bg"])
        btns.pack(fill="x", padx=24, pady=(0, 20))
        RoundedButton(btns, "Save Report (.txt)", command=self._save_report,
                      bg=COLORS["secondary"], icon="📄", width=200, height=42).pack(side=tk.LEFT, padx=(0, 10))
        RoundedButton(btns, "Export PDF Report", command=self._export_pdf,
                      bg=COLORS["danger"], icon="🧾", width=200, height=42).pack(side=tk.LEFT, padx=10)
        RoundedButton(btns, "Export to Excel", command=self._export_excel,
                      bg=COLORS["success"], icon="📊", width=200, height=42).pack(side=tk.LEFT, padx=10)
        RoundedButton(btns, "Export to CSV", command=self._export_csv,
                      bg=COLORS["primary"], icon="🗂️", width=200, height=42).pack(side=tk.LEFT, padx=10)

    # ══════════════════════════════════════════════════════════════════
    #  LOGGING
    # ══════════════════════════════════════════════════════════════════
    def _log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.status_text.insert(tk.END, line + "\n")
        self.status_text.see(tk.END)
        self.activity_log.append(line)
        self.root.update()

    def _mark_step(self, index, done=True):
        lbl = self.step_labels[index]
        if done:
            lbl.config(text=f"✓ {lbl.cget('text').split(' ', 1)[1]}", fg=COLORS["success"])
        self.progress_bar["value"] = index + 1
        self.root.update()

    # ══════════════════════════════════════════════════════════════════
    #  STEP 1 — STUDENT DATA GENERATION  (core logic preserved)
    # ══════════════════════════════════════════════════════════════════
    def _generate_student_data(self):
        self._log("Step 1 ▶ Generating student data (batches 19-23) ...")
        domain_counts = {}
        for d in DOMAINS:
            try:
                domain_counts[d] = max(0, int(self.domain_vars[d].get()))
            except ValueError:
                domain_counts[d] = DEFAULT_DOMAIN_COUNTS[d]

        total = sum(domain_counts.values())
        if total == 0:
            raise ValueError("Total students cannot be 0. Please enter valid domain counts.")

        students = []
        sid = 1
        for domain in DOMAINS:
            count = domain_counts[domain]
            per_batch = count // len(BATCHES)
            remainder = count % len(BATCHES)
            for b_idx, batch in enumerate(BATCHES):
                batch_count = per_batch + (1 if b_idx < remainder else 0)
                for _ in range(batch_count):
                    students.append({
                        "student_id": f"{batch}F{sid:04d}",
                        "batch":      batch,
                        "domain":     domain,
                    })
                    sid += 1

        self.student_df = pd.DataFrame(students)
        breakdown = " | ".join(f"{d[:4]}:{domain_counts[d]}" for d in DOMAINS)
        self._log(f"  ✓ {len(self.student_df)} students across {len(BATCHES)} batches")
        self._log(f"  Domain breakdown → {breakdown}")
        return self.student_df

    # ══════════════════════════════════════════════════════════════════
    #  STEP 2 — ROOM DATA GENERATION (core logic preserved)
    # ══════════════════════════════════════════════════════════════════
    def _generate_room_data(self):
        self._log("Step 2 ▶ Generating room data ...")
        n = int(self.room_count_var.get())
        room_ids = [f"R{i+1:02d}" for i in range(n)]
        caps = ([25] * 4 + [30] * 14 + [32] * 8 + [35] * 4)
        caps = caps[:n]
        np.random.seed(42)
        np.random.shuffle(caps)
        self.room_df = pd.DataFrame({"room_id": room_ids, "capacity": caps})
        self._log(f"  ✓ {n} rooms | Total capacity: {self.room_df['capacity'].sum()} seats")
        return self.room_df

    # ══════════════════════════════════════════════════════════════════
    #  STEP 3 — FACULTY DATA GENERATION (core logic preserved)
    # ══════════════════════════════════════════════════════════════════
    def _generate_faculty_data(self):
        self._log("Step 3 ▶ Generating faculty data ...")
        records = []
        fid = 1
        for domain in DOMAINS:
            for name in FACULTY_NAMES[domain]:
                records.append({
                    "faculty_id":   f"FAC{fid:03d}",
                    "faculty_name": name,
                    "domain":       domain,
                    "available":    True,
                })
                fid += 1
        self.faculty_df = pd.DataFrame(records)
        self._log(f"  ✓ {len(self.faculty_df)} faculty members across {len(DOMAINS)} domains")
        return self.faculty_df

    # ══════════════════════════════════════════════════════════════════
    #  STEP 4 — K-MEANS CLUSTERING  (the core AI algorithm — preserved)
    # ══════════════════════════════════════════════════════════════════
    def _run_clustering(self):
        self._log("Step 4 ▶ Running K-Means clustering (domain + batch features) ...")

        domain_enc = LabelEncoder().fit_transform(self.student_df["domain"])
        batch_enc  = LabelEncoder().fit_transform(self.student_df["batch"])
        X = np.column_stack([domain_enc, batch_enc])

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        optimal_k = min(len(self.room_df), max(1, len(self.student_df) // 25))
        self._log(f"  Using k = {optimal_k} clusters")

        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20, max_iter=500)
        self.student_df["cluster"] = kmeans.fit_predict(X_scaled)

        counts = self.student_df["cluster"].value_counts()
        self._log(f"  ✓ Clusters: min={counts.min()} max={counts.max()} mean={counts.mean():.1f}")
        self.stat_cards["clusters"].set(str(optimal_k))
        return optimal_k

    # ══════════════════════════════════════════════════════════════════
    #  STEP 5 — SEATING ALLOCATION (core logic preserved)
    # ══════════════════════════════════════════════════════════════════
    def _generate_seating_plan(self):
        self._log("Step 5 ▶ Generating seating plan ...")

        total_capacity = self.room_df["capacity"].sum()
        rooms = self.room_df.set_index("room_id")["capacity"].to_dict()
        room_list = list(rooms.keys())

        ordered = self.student_df.sort_values(["cluster", "domain", "batch"]).reset_index(drop=True)

        assignments = []
        shift = 1
        seat_used = {r: 0 for r in room_list}
        room_idx = 0

        for _, student in ordered.iterrows():
            while room_idx < len(room_list) and seat_used[room_list[room_idx]] >= rooms[room_list[room_idx]]:
                room_idx += 1
            if room_idx >= len(room_list):
                shift += 1
                seat_used = {r: 0 for r in room_list}
                room_idx = 0
            room_id = room_list[room_idx]
            seat_used[room_id] += 1
            assignments.append({
                **student.to_dict(),
                "room_assigned": room_id,
                "exam_shift":    shift,
                "seat_number":   seat_used[room_id],
            })

        self.seating_df = pd.DataFrame(assignments)
        rooms_used = self.seating_df["room_assigned"].nunique()
        shifts = self.seating_df["exam_shift"].nunique()
        util = len(self.seating_df) / (total_capacity * shifts) * 100

        self._log(f"  ✓ Seated: {len(self.seating_df)} | Shifts: {shifts} | "
                  f"Rooms used per shift: {rooms_used}")

        self.stat_cards["students"].set(str(len(self.student_df)))
        self.stat_cards["rooms"].set(f"{rooms_used}/{len(self.room_df)}")
        self.stat_cards["utilization"].set(f"{util:.1f}%")
        return self.seating_df

    # ══════════════════════════════════════════════════════════════════
    #  STEP 6 — FACULTY ALLOCATION (core logic preserved)
    # ══════════════════════════════════════════════════════════════════
    def _allocate_faculty(self):
        self._log("Step 6 ▶ Allocating faculty to rooms ...")

        faculty_pool = {
            d: list(self.faculty_df[self.faculty_df["domain"] == d]["faculty_name"])
            for d in DOMAINS
        }
        pool_idx = {d: 0 for d in DOMAINS}

        def pick_faculty(domain):
            pool = faculty_pool[domain]
            name = pool[pool_idx[domain] % len(pool)]
            pool_idx[domain] += 1
            return name

        allocations = []
        shift_1 = self.seating_df[self.seating_df["exam_shift"] == 1]

        for room_id in sorted(shift_1["room_assigned"].unique()):
            room_students = shift_1[shift_1["room_assigned"] == room_id]
            domains_present = room_students["domain"].unique().tolist()
            dominant_domain = room_students["domain"].value_counts().index[0]
            assigned_faculty = [pick_faculty(d) for d in domains_present]
            allocations.append({
                "room_id":         room_id,
                "students":        len(room_students),
                "dominant_domain": dominant_domain,
                "domains_present": ", ".join(domains_present),
                "faculty_names":   "; ".join(assigned_faculty),
            })

        self.allocation_df = pd.DataFrame(allocations)
        self._log(f"  ✓ Faculty deployed across {len(self.allocation_df)} rooms")
        self.stat_cards["faculty"].set(str(len(self.faculty_df)))
        return self.allocation_df

    # ══════════════════════════════════════════════════════════════════
    #  AI INSIGHTS COMPUTATION  (new)
    # ══════════════════════════════════════════════════════════════════
    def _compute_insights(self):
        s1 = self.seating_df[self.seating_df["exam_shift"] == 1]
        room_cap = dict(zip(self.room_df["room_id"], self.room_df["capacity"]))
        room_usage = s1["room_assigned"].value_counts()
        util_by_room = {r: room_usage.get(r, 0) / room_cap[r] * 100 for r in room_cap}

        most_crowded = max(util_by_room, key=util_by_room.get)
        avg_util = sum(util_by_room.values()) / len(util_by_room)

        cluster_counts = self.student_df["cluster"].value_counts()
        largest_cluster = cluster_counts.idxmax()
        smallest_cluster = cluster_counts.idxmin()

        dept_counts = self.student_df["domain"].value_counts().to_dict()

        faculty_workload = {}
        for names in self.allocation_df["faculty_names"]:
            for n in names.split("; "):
                faculty_workload[n] = faculty_workload.get(n, 0) + 1
        busiest_faculty = max(faculty_workload, key=faculty_workload.get) if faculty_workload else "—"

        shifts = self.seating_df["exam_shift"].nunique()
        seat_opt_pct = len(self.seating_df) / (self.room_df["capacity"].sum() * shifts) * 100

        balance_spread = (cluster_counts.max() - cluster_counts.min()) / max(1, cluster_counts.mean())
        confidence = max(60.0, min(99.0, 97 - balance_spread * 25))

        self.insights = {
            "most_crowded_room": most_crowded,
            "most_crowded_util": util_by_room[most_crowded],
            "avg_util": avg_util,
            "largest_cluster": (largest_cluster, int(cluster_counts.max())),
            "smallest_cluster": (smallest_cluster, int(cluster_counts.min())),
            "dept_counts": dept_counts,
            "busiest_faculty": (busiest_faculty, faculty_workload.get(busiest_faculty, 0)),
            "shifts": shifts,
            "seat_opt_pct": seat_opt_pct,
            "confidence": confidence,
        }
        return self.insights

    # ══════════════════════════════════════════════════════════════════
    #  UI UPDATE METHODS
    # ══════════════════════════════════════════════════════════════════
    def _update_preview(self):
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        if self.student_df is None:
            return
        cols = ["student_id", "batch", "domain", "cluster"]
        self.preview_tree["columns"] = cols
        self.preview_tree["show"] = "headings"
        widths = [130, 60, 200, 70]
        for col, w in zip(cols, widths):
            self.preview_tree.heading(col, text=col.replace("_", " ").title())
            self.preview_tree.column(col, width=w)
        for _, row in self.student_df.head(60).iterrows():
            self.preview_tree.insert("", "end", values=(
                row["student_id"], row["batch"], row["domain"], row["cluster"]))

    def _update_seating_tab(self):
        if self.seating_df is None:
            return
        rooms = sorted(self.seating_df["room_assigned"].unique())
        shifts = sorted(self.seating_df["exam_shift"].unique())
        self.room_combo["values"] = rooms
        self.shift_combo["values"] = shifts
        self.room_combo.set(rooms[0])
        self.shift_combo.set(shifts[0])
        self._show_room_seating(rooms[0], shifts[0])

    def _show_room_seating(self, room_id, shift):
        subset = self.seating_df[
            (self.seating_df["room_assigned"] == room_id) &
            (self.seating_df["exam_shift"] == int(shift))
        ]
        capacity = int(self.room_df.set_index("room_id").loc[room_id, "capacity"])
        self._draw_seat_grid(subset, capacity)
        for k in self.seat_info_vars:
            self.seat_info_vars[k].set("—")

        for item in self.seating_tree.get_children():
            self.seating_tree.delete(item)
        cols = ["seat_number", "student_id", "batch", "domain", "cluster"]
        heads = ["Seat", "Roll No.", "Batch", "Domain", "Cluster"]
        widths = [60, 120, 60, 200, 70]
        self.seating_tree["columns"] = cols
        self.seating_tree["show"] = "headings"
        for col, h, w in zip(cols, heads, widths):
            self.seating_tree.heading(col, text=h)
            self.seating_tree.column(col, width=w)
        for _, row in subset.iterrows():
            self.seating_tree.insert("", "end", values=(
                row["seat_number"], row["student_id"], row["batch"], row["domain"], row["cluster"]))

    def _update_faculty_view(self):
        for item in self.faculty_tree.get_children():
            self.faculty_tree.delete(item)
        if self.allocation_df is None:
            return
        cols = ["room_id", "students", "dominant_domain", "domains_present", "faculty_names"]
        heads = ["Room", "Students", "Main Domain", "Domains Present", "Invigilators"]
        widths = [70, 80, 160, 260, 320]
        self.faculty_tree["columns"] = cols
        self.faculty_tree["show"] = "headings"
        for col, h, w in zip(cols, heads, widths):
            self.faculty_tree.heading(col, text=h)
            self.faculty_tree.column(col, width=w)
        for _, row in self.allocation_df.iterrows():
            self.faculty_tree.insert("", "end", values=(
                row["room_id"], row["students"], row["dominant_domain"],
                row["domains_present"], row["faculty_names"]))

    @staticmethod
    def _clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _mount_fig(self, frame, fig):
        self._clear_frame(frame)
        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(fill="both", expand=True)

    def _update_charts(self):
        if self.student_df is None:
            return
        palette = list(DOMAIN_COLORS.values())

        # Students by Department
        fig1, ax1 = plt.subplots(figsize=(7, 4.2))
        dc = self.student_df["domain"].value_counts()
        ax1.pie(dc.values, labels=dc.index, autopct="%1.1f%%",
                colors=[DOMAIN_COLORS[d] for d in dc.index], startangle=90)
        ax1.set_title("Students by Department")
        fig1.tight_layout()
        self._mount_fig(self.domain_chart_frame, fig1)

        # Students by Batch
        fig4, ax4 = plt.subplots(figsize=(7, 4.2))
        bc = self.student_df["batch"].value_counts().sort_index()
        ax4.bar([str(b) for b in bc.index], bc.values, color=palette, edgecolor="white")
        ax4.set_xlabel("Batch"); ax4.set_ylabel("Students")
        ax4.set_title("Student Count per Batch (19-23)")
        fig4.tight_layout()
        self._mount_fig(self.batch_chart_frame, fig4)

        # Cluster Distribution
        fig3, ax3 = plt.subplots(figsize=(7, 4.2))
        cc = self.student_df["cluster"].value_counts().sort_index()
        ax3.bar(cc.index, cc.values, color=COLORS["primary"], alpha=0.85, edgecolor="white")
        ax3.set_xlabel("Cluster ID"); ax3.set_ylabel("Students")
        ax3.set_title("K-Means Cluster Sizes")
        fig3.tight_layout()
        self._mount_fig(self.cluster_chart_frame, fig3)

        if self.seating_df is not None:
            # Room Utilization
            fig2, ax2 = plt.subplots(figsize=(7, 4.2))
            s1 = self.seating_df[self.seating_df["exam_shift"] == 1]
            room_usage = s1["room_assigned"].value_counts()
            room_cap = dict(zip(self.room_df["room_id"], self.room_df["capacity"]))
            rooms_sorted = sorted(room_cap.keys())
            utils = [room_usage.get(r, 0) / room_cap[r] * 100 for r in rooms_sorted]
            ax2.bar(rooms_sorted, utils, color=COLORS["success"], alpha=0.85, edgecolor="white")
            ax2.axhline(100, color=COLORS["danger"], linestyle="--", linewidth=1, label="Full capacity")
            ax2.set_xlabel("Room"); ax2.set_ylabel("Utilization (%)")
            ax2.set_title("Room Utilization (Shift 1)")
            ax2.tick_params(axis="x", rotation=60)
            ax2.legend()
            fig2.tight_layout()
            self._mount_fig(self.util_chart_frame, fig2)

            # Faculty Workload
            if self.allocation_df is not None:
                workload = {}
                for names in self.allocation_df["faculty_names"]:
                    for n in names.split("; "):
                        workload[n] = workload.get(n, 0) + 1
                fig5, ax5 = plt.subplots(figsize=(7, 4.4))
                names = list(workload.keys())
                vals = list(workload.values())
                ax5.barh(names, vals, color=COLORS["purple"], alpha=0.85, edgecolor="white")
                ax5.set_xlabel("Rooms Assigned")
                ax5.set_title("Faculty Workload")
                fig5.tight_layout()
                self._mount_fig(self.workload_chart_frame, fig5)

            # Occupancy Heatmap (rooms x shifts)
            fig6, ax6 = plt.subplots(figsize=(7.5, 4.4))
            pivot = self.seating_df.pivot_table(index="room_assigned", columns="exam_shift",
                                                 values="student_id", aggfunc="count", fill_value=0)
            im = ax6.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
            ax6.set_xticks(range(len(pivot.columns)))
            ax6.set_xticklabels([f"Shift {c}" for c in pivot.columns])
            ax6.set_yticks(range(len(pivot.index)))
            ax6.set_yticklabels(pivot.index, fontsize=6)
            ax6.set_title("Room Occupancy Heatmap")
            fig6.colorbar(im, ax=ax6, label="Students Seated")
            fig6.tight_layout()
            self._mount_fig(self.heatmap_chart_frame, fig6)

    def _update_insights_page(self):
        if not self.insights:
            return
        ins = self.insights
        self.confidence_var.set(f"{ins['confidence']:.1f}%")

        self._clear_frame(self.insight_grid)
        tiles = [
            ("🏫", "Most Crowded Room", f"{ins['most_crowded_room']} is running at "
             f"{ins['most_crowded_util']:.1f}% utilization.", COLORS["danger"]),
            ("📈", "Average Utilization", f"Rooms are averaging {ins['avg_util']:.1f}% "
             "capacity utilization across shift 1.", COLORS["primary"]),
            ("🧩", "Largest Cluster", f"Cluster {ins['largest_cluster'][0]} has "
             f"{ins['largest_cluster'][1]} students — the biggest AI-formed group.", COLORS["purple"]),
            ("🔹", "Smallest Cluster", f"Cluster {ins['smallest_cluster'][0]} has "
             f"{ins['smallest_cluster'][1]} students — the smallest AI-formed group.", COLORS["secondary"]),
            ("👩‍🏫", "Busiest Faculty", f"{ins['busiest_faculty'][0]} is assigned to "
             f"{ins['busiest_faculty'][1]} rooms — the highest invigilation load.", COLORS["warning"]),
            ("🔁", "Exam Shifts Required", f"{ins['shifts']} shift(s) needed to seat all "
             "students given current room capacity.", COLORS["success"]),
        ]
        for i, (icon, title, body, color) in enumerate(tiles):
            tile = InfoTile(self.insight_grid, icon, title, body, color)
            tile.grid(row=i // 3, column=i % 3, padx=8, pady=8)

        recs = []
        if ins["most_crowded_util"] >= 98:
            recs.append(f"⚠ AI recommends opening one more room — {ins['most_crowded_room']} "
                        "is at or near full capacity.")
        if ins["avg_util"] < 70:
            recs.append("ℹ Average room utilization is under 70% — consider reducing the "
                        "room count to cut operating costs.")
        recs.append("✓ K-Means successfully balanced student groups across clusters "
                    f"(confidence {ins['confidence']:.1f}%).")
        recs.append(f"✓ Seat optimization stands at {ins['seat_opt_pct']:.1f}% of total "
                    "available capacity being used.")
        dept_line = ", ".join(f"{d}: {c}" for d, c in ins["dept_counts"].items())
        recs.append(f"ℹ Department distribution — {dept_line}.")
        recs.append(f"✓ Faculty allocation covered all rooms with a round-robin policy "
                    f"to prevent overload (busiest: {ins['busiest_faculty'][0]}).")

        self.recommendations_text.delete(1.0, tk.END)
        self.recommendations_text.insert(1.0, "\n\n".join(recs))

    # ══════════════════════════════════════════════════════════════════
    #  REPORT GENERATION
    # ══════════════════════════════════════════════════════════════════
    def _update_report(self):
        if self.student_df is None:
            return
        total_cap = self.room_df["capacity"].sum()
        shifts = self.seating_df["exam_shift"].nunique()
        seated_s1 = len(self.seating_df[self.seating_df["exam_shift"] == 1])
        util = seated_s1 / total_cap * 100
        ins = self.insights

        report = f"""
{'='*70}
   {APP_NAME.upper()} — FINAL EXAMINATION REPORT
   {APP_TAGLINE}
{'='*70}
   Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

   STUDENT STATISTICS
   {'-'*60}
   Total Students Enrolled   : {len(self.student_df)}
   Batches                   : {sorted(self.student_df['batch'].unique())}

   Domain Breakdown:
{self.student_df['domain'].value_counts().to_string()}

   Batch Breakdown:
{self.student_df['batch'].value_counts().sort_index().to_string()}

   AI CLUSTERING (K-MEANS) STATISTICS
   {'-'*60}
   Feature Set               : Domain + Batch (encoded & scaled)
   Clusters Used (k)         : {self.student_df['cluster'].nunique()}
   Min Cluster Size          : {self.student_df['cluster'].value_counts().min()}
   Max Cluster Size          : {self.student_df['cluster'].value_counts().max()}
   Mean Cluster Size         : {self.student_df['cluster'].value_counts().mean():.1f}
   AI Confidence Score       : {ins.get('confidence', 0):.1f}%

   SEATING STATISTICS
   {'-'*60}
   Total Rooms Available     : {len(self.room_df)}
   Total Seat Capacity       : {total_cap}
   Students Seated (Shift 1) : {seated_s1}
   Exam Shifts Required      : {shifts}
   Room Utilization (Shift 1): {util:.1f}%
   Most Crowded Room         : {ins.get('most_crowded_room', '—')}
   Capacity Range            : {self.room_df['capacity'].min()} - {self.room_df['capacity'].max()} seats

   FACULTY STATISTICS
   {'-'*60}
   Total Faculty Available   : {len(self.faculty_df)}
   Faculty Deployed          : {len(self.allocation_df)}
   Domains Covered           : {len(DOMAINS)}
   Busiest Faculty           : {ins.get('busiest_faculty', ('—', 0))[0]}
   (Each room assigned faculty matching all domains present)

{'='*70}
   PIPELINE COMPLETE — ExamGenius AI has generated a fair, optimized,
   AI-driven examination plan.
{'='*70}
"""
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    # ══════════════════════════════════════════════════════════════════
    #  EXPORTS
    # ══════════════════════════════════════════════════════════════════
    def _save_report(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the AI pipeline first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt")],
                                           initialfile="examgenius_report.txt")
        if fn:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self.report_text.get(1.0, tk.END))
            messagebox.showinfo("Saved", f"Report saved to:\n{fn}")

    def _export_excel(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the AI pipeline first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                           filetypes=[("Excel files", "*.xlsx")],
                                           initialfile="examgenius_data.xlsx")
        if fn:
            with pd.ExcelWriter(fn, engine="openpyxl") as writer:
                self.student_df.to_excel(writer, sheet_name="Students", index=False)
                self.seating_df.to_excel(writer, sheet_name="Seating", index=False)
                self.allocation_df.to_excel(writer, sheet_name="Faculty", index=False)
                self.room_df.to_excel(writer, sheet_name="Rooms", index=False)
            messagebox.showinfo("Exported", f"Data exported to:\n{fn}")

    def _export_csv(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the AI pipeline first.")
            return
        folder = filedialog.askdirectory(title="Choose folder for CSV export")
        if not folder:
            return
        self.student_df.to_csv(os.path.join(folder, "students.csv"), index=False)
        self.seating_df.to_csv(os.path.join(folder, "seating.csv"), index=False)
        self.allocation_df.to_csv(os.path.join(folder, "faculty_allocation.csv"), index=False)
        self.room_df.to_csv(os.path.join(folder, "rooms.csv"), index=False)
        messagebox.showinfo("Exported", f"CSV files saved to:\n{folder}")

    def _export_pdf(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the AI pipeline first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".pdf",
                                           filetypes=[("PDF files", "*.pdf")],
                                           initialfile="examgenius_report.pdf")
        if not fn:
            return
        with PdfPages(fn) as pdf:
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.5, 0.96, APP_NAME, ha="center", fontsize=20, weight="bold")
            fig.text(0.5, 0.935, APP_TAGLINE, ha="center", fontsize=9, color="#555")
            report_body = self.report_text.get(1.0, tk.END)
            fig.text(0.06, 0.90, report_body, fontsize=6.5, family="monospace", va="top")
            pdf.savefig(fig)
            plt.close(fig)
        messagebox.showinfo("Exported", f"PDF report saved to:\n{fn}")

    # ══════════════════════════════════════════════════════════════════
    #  MAIN PIPELINE
    # ══════════════════════════════════════════════════════════════════
    def run_pipeline(self):
        if self.pipeline_running:
            return
        self.pipeline_running = True
        self.show_page("dashboard")
        self.ai_status_var.set("● AI Engine Running…")
        self.progress_bar["value"] = 0
        for lbl in self.step_labels.values():
            name = lbl.cget("text").split(" ", 1)[1]
            lbl.config(text=f"○ {name}", fg=COLORS["text_light"])
        self.stat_cards["ai_status"].set("Running")

        self._log("\n" + "=" * 55)
        self._log(f"STARTING {APP_NAME.upper()} PIPELINE")
        self._log("=" * 55)

        self._spin_active = True
        self._spin_frames = ["◐", "◓", "◑", "◒"]
        self._spin_i = 0
        self._animate_spinner()

        def _thread():
            try:
                self._generate_student_data()
                self.root.after(0, lambda: self._mark_step(0))
                self._generate_room_data()
                self.root.after(0, lambda: self._mark_step(1))
                self._generate_faculty_data()
                self.root.after(0, lambda: self._mark_step(2))
                self._run_clustering()
                self.root.after(0, lambda: self._mark_step(3))
                self._generate_seating_plan()
                self.root.after(0, lambda: self._mark_step(4))
                self._allocate_faculty()
                self.root.after(0, lambda: self._mark_step(5))
                self._compute_insights()

                self.root.after(0, self._update_preview)
                self.root.after(0, self._update_seating_tab)
                self.root.after(0, self._update_faculty_view)
                self.root.after(0, self._update_charts)
                self.root.after(0, self._update_insights_page)
                self.root.after(0, self._update_report)

                self._log("\n" + "=" * 55)
                self._log("✓  PIPELINE COMPLETE — All outputs generated")
                self._log("=" * 55 + "\n")

                self.root.after(0, lambda: self.ai_status_var.set("● AI Engine Ready"))
                self.root.after(0, lambda: self.stat_cards["ai_status"].set("Ready"))
                self.root.after(0, self._stop_spinner)
                self.pipeline_running = False
                self.root.after(0, lambda: messagebox.showinfo(
                    "Pipeline Complete", "ExamGenius AI pipeline completed successfully!"))
            except Exception as exc:
                self.pipeline_running = False
                self.root.after(0, self._stop_spinner)
                self.root.after(0, lambda: self.ai_status_var.set("● AI Engine Error"))
                self._log(f"ERROR: {exc}")
                self.root.after(0, lambda: messagebox.showerror("Pipeline Error", str(exc)))

        Thread(target=_thread, daemon=True).start()

    def _animate_spinner(self):
        if not getattr(self, "_spin_active", False):
            self.spinner_var.set("")
            return
        self.spinner_var.set(self._spin_frames[self._spin_i % len(self._spin_frames)])
        self._spin_i += 1
        self.root.after(150, self._animate_spinner)

    def _stop_spinner(self):
        self._spin_active = False
        self.spinner_var.set("✓")


def main():
    root = tk.Tk()
    ExamGeniusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
