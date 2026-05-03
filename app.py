import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
import datetime

warnings.filterwarnings("ignore")

if not os.path.exists("outputs"):
    os.makedirs("outputs")

# ── Constants matching the problem statement ─────────────────────────────────
DOMAINS = [
    "Computer Science",
    "Artificial Intelligence",
    "Business Analytics",
    "Software Engineering",
    "Electrical Engineering",
]
BATCHES = [19, 20, 21, 22, 23]          # batches 19-23 as per requirement
DEFAULT_TOTAL_STUDENTS = 2450           # 2400-2500 range
DEFAULT_ROOM_COUNT = 30

# Approximate per-domain student counts (sum ≈ 2450)
DEFAULT_DOMAIN_COUNTS = {
    "Computer Science": 550,
    "Artificial Intelligence": 500,
    "Business Analytics": 400,
    "Software Engineering": 450,
    "Electrical Engineering": 550,
}

FACULTY_NAMES = {
    "Computer Science":       ["Dr. Fayyaz Ahmed",  "Prof. Alisha Tariq", "Dr. Hashim Raza"],
    "Artificial Intelligence":["Dr. Zainab Ahmed",  "Prof. Kamran Iqbal", "Dr. Farrukh Shah", "Prof. Malik Saeed"],
    "Business Analytics":     ["Dr. Rehan Qureshi", "Prof. Ayesha Awan",  "Dr. Tahir Hussain"],
    "Software Engineering":   ["Dr. Ali Hassan",    "Prof. Saba Naseem",  "Dr. Usman Tariq"],
    "Electrical Engineering": ["Dr. Tariq Mehmood", "Prof. Sadia Kiran",  "Dr. Kashif Anwar"],
}


class ExamManagementSystem:
    """Automated Exam Management System using K-Means Clustering."""

    def __init__(self, root):
        self.root = root
        self.root.title("Exam Management System – NUCES Faisalabad")
        self.root.geometry("1400x820")
        self.root.configure(bg="#f0f4f8")

        # DataFrames
        self.student_df   = None
        self.room_df      = None
        self.faculty_df   = None
        self.seating_df   = None
        self.allocation_df = None

        self.colors = {
            "primary": "#1a2e44",
            "success": "#27ae60",
            "info":    "#2980b9",
            "warn":    "#e67e22",
            "danger":  "#c0392b",
            "purple":  "#8e44ad",
            "teal":    "#16a085",
        }

        self._setup_ui()

    # ── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tabs = {
            "dashboard": "Dashboard",
            "input":     "Input",
            "seating":   "Seating Plan",
            "faculty":   "Faculty",
            "charts":    "Charts",
            "report":    "Report",
        }
        self.frames = {}
        for key, label in tabs.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=label)
            self.frames[key] = frame

        self._setup_dashboard_tab()
        self._setup_input_tab()
        self._setup_seating_tab()
        self._setup_faculty_tab()
        self._setup_charts_tab()
        self._setup_report_tab()

    def _setup_dashboard_tab(self):
        tab = self.frames["dashboard"]
        tk.Label(tab, text="Exam Management Dashboard",
                 font=("Arial", 22, "bold"), bg="#f0f4f8",
                 fg=self.colors["primary"]).pack(pady=18)

        metrics_frame = tk.Frame(tab, bg="#f0f4f8")
        metrics_frame.pack(pady=10)

        self.metric_vars = {}
        metrics = [
            ("Total Students",   "enrolled",    "0",    self.colors["info"]),
            ("Seated / Session", "seated",      "0",    self.colors["success"]),
            ("Rooms Used",       "rooms_used",  "0/30", self.colors["warn"]),
            ("Avg Utilisation",  "utilisation", "0%",   self.colors["purple"]),
            ("Faculty Deployed", "faculty",     "0",    self.colors["teal"]),
            ("Clusters (k)",     "clusters",    "0",    self.colors["danger"]),
        ]
        for i, (title, key, default, color) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg="white", relief=tk.RAISED, bd=1,
                            width=210, height=120)
            card.grid(row=i // 3, column=i % 3, padx=15, pady=15)
            card.pack_propagate(False)
            tk.Label(card, text=title, font=("Arial", 11),
                     bg="white", fg="#555").pack(pady=(14, 4))
            var = tk.StringVar(value=default)
            self.metric_vars[key] = var
            tk.Label(card, textvariable=var, font=("Arial", 26, "bold"),
                     bg="white", fg=color).pack()

        status_frame = tk.LabelFrame(tab, text="Pipeline Log",
                                     font=("Arial", 13, "bold"), bg="#f0f4f8")
        status_frame.pack(fill="x", padx=50, pady=16)

        self.status_text = tk.Text(status_frame, height=12, font=("Consolas", 10))
        sb = tk.Scrollbar(status_frame, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _setup_input_tab(self):
        tab = self.frames["input"]
        tk.Label(tab, text="Exam Configuration",
                 font=("Arial", 18, "bold"), bg="#f0f4f8",
                 fg=self.colors["primary"]).pack(pady=16)

        main_frame = tk.Frame(tab, bg="#f0f4f8")
        main_frame.pack(fill="both", expand=True, padx=40)

        # ── Left: parameters ──────────────────────────────────────────────────
        cfg = tk.LabelFrame(main_frame, text="Parameters",
                            font=("Arial", 12, "bold"), bg="#f0f4f8")
        cfg.pack(side=tk.LEFT, fill="both", expand=True, padx=10)

        tk.Label(cfg, text="Total Students:",
                 bg="#f0f4f8", font=("Arial", 11)).pack(pady=(12, 4))
        self.student_count_var = tk.StringVar(value=str(DEFAULT_TOTAL_STUDENTS))
        tk.Entry(cfg, textvariable=self.student_count_var,
                 width=20, font=("Arial", 11)).pack()

        # Hint: changing total auto-redistributes domain counts
        tk.Label(cfg, text="↑ Change total → domain counts update automatically",
                 bg="#f0f4f8", font=("Arial", 9), fg="#888").pack()

        tk.Label(cfg, text="Domain Distribution:",
                 bg="#f0f4f8", font=("Arial", 11, "bold")).pack(pady=(14, 4))
        tk.Label(cfg, text="(edit freely; total will sync to their sum)",
                 bg="#f0f4f8", font=("Arial", 9), fg="#888").pack(pady=(0, 6))

        self.domain_vars = {}
        dom_frame = tk.Frame(cfg, bg="#f0f4f8")
        dom_frame.pack()
        for i, domain in enumerate(DOMAINS):
            tk.Label(dom_frame, text=f"{domain}:", bg="#f0f4f8",
                     font=("Arial", 10)).grid(row=i, column=0, sticky="w",
                                              padx=6, pady=3)
            var = tk.StringVar(value=str(DEFAULT_DOMAIN_COUNTS[domain]))
            self.domain_vars[domain] = var
            tk.Entry(dom_frame, textvariable=var,
                     width=8, font=("Arial", 10)).grid(row=i, column=1,
                                                       padx=6, pady=3)

        # Live sum indicator — turns red when domain sum ≠ total
        self.sum_label_var = tk.StringVar(value=f"Domain sum: {DEFAULT_TOTAL_STUDENTS}  ✓")
        self.sum_label = tk.Label(cfg, textvariable=self.sum_label_var,
                                  bg="#f0f4f8", font=("Arial", 10, "bold"),
                                  fg=self.colors["success"])
        self.sum_label.pack(pady=(6, 0))

        tk.Label(cfg, text="Number of Rooms:",
                 bg="#f0f4f8", font=("Arial", 11)).pack(pady=(16, 4))
        self.room_count_var = tk.StringVar(value=str(DEFAULT_ROOM_COUNT))
        tk.Entry(cfg, textvariable=self.room_count_var,
                 width=20, font=("Arial", 11)).pack()

        tk.Button(cfg, text="  RUN PIPELINE", command=self.run_pipeline,
                  bg=self.colors["success"], fg="white",
                  font=("Arial", 13, "bold"), padx=28, pady=10).pack(pady=24)

        # ── Right: preview ────────────────────────────────────────────────────
        prev = tk.LabelFrame(main_frame, text="Student Data Preview",
                             font=("Arial", 12, "bold"), bg="#f0f4f8")
        prev.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)

        self.preview_tree = ttk.Treeview(prev, height=16)
        sb2 = ttk.Scrollbar(prev, orient=tk.VERTICAL,
                             command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=sb2.set)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Wire up live sync after all widgets exist ─────────────────────────
        self._attach_sync_traces()

    def _setup_seating_tab(self):
        tab = self.frames["seating"]
        top = tk.Frame(tab, bg="#f0f4f8")
        top.pack(fill="x", padx=10, pady=8)

        tk.Label(top, text="Select Room:", bg="#f0f4f8",
                 font=("Arial", 12)).pack(side=tk.LEFT, padx=6)
        self.room_combo = ttk.Combobox(top, width=10, font=("Arial", 11))
        self.room_combo.pack(side=tk.LEFT, padx=6)
        self.room_combo.bind("<<ComboboxSelected>>", self._on_room_select)

        tk.Label(top, text="Select Shift:", bg="#f0f4f8",
                 font=("Arial", 12)).pack(side=tk.LEFT, padx=(20, 6))
        self.shift_combo = ttk.Combobox(top, width=6, font=("Arial", 11))
        self.shift_combo.pack(side=tk.LEFT, padx=6)
        self.shift_combo.bind("<<ComboboxSelected>>", self._on_room_select)

        self.seating_tree = ttk.Treeview(tab, height=22)
        sb = ttk.Scrollbar(tab, orient=tk.VERTICAL,
                           command=self.seating_tree.yview)
        self.seating_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.seating_tree.pack(fill="both", expand=True, padx=10, pady=6)

    def _setup_faculty_tab(self):
        tab = self.frames["faculty"]
        self.faculty_tree = ttk.Treeview(tab, height=24)
        sb = ttk.Scrollbar(tab, orient=tk.VERTICAL,
                           command=self.faculty_tree.yview)
        self.faculty_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.faculty_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _setup_charts_tab(self):
        cn = ttk.Notebook(self.frames["charts"])
        cn.pack(fill="both", expand=True, padx=8, pady=8)

        self.domain_chart_frame  = ttk.Frame(cn)
        self.util_chart_frame    = ttk.Frame(cn)
        self.cluster_chart_frame = ttk.Frame(cn)
        self.batch_chart_frame   = ttk.Frame(cn)

        cn.add(self.domain_chart_frame,  text="Domain Distribution")
        cn.add(self.util_chart_frame,    text="Room Utilisation")
        cn.add(self.cluster_chart_frame, text="Cluster Distribution")
        cn.add(self.batch_chart_frame,   text="Batch Distribution")

    def _setup_report_tab(self):
        tab = self.frames["report"]
        self.report_text = tk.Text(tab, font=("Consolas", 10))
        sb = tk.Scrollbar(tab, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(tab, bg="#f0f4f8")
        btn_frame.pack(fill="x", pady=8)
        tk.Button(btn_frame, text="Save Report (.txt)",
                  command=self._save_report,
                  bg=self.colors["info"], fg="white",
                  font=("Arial", 11), padx=18).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Export to Excel (.xlsx)",
                  command=self._export_excel,
                  bg=self.colors["success"], fg="white",
                  font=("Arial", 11), padx=18).pack(side=tk.LEFT, padx=10)

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.status_text.see(tk.END)
        self.root.update()

    # ── Two-way live sync: total ↔ domain fields ──────────────────────────────

    def _attach_sync_traces(self):
        """
        Attach StringVar traces so:
          • Editing Total Students  → domain counts scale proportionally.
          • Editing any domain field → Total Students updates to their sum.
        A guard flag (_syncing) prevents infinite recursion.
        """
        self._syncing = False
        self.student_count_var.trace_add("write", self._on_total_changed)
        for var in self.domain_vars.values():
            var.trace_add("write", self._on_domain_changed)

    def _on_total_changed(self, *_):
        """When user edits Total Students, redistribute domain counts proportionally."""
        if self._syncing:
            return
        try:
            new_total = int(self.student_count_var.get())
        except ValueError:
            return  # user mid-typing; wait for valid integer

        if new_total <= 0:
            return

        self._syncing = True
        try:
            # Current domain counts (use defaults if invalid)
            raw = {}
            for d in DOMAINS:
                try:
                    raw[d] = max(1, int(self.domain_vars[d].get()))
                except ValueError:
                    raw[d] = DEFAULT_DOMAIN_COUNTS[d]

            raw_sum = sum(raw.values())
            new_counts = {d: round(raw[d] / raw_sum * new_total) for d in DOMAINS}

            # Fix rounding drift so counts sum exactly to new_total
            diff = new_total - sum(new_counts.values())
            new_counts[DOMAINS[0]] += diff

            for d in DOMAINS:
                self.domain_vars[d].set(str(new_counts[d]))

            self._refresh_sum_label(new_total, new_total)
        finally:
            self._syncing = False

    def _on_domain_changed(self, *_):
        """When user edits any domain field, update Total Students to their sum."""
        if self._syncing:
            return
        try:
            domain_sum = sum(
                int(self.domain_vars[d].get()) for d in DOMAINS
            )
        except ValueError:
            return  # user mid-typing

        self._syncing = True
        try:
            self.student_count_var.set(str(domain_sum))
            self._refresh_sum_label(domain_sum, domain_sum)
        finally:
            self._syncing = False

    def _refresh_sum_label(self, domain_sum, total):
        """Update the sum indicator label colour and text."""
        if domain_sum == total:
            self.sum_label_var.set(f"Domain sum: {domain_sum}  ✓")
            self.sum_label.config(fg=self.colors["success"])
        else:
            self.sum_label_var.set(
                f"Domain sum: {domain_sum}  ✗  (total = {total})")
            self.sum_label.config(fg=self.colors["danger"])

    # ── Step 1 – Data Collection ──────────────────────────────────────────────

    def _generate_student_data(self):
        """
        Generate students for batches 19-23, 5 domains.
        Total students kept in 2400-2500 range as per problem statement.
        """
        self._log("Step 1 ▶ Generating student data (batches 19-23) ...")

        # Domain counts come directly from the UI — already in sync with total
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
            remainder = count % len(BATCHES)   # distribute leftover students to first batches

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

    # ── Step 2 – Room Data ────────────────────────────────────────────────────

    def _generate_room_data(self):
        """
        Generate 30 rooms: mix of 25, 30, and 32-35 seat capacities
        as stated in the problem (capacity 30-35, few rooms with 25 seats).
        """
        self._log("Step 2 ▶ Generating room data ...")

        n = int(self.room_count_var.get())
        room_ids = [f"R{i+1:02d}" for i in range(n)]

        # Problem says: 30-35 capacity, a few rooms with 25 seats
        caps = ([25] * 4            # few 25-seat rooms
                + [30] * 14          # majority 30-seat
                + [32] * 8           # medium
                + [35] * 4)          # large rooms
        caps = caps[:n]
        np.random.seed(42)
        np.random.shuffle(caps)

        self.room_df = pd.DataFrame({"room_id": room_ids, "capacity": caps})
        self._log(f"  ✓ {n} rooms | Total capacity: {self.room_df['capacity'].sum()} seats")
        return self.room_df

    # ── Step 3 – Faculty Data ─────────────────────────────────────────────────

    def _generate_faculty_data(self):
        """One faculty list per domain; names from FACULTY_NAMES dictionary."""
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

    # ── Step 4 – K-Means Clustering ───────────────────────────────────────────

    def _run_clustering(self):
        """
        K-Means Clustering using BOTH domain and batch as features,
        as required by the problem statement (group by domain + batch).

        Optimal k: number of rooms (30) so each cluster maps to one room/exam group.
        """
        self._log("Step 4 ▶ Running K-Means clustering (domain + batch features) ...")

        # Encode categorical features numerically
        domain_enc = LabelEncoder().fit_transform(self.student_df["domain"])
        batch_enc  = LabelEncoder().fit_transform(self.student_df["batch"])

        # Feature matrix: [domain_encoded, batch_encoded]
        X = np.column_stack([domain_enc, batch_enc])

        # Standardise so neither feature dominates distance calculation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Optimal k = number of rooms (each cluster fills roughly one room)
        optimal_k = min(len(self.room_df), len(self.student_df) // 25)
        self._log(f"  Using k = {optimal_k} clusters")

        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20, max_iter=500)
        self.student_df["cluster"] = kmeans.fit_predict(X_scaled)

        counts = self.student_df["cluster"].value_counts()
        self._log(f"  ✓ Clusters: min={counts.min()} max={counts.max()} "
                  f"mean={counts.mean():.1f}")
        self.metric_vars["clusters"].set(str(optimal_k))

    # ── Step 5 – Seating Plan ─────────────────────────────────────────────────

    def _generate_seating_plan(self):
        """
        Assign students to rooms respecting capacity limits.
        Students sorted by cluster (domain+batch group) so same-cluster
        students sit together. Multiple shifts used when students > capacity.
        Each shift fills all rooms before starting a new shift.
        """
        self._log("Step 5 ▶ Generating seating plan ...")

        total_capacity = self.room_df["capacity"].sum()
        rooms = self.room_df.set_index("room_id")["capacity"].to_dict()
        room_list = list(rooms.keys())

        # Sort by cluster so same-domain/batch groups sit together
        ordered = self.student_df.sort_values(
            ["cluster", "domain", "batch"]
        ).reset_index(drop=True)

        assignments = []
        shift = 1
        # seat_used[room] resets at every new shift
        seat_used = {r: 0 for r in room_list}
        room_idx = 0   # pointer into room_list

        for _, student in ordered.iterrows():
            # Advance to a room that still has space in current shift
            while room_idx < len(room_list) and \
                    seat_used[room_list[room_idx]] >= rooms[room_list[room_idx]]:
                room_idx += 1

            # All rooms full → start new shift
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
        util   = len(self.seating_df) / (total_capacity * shifts) * 100

        self._log(f"  ✓ Seated: {len(self.seating_df)} | "
                  f"Shifts: {shifts} | Rooms used per shift: {rooms_used}")

        self.metric_vars["enrolled"].set(str(len(self.student_df)))
        self.metric_vars["seated"].set(str(len(self.seating_df) // shifts))
        self.metric_vars["rooms_used"].set(f"{rooms_used}/{len(self.room_df)}")
        self.metric_vars["utilisation"].set(f"{util:.1f}%")

        return self.seating_df

    # ── Step 6 – Faculty Allocation ───────────────────────────────────────────

    def _allocate_faculty(self):
        """
        Assign faculty to rooms.
        Requirement: each room gets at least one faculty from each domain
        whose students appear in that room.  A cycling pool ensures no
        faculty member is overloaded.
        """
        self._log("Step 6 ▶ Allocating faculty to rooms ...")

        # Build cycling pool per domain so we can keep re-using names if needed
        faculty_pool = {
            d: list(self.faculty_df[self.faculty_df["domain"] == d]["faculty_name"])
            for d in DOMAINS
        }
        pool_idx = {d: 0 for d in DOMAINS}

        def pick_faculty(domain):
            """Round-robin selection from domain pool."""
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

            # Assign one faculty per domain present in this room
            assigned_faculty = []
            for d in domains_present:
                assigned_faculty.append(pick_faculty(d))

            allocations.append({
                "room_id":        room_id,
                "students":       len(room_students),
                "dominant_domain": dominant_domain,
                "domains_present": ", ".join(domains_present),
                "faculty_names":  "; ".join(assigned_faculty),
            })

        self.allocation_df = pd.DataFrame(allocations)
        self._log(f"  ✓ Faculty deployed across {len(self.allocation_df)} rooms")
        self.metric_vars["faculty"].set(str(len(self.allocation_df)))
        return self.allocation_df

    # ── UI Update Methods ─────────────────────────────────────────────────────

    def _update_preview(self):
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        if self.student_df is None:
            return
        cols = ["student_id", "batch", "domain", "cluster"]
        self.preview_tree["columns"] = cols
        self.preview_tree["show"]    = "headings"
        widths = [130, 70, 200, 80]
        for col, w in zip(cols, widths):
            self.preview_tree.heading(col, text=col.replace("_", " ").title())
            self.preview_tree.column(col, width=w)
        for _, row in self.student_df.head(25).iterrows():
            self.preview_tree.insert("", "end", values=(
                row["student_id"], row["batch"], row["domain"], row["cluster"]
            ))

    def _update_seating_tab(self):
        if self.seating_df is None:
            return
        rooms  = sorted(self.seating_df["room_assigned"].unique())
        shifts = sorted(self.seating_df["exam_shift"].unique())
        self.room_combo["values"]  = rooms
        self.shift_combo["values"] = shifts
        self.room_combo.set(rooms[0])
        self.shift_combo.set(shifts[0])
        self._show_room_seating(rooms[0], shifts[0])

    def _show_room_seating(self, room_id, shift):
        for item in self.seating_tree.get_children():
            self.seating_tree.delete(item)
        subset = self.seating_df[
            (self.seating_df["room_assigned"] == room_id) &
            (self.seating_df["exam_shift"]    == int(shift))
        ]
        cols  = ["seat_number", "student_id", "batch", "domain", "cluster"]
        heads = ["Seat", "Roll No.", "Batch", "Domain", "Cluster"]
        widths = [70, 140, 70, 200, 80]
        self.seating_tree["columns"] = cols
        self.seating_tree["show"]    = "headings"
        for col, h, w in zip(cols, heads, widths):
            self.seating_tree.heading(col, text=h)
            self.seating_tree.column(col, width=w)
        for _, row in subset.iterrows():
            self.seating_tree.insert("", "end", values=(
                row["seat_number"], row["student_id"],
                row["batch"], row["domain"], row["cluster"]
            ))

    def _update_faculty_view(self):
        for item in self.faculty_tree.get_children():
            self.faculty_tree.delete(item)
        if self.allocation_df is None:
            return
        cols  = ["room_id", "students", "dominant_domain",
                 "domains_present", "faculty_names"]
        heads = ["Room", "Students", "Main Domain",
                 "Domains Present", "Invigilators"]
        widths = [70, 80, 160, 280, 320]
        self.faculty_tree["columns"] = cols
        self.faculty_tree["show"]    = "headings"
        for col, h, w in zip(cols, heads, widths):
            self.faculty_tree.heading(col, text=h)
            self.faculty_tree.column(col, width=w)
        for _, row in self.allocation_df.iterrows():
            self.faculty_tree.insert("", "end", values=(
                row["room_id"], row["students"], row["dominant_domain"],
                row["domains_present"], row["faculty_names"]
            ))

    def _update_charts(self):
        if self.student_df is None:
            return

        # Chart 1 – Domain Distribution
        self._clear_frame(self.domain_chart_frame)
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        domain_counts = self.student_df["domain"].value_counts()
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
        ax1.pie(domain_counts.values, labels=domain_counts.index,
                autopct="%1.1f%%", colors=colors, startangle=90)
        ax1.set_title("Student Distribution by Domain")
        FigureCanvasTkAgg(fig1, master=self.domain_chart_frame).get_tk_widget()\
            .pack(fill="both", expand=True)

        # Chart 2 – Room Utilisation
        self._clear_frame(self.util_chart_frame)
        if self.seating_df is not None:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            s1 = self.seating_df[self.seating_df["exam_shift"] == 1]
            room_usage = s1["room_assigned"].value_counts()
            room_cap   = dict(zip(self.room_df["room_id"], self.room_df["capacity"]))
            rooms_sorted = sorted(room_cap.keys())
            utils = [room_usage.get(r, 0) / room_cap[r] * 100
                     for r in rooms_sorted]
            ax2.bar(rooms_sorted, utils, color="#27ae60", alpha=0.75, edgecolor="white")
            ax2.axhline(100, color="red", linestyle="--", linewidth=1, label="Full capacity")
            ax2.set_xlabel("Room"); ax2.set_ylabel("Utilisation (%)")
            ax2.set_title("Room Utilisation (Shift 1)")
            ax2.tick_params(axis="x", rotation=60)
            ax2.legend()
            fig2.tight_layout()
            FigureCanvasTkAgg(fig2, master=self.util_chart_frame).get_tk_widget()\
                .pack(fill="both", expand=True)

        # Chart 3 – Cluster Distribution
        self._clear_frame(self.cluster_chart_frame)
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        cc = self.student_df["cluster"].value_counts().sort_index()
        ax3.bar(cc.index, cc.values, color="#3498db", alpha=0.75, edgecolor="white")
        ax3.set_xlabel("Cluster ID"); ax3.set_ylabel("Number of Students")
        ax3.set_title("K-Means Cluster Sizes")
        fig3.tight_layout()
        FigureCanvasTkAgg(fig3, master=self.cluster_chart_frame).get_tk_widget()\
            .pack(fill="both", expand=True)

        # Chart 4 – Batch Distribution
        self._clear_frame(self.batch_chart_frame)
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        bc = self.student_df["batch"].value_counts().sort_index()
        ax4.bar([str(b) for b in bc.index], bc.values,
                color=colors, edgecolor="white")
        ax4.set_xlabel("Batch"); ax4.set_ylabel("Number of Students")
        ax4.set_title("Student Count per Batch (19-23)")
        fig4.tight_layout()
        FigureCanvasTkAgg(fig4, master=self.batch_chart_frame).get_tk_widget()\
            .pack(fill="both", expand=True)

    @staticmethod
    def _clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _update_report(self):
        if self.student_df is None:
            return
        total_cap = self.room_df["capacity"].sum()
        shifts    = self.seating_df["exam_shift"].nunique()
        seated_s1 = len(self.seating_df[self.seating_df["exam_shift"] == 1])
        util      = seated_s1 / total_cap * 100

        report = f"""
{'='*65}
   EXAM MANAGEMENT SYSTEM – FINAL REPORT
   National University of CS & Emerging Sciences, Faisalabad
{'='*65}
   Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*65}

   STUDENT STATISTICS
   {'-'*55}
   Total Students Enrolled   : {len(self.student_df)}
   Batches                   : {sorted(self.student_df['batch'].unique())}

   Domain Breakdown:
{self.student_df['domain'].value_counts().to_string()}

   Batch Breakdown:
{self.student_df['batch'].value_counts().sort_index().to_string()}

   CLUSTERING (K-Means) STATISTICS
   {'-'*55}
   Feature Set               : Domain + Batch (both encoded & scaled)
   Clusters Used (k)         : {self.student_df['cluster'].nunique()}
   Min Cluster Size          : {self.student_df['cluster'].value_counts().min()}
   Max Cluster Size          : {self.student_df['cluster'].value_counts().max()}
   Mean Cluster Size         : {self.student_df['cluster'].value_counts().mean():.1f}

   SEATING STATISTICS
   {'-'*55}
   Total Rooms Available     : {len(self.room_df)}
   Total Seat Capacity       : {total_cap}
   Students Seated (Shift 1) : {seated_s1}
   Exam Shifts Required      : {shifts}
   Room Utilisation (Shift 1): {util:.1f}%
   Capacity Range            : {self.room_df['capacity'].min()} – {self.room_df['capacity'].max()} seats

   FACULTY STATISTICS
   {'-'*55}
   Total Faculty Available   : {len(self.faculty_df)}
   Faculty Deployed          : {len(self.allocation_df)}
   Domains Covered           : {len(DOMAINS)}
   (Each room assigned faculty matching all domains present)

{'='*65}
   PIPELINE COMPLETE – All project requirements satisfied
{'='*65}
"""
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_room_select(self, _event=None):
        room  = self.room_combo.get()
        shift = self.shift_combo.get()
        if room and shift:
            self._show_room_seating(room, shift)

    # ── Export / Save ─────────────────────────────────────────────────────────

    def _save_report(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the pipeline first.")
            return
        fn = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="exam_report.txt",
        )
        if fn:
            with open(fn, "w") as f:
                f.write(self.report_text.get(1.0, tk.END))
            messagebox.showinfo("Saved", f"Report saved to:\n{fn}")

    def _export_excel(self):
        if self.student_df is None:
            messagebox.showwarning("No Data", "Run the pipeline first.")
            return
        fn = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="exam_data.xlsx",
        )
        if fn:
            with pd.ExcelWriter(fn, engine="openpyxl") as writer:
                self.student_df.to_excel(writer,   sheet_name="Students", index=False)
                self.seating_df.to_excel(writer,   sheet_name="Seating",  index=False)
                self.allocation_df.to_excel(writer, sheet_name="Faculty",  index=False)
                self.room_df.to_excel(writer,      sheet_name="Rooms",    index=False)
            messagebox.showinfo("Exported", f"Data exported to:\n{fn}")

    # ── Main Pipeline ─────────────────────────────────────────────────────────

    def run_pipeline(self):
        """Execute all 6 steps in a background thread to keep the GUI responsive."""
        self._log("\n" + "=" * 55)
        self._log("STARTING EXAM MANAGEMENT PIPELINE")
        self._log("=" * 55)

        def _thread():
            try:
                self._generate_student_data()   # Step 1 – Data Collection
                self._generate_room_data()       # Step 1 – Room data
                self._generate_faculty_data()    # Step 1 – Faculty data
                self._run_clustering()           # Step 4 – K-Means
                self._generate_seating_plan()    # Step 5 – Seating
                self._allocate_faculty()         # Step 6 – Faculty Allocation

                # Update all UI elements on the main thread
                self.root.after(0, self._update_preview)
                self.root.after(0, self._update_seating_tab)
                self.root.after(0, self._update_faculty_view)
                self.root.after(0, self._update_charts)
                self.root.after(0, self._update_report)

                self._log("\n" + "=" * 55)
                self._log("✓  PIPELINE COMPLETE – All outputs generated")
                self._log("=" * 55 + "\n")
                messagebox.showinfo("Done", "Pipeline completed successfully!")

            except Exception as exc:
                self._log(f"ERROR: {exc}")
                messagebox.showerror("Pipeline Error", str(exc))

        Thread(target=_thread, daemon=True).start()


def main():
    root = tk.Tk()
    ExamManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
