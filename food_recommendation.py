"""
╔══════════════════════════════════════════════════════════════════╗
║       NHAM EY KOR BAN — Phnom Penh Food Recommendation System ║|||
║    Data Structure + Data Manipulation + Data Visualization       ║
║              Scoring Algorithm + Tkinter GUI                     ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO RUN:
    pip install matplotlib numpy pillow tkintermapview
    python food_recommendation.py
"""
# pasted this pip install matplotlib numpy
import tkinter as tk
from PIL import Image, ImageTk
from dataSet import FOOD_DATASET, CUISINES, ALLERGIES   # CUISINES & ALLERGIES now used in UI

from tkinter import ttk, messagebox
import tkintermapview
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
import numpy as np


# ══════════════════════════════════════════════════════════════════
#  SCORING WEIGHTS  (total = 100)
# ══════════════════════════════════════════════════════════════════
SCORE_BUDGET  = 30
SCORE_TASTE   = 25
SCORE_MAIN    = 25
SCORE_CUISINE = 20
MAX_SCORE     = SCORE_BUDGET + SCORE_TASTE + SCORE_MAIN + SCORE_CUISINE  # 100

BUDGET_LEVELS = ["low", "mid", "high"]


# ══════════════════════════════════════════════════════════════════
#  SCORING ALGORITHM
# ══════════════════════════════════════════════════════════════════
def score_food(food: dict, budget: str, taste: str, main: str, cuisine: str) -> int:
    score = 0

    # Budget — partial credit for adjacent level
    u_idx = BUDGET_LEVELS.index(budget)
    f_idx = BUDGET_LEVELS.index(food["budget"])
    diff  = abs(u_idx - f_idx)
    if diff == 0:
        score += SCORE_BUDGET
    elif diff == 1:
        score += int(SCORE_BUDGET * 0.4)   # 12 pts partial

    # Taste
    if taste == "any" or food["taste"] == taste:
        score += SCORE_TASTE

    # Main preference
    if main == "any" or food["main"] == main:
        score += SCORE_MAIN

    # Cuisine
    if cuisine == "any" or food["cuisine"] == cuisine:
        score += SCORE_CUISINE

    return score


# ══════════════════════════════════════════════════════════════════
#  DATA MANIPULATION — filter → score → sort
# ══════════════════════════════════════════════════════════════════
def filter_and_score(budget, taste, main, cuisine, allergies) -> list:
    results = []
    for food in FOOD_DATASET:
        # 1. Allergy filter
        if any(a in food["allergens"] for a in allergies):
            continue
        # 2. Score
        s = score_food(food, budget, taste, main, cuisine)
        results.append({**food, "score": s, "pct": round(s / MAX_SCORE * 100)})
    # 3. Sort descending by score  (Timsort O(n log n))
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ══════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════════════════════════
BG       = "#fff7e7"
SURFACE  = "#fff7e7"
SURFACE2 = "#fff7e7"
ACCENT   = "#e83420"
ACCENT2  = "#c0392b"
ACCENT3  = "#27ae60"
TEXT     = "#050505"
MUTED    = "#0f0f0e"
BORDER   = "#100f0e"
WHITE    = "#ffffff"   # FIX: was "#000000" (black), corrected to actual white


# ══════════════════════════════════════════════════════════════════
#  MAIN APP SHELL
# ══════════════════════════════════════════════════════════════════
class FoodMatchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NHAM EY KOR BAN")
        self.geometry("960x680")
        self.minsize(820, 580)
        self.configure(bg=BG)

        # Shared preference variables
        self.budget_var  = tk.StringVar(value="mid")
        self.taste_var   = tk.StringVar(value="any")
        self.main_var    = tk.StringVar(value="any")
        self.cuisine_var = tk.StringVar(value="any")

        # FIX: allergy_vars now built from ALLERGIES list imported from dataSet
        self.allergy_vars = {k: tk.BooleanVar() for k in ALLERGIES}

        self.results: list = []

        # Stack pages
        self.frames = {}
        for Cls in (WelcomePage, InputPage, ResultPage):
            f = Cls(self)
            self.frames[Cls.__name__] = f
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show("WelcomePage")

    def show(self, name: str):
        f = self.frames[name]
        f.tkraise()
        if hasattr(f, "on_show"):
            f.on_show()


# ══════════════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ══════════════════════════════════════════════════════════════════
def sec_label(parent, text):
    tk.Label(parent, text=text, font=("Helvetica", 11, "bold"),
             bg=SURFACE, fg=ACCENT, anchor="w").pack(fill="x", padx=10, pady=(10, 2))

def radio_row(parent, var, options):
    row = tk.Frame(parent, bg=SURFACE)
    row.pack(fill="x", padx=10, pady=2)
    for label, val in options:
        tk.Radiobutton(row, text=label, variable=var, value=val,
                       bg=SURFACE, fg=TEXT, selectcolor=SURFACE2,
                       activebackground=SURFACE, activeforeground=ACCENT,
                       font=("Helvetica", 10)).pack(side="left", padx=4)


# ══════════════════════════════════════════════════════════════════
#  PAGE 1 — WELCOME
# ══════════════════════════════════════════════════════════════════
class WelcomePage(tk.Frame):
    def __init__(self, master: FoodMatchApp):
        super().__init__(master, bg=BG)

        # ── Logo ─────────────────────────────────────────
        try:
            img = Image.open("NHAM EY KOR BAN.png")
            img = img.resize((200, 200), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(img)   # must keep reference!
            tk.Label(self, image=self._logo, bg=BG).pack(pady=(50, 8))
        except Exception:
            tk.Label(self, text="🍽️", font=("Segoe UI Emoji", 64),
                     bg=BG, fg=ACCENT).pack(pady=(70, 8))
        # ─────────────────────────────────────────────────

        tk.Label(self, text="NHAM EY KOR BAN",
                 font=("Georgia", 44, "bold"), bg=BG, fg=ACCENT).pack()

        tk.Label(self, text="Phnom Penh Local Food Recommender",
                 font=("Helvetica", 14), bg=BG, fg=MUTED).pack(pady=(4, 8))

        tk.Label(self,
                 text="Tell us your budget, taste & preferences —\n"
                      "we'll find the perfect Phnom Penh dish for you! 🇰🇭",
                 font=("Helvetica", 11), bg=BG, fg=TEXT, justify="center").pack(pady=(8, 36))

        btn = tk.Button(self, text="  Get Started  →",
                        font=("Helvetica", 13, "bold"),
                        bg=ACCENT, fg=BG, relief="flat", cursor="hand2",
                        padx=26, pady=10,
                        command=lambda: master.show("InputPage"))
        btn.pack()
        btn.bind("<Enter>", lambda e: btn.configure(bg="#ffc240"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=ACCENT))

        tk.Label(self,
                 text=f"🗺  {len(FOOD_DATASET)} local spots  ·  "
                      f"{len(set(f['cuisine'] for f in FOOD_DATASET))} cuisines  ·  "
                      f"Scoring algorithm with allergy filter",
                 font=("Helvetica", 9), bg=BG, fg=MUTED).pack(pady=(28, 0))


# ══════════════════════════════════════════════════════════════════
#  PAGE 2 — INPUT FORM
# ══════════════════════════════════════════════════════════════════
class InputPage(tk.Frame):
    def __init__(self, master: FoodMatchApp):
        super().__init__(master, bg=BG)
        self._master = master

        # Header
        hdr = tk.Frame(self, bg=SURFACE2, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔍  Your Preferences",
                 font=("Georgia", 18, "bold"), bg=SURFACE2, fg=ACCENT).pack()
        tk.Label(hdr, text="Fill in the options below, then click Recommend",
                 font=("Helvetica", 10), bg=SURFACE2, fg=MUTED).pack()

        # Scrollable body
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=SURFACE, padx=16, pady=10)
        win  = canvas.create_window((0, 0), window=body, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())
        body.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── Budget ──
        sec_label(body, "  Budget")
        radio_row(body, master.budget_var, [
            ("Low  (< $3)", "low"),
            ("Mid  ($3–$10)", "mid"),
            ("High (> $30)", "high"),
        ])

        # ── Taste ──
        sec_label(body, "  Taste Profile")
        radio_row(body, master.taste_var, [
            ("Any", "any"), ("Savory", "savory"), ("Spicy", "spicy"),
            ("Sweet", "sweet"), ("Sour", "sour"), ("Mild", "mild"),
        ])

        # ── Main Preference ──
        sec_label(body, " Main Preference")
        radio_row(body, master.main_var, [
            ("Any", "any"), ("Rice", "rice"), ("Noodles", "noodles"),
            ("Soup", "soup"), ("Snack", "snack"),
        ])
        radio_row(body, master.main_var, [
            ("Sandwich", "sandwich"), ("Seafood", "seafood"), ("Beef", "beef"),
            ("Dessert", "dessert"), ("Drink", "drink"), ("Stir-Fry", "stir-fry"),
        ])

        # ── Cuisine — FIX: now built dynamically from CUISINES list in dataSet ──
        sec_label(body, " Cuisine")
        cuisine_opts = [(c.capitalize(), c) for c in CUISINES]
        for i in range(0, len(cuisine_opts), 4):   # 4 options per row
            radio_row(body, master.cuisine_var, cuisine_opts[i:i+4])

        # ── Allergies — FIX: now built dynamically from ALLERGIES list in dataSet ──
        sec_label(body, "☠️ Allergies / Avoid")
        af = tk.Frame(body, bg=SURFACE)
        af.pack(fill="x", padx=10, pady=4)
        for i, (key, var) in enumerate(master.allergy_vars.items()):
            tk.Checkbutton(af, text=key.capitalize(), variable=var,
                           bg=SURFACE, fg=TEXT, selectcolor=SURFACE2,
                           activebackground=SURFACE, activeforeground=ACCENT,
                           font=("Helvetica", 10)).grid(
                               row=i // 4, column=i % 4, sticky="w", padx=8, pady=2)

        # ── Buttons ──
        btn_row = tk.Frame(body, bg=SURFACE)
        btn_row.pack(fill="x", pady=(20, 10))

        tk.Button(btn_row, text="← Back",
                  font=("Helvetica", 11), bg=SURFACE2, fg=MUTED,
                  relief="flat", cursor="hand2", padx=14, pady=8,
                  command=lambda: master.show("WelcomePage")).pack(side="left", padx=4)

        go = tk.Button(btn_row, text=" Recommend  →",
                       font=("Helvetica", 12, "bold"), bg=MUTED, fg=BG,
                       relief="flat", cursor="hand2", padx=22, pady=8,
                       command=self._recommend)
        go.pack(side="right", padx=4)
        go.bind("<Enter>", lambda e: go.configure(bg="#ffc240"))
        go.bind("<Leave>", lambda e: go.configure(bg=ACCENT))

    def _recommend(self):
        allergies = [k for k, v in self._master.allergy_vars.items() if v.get()]
        results   = filter_and_score(
            budget    = self._master.budget_var.get(),
            taste     = self._master.taste_var.get(),
            main      = self._master.main_var.get(),
            cuisine   = self._master.cuisine_var.get(),
            allergies = allergies,
        )
        if not results:
            messagebox.showwarning("No Results",
                "No food items match your filters.\n"
                "Try relaxing your preferences or allergy selections.")
            return
        self._master.results = results
        self._master.show("ResultPage")


# ══════════════════════════════════════════════════════════════════
#  PAGE 3 — RESULTS + VISUALISATION
# ══════════════════════════════════════════════════════════════════
class ResultPage(tk.Frame):
    def __init__(self, master: FoodMatchApp):
        super().__init__(master, bg=BG)
        self._master     = master
        self._fig_canvas = None   # matplotlib canvas reference
        self._map_widget = None   # map widget reference
        self._chart_vis  = True   # True = map view, False = bar chart view

        # Header
        hdr = tk.Frame(self, bg=SURFACE2, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏆  Top Recommendations — Phnom Penh",
                 font=("Georgia", 17, "bold"), bg=SURFACE2, fg=ACCENT).pack()
        self.sub_lbl = tk.Label(hdr, text="", font=("Helvetica", 10),
                                bg=SURFACE2, fg=MUTED)
        self.sub_lbl.pack()

        # Paned window: list | map/chart
        self._pane = tk.PanedWindow(self, orient="horizontal", bg=BG,
                                    sashwidth=5, sashrelief="flat")
        self._pane.pack(fill="both", expand=True)

        self._left  = tk.Frame(self._pane, bg=BG)
        self._right = tk.Frame(self._pane, bg=BG)
        self._pane.add(self._left,  minsize=370)
        self._pane.add(self._right, minsize=380)

        # Footer
        foot = tk.Frame(self, bg=SURFACE2, pady=8)
        foot.pack(fill="x", side="bottom")
        tk.Button(foot, text="← New Search",
                  font=("Helvetica", 11), bg=SURFACE2, fg=MUTED,
                  relief="flat", cursor="hand2", padx=14, pady=6,
                  command=lambda: master.show("InputPage")).pack(side="left", padx=10)

        # FIX: button label updates to describe what it will switch TO
        self._toggle_btn = tk.Button(
            foot, text="📊 Show Bar Chart",
            font=("Helvetica", 11), bg=ACCENT2, fg=WHITE,
            relief="flat", cursor="hand2", padx=14, pady=6,
            command=self._toggle_chart)
        self._toggle_btn.pack(side="right", padx=10)

    # ── called whenever page is raised ──
    def on_show(self):
        self._chart_vis = True   # always start on map view
        self._toggle_btn.config(text="📊 Show Bar Chart")
        self._build_list()
        self._build_right()

    # ── Ranked food cards ──
    def _build_list(self):
        for w in self._left.winfo_children():
            w.destroy()

        results = self._master.results
        shown   = results[:10]
        self.sub_lbl.config(
            text=f"Top {len(shown)} of {len(results)} matching foods | "
                 f"Max possible score: {MAX_SCORE} pts")

        canvas = tk.Canvas(self._left, bg=BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(self._left, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

        for rank, food in enumerate(shown, 1):
            card = tk.Frame(inner, bg=SURFACE, padx=10, pady=8,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(fill="x", padx=8, pady=4)

            # Row 1: rank + name + score badge
            r1 = tk.Frame(card, bg=SURFACE)
            r1.pack(fill="x")
            medal = MEDALS.get(rank, f"#{rank}")
            tk.Label(r1, text=f"{medal}  {food['emoji']}  {food['name']}",
                     font=("Helvetica", 12, "bold"), bg=SURFACE, fg=TEXT,
                     anchor="w").pack(side="left")

            badge_col = (ACCENT3 if food["pct"] >= 70 else
                         ACCENT  if food["pct"] >= 40 else ACCENT2)
            tk.Label(r1, text=f"{food['pct']}%",
                     font=("Helvetica", 11, "bold"),
                     bg=badge_col, fg=BG, padx=6, pady=1).pack(side="right")

            # Row 2: place
            tk.Label(card, text=f"📍 {food['place']}",
                     font=("Helvetica", 9), bg=SURFACE, fg=MUTED,
                     anchor="w").pack(fill="x")

            # Row 3: desc + price
            r3 = tk.Frame(card, bg=SURFACE)
            r3.pack(fill="x", pady=(2, 0))
            tk.Label(r3, text=food["desc"],
                     font=("Helvetica", 9, "italic"), bg=SURFACE, fg=MUTED,
                     anchor="w", wraplength=280, justify="left").pack(side="left")
            tk.Label(r3, text=food["price"],
                     font=("Helvetica", 9, "bold"), bg=SURFACE, fg=ACCENT).pack(side="right")

            # Score bar
            bar_bg = tk.Frame(card, bg=BORDER, height=6)
            bar_bg.pack(fill="x", pady=(6, 0))
            bar_bg.update_idletasks()
            fill = tk.Frame(bar_bg, bg=badge_col, height=6)
            fill.place(relwidth=max(0.02, food["pct"] / 100), relheight=1)

            # Score breakdown tooltip label
            tk.Label(card,
                     text=f"Score: {food['score']}/{MAX_SCORE}  "
                          f"| Budget:{food['budget']}  Taste:{food['taste']}  "
                          f"Cuisine:{food['cuisine']}",
                     font=("Helvetica", 8), bg=SURFACE, fg=BORDER).pack(anchor="w")

    # ══════════════════════════════════════════════════════════════
    #  RIGHT PANEL — rebuilds to whichever view is active
    # ══════════════════════════════════════════════════════════════
    def _build_right(self):
        for w in self._right.winfo_children():
            w.destroy()
        self._fig_canvas = None
        self._map_widget = None

        if self._chart_vis:
            self._build_map()
        else:
            self._build_chart()

    # ── Interactive Map ──
    def _build_map(self):
        results = self._master.results
        top10   = results[:10]

        # Create the map widget centered on Phnom Penh
        self._map_widget = tkintermapview.TkinterMapView(
            self._right, width=460, height=520, corner_radius=0
        )
        self._map_widget.pack(fill="both", expand=True, padx=4, pady=4)
        self._map_widget.set_position(11.5564, 104.9282)  # Phnom Penh center
        self._map_widget.set_zoom(13)

        MEDAL_ICONS = {1: "🥇", 2: "🥈", 3: "🥉"}

        for rank, food in enumerate(top10, 1):
            lat = food.get("lat")
            lng = food.get("lng")
            if lat and lng:
                medal = MEDAL_ICONS.get(rank, f"#{rank}")
                label = f"{medal} {food['emoji']} {food['name']} ({food['pct']}%)"
                self._map_widget.set_marker(lat, lng, text=label)

    # ── Matplotlib Stacked Bar Chart — shows score breakdown per category ──
    # This is always realistic because it shows HOW each food earned its score,
    # even when totals are equal (e.g. all "any" → each segment explains why).
    def _build_chart(self):
        results = self._master.results
        top10   = results[:10]

        # Re-compute per-category score for each food so the chart is always
        # meaningful regardless of what the user selected
        budget_sel  = self._master.budget_var.get()
        taste_sel   = self._master.taste_var.get()
        main_sel    = self._master.main_var.get()
        cuisine_sel = self._master.cuisine_var.get()

        def _cat_scores(food):
            # Budget component
            u_idx = BUDGET_LEVELS.index(budget_sel)
            f_idx = BUDGET_LEVELS.index(food["budget"])
            diff  = abs(u_idx - f_idx)
            if diff == 0:
                b = SCORE_BUDGET
            elif diff == 1:
                b = int(SCORE_BUDGET * 0.4)   # 12 pts partial
            else:
                b = 0
            # Taste component
            t = SCORE_TASTE   if (taste_sel   == "any" or food["taste"]   == taste_sel)   else 0
            # Main component
            m = SCORE_MAIN    if (main_sel    == "any" or food["main"]    == main_sel)    else 0
            # Cuisine component
            c = SCORE_CUISINE if (cuisine_sel == "any" or food["cuisine"] == cuisine_sel) else 0
            return b, t, m, c

        # Shorten long names for x-axis labels
        names = [f["name"][:13] + "…" if len(f["name"]) > 13
                 else f["name"] for f in top10]

        cat_data = [_cat_scores(f) for f in top10]
        b_vals = [d[0] for d in cat_data]
        t_vals = [d[1] for d in cat_data]
        m_vals = [d[2] for d in cat_data]
        c_vals = [d[3] for d in cat_data]

        # Missed points (grey) = what was NOT scored — shows lost potential
        missed = [MAX_SCORE - (b+t+m+c) for b, t, m, c in cat_data]

        x = np.arange(len(names))

        fig = Figure(figsize=(5, 4.8), dpi=96, facecolor="#fff7e7")
        ax  = fig.add_subplot(111)
        ax.set_facecolor("#fff7e7")

        # Stack: Budget → Taste → Main → Cuisine → Missed (grey)
        p1 = ax.bar(x, b_vals,                           color="#e83420", label=f"Budget  (/{SCORE_BUDGET})",  zorder=3)
        p2 = ax.bar(x, t_vals, bottom=b_vals,            color="#f39c12", label=f"Taste   (/{SCORE_TASTE})",   zorder=3)
        p3 = ax.bar(x, m_vals, bottom=np.add(b_vals, t_vals),
                    color="#27ae60", label=f"Main    (/{SCORE_MAIN})",    zorder=3)
        p4 = ax.bar(x, c_vals,
                    bottom=np.add(np.add(b_vals, t_vals), m_vals),
                    color="#2980b9", label=f"Cuisine (/{SCORE_CUISINE})", zorder=3)
        ax.bar(x, missed,
               bottom=np.add(np.add(np.add(b_vals, t_vals), m_vals), c_vals),
               color="#ddd5c8", label="Not matched", zorder=3)

        # Total score label on top of each bar
        for i, food in enumerate(top10):
            ax.text(i, food["score"] + 0.8, str(food["score"]),
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color="#050505")

        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("Score breakdown / 100", fontsize=9)
        ax.set_title("Top 10 — Score Breakdown by Category", fontsize=10,
                     fontweight="bold", color="#e83420")
        ax.set_ylim(0, MAX_SCORE + 12)
        ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, loc="upper right",
                  framealpha=0.85, ncol=1)

        fig.tight_layout()

        # Embed matplotlib figure into the Tkinter frame
        self._fig_canvas = FigureCanvasTkAgg(fig, master=self._right)
        self._fig_canvas.draw()
        self._fig_canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=4, pady=4)

    # ── FIX: Toggle now truly switches between Map and Bar Chart ──
    def _toggle_chart(self):
        if self._chart_vis:
            # currently on map → switch to bar chart
            self._chart_vis = False
            self._toggle_btn.config(text="🗺  Show Map")
        else:
            # currently on bar chart → switch to map
            self._chart_vis = True
            self._toggle_btn.config(text="📊 Show Bar Chart")
        self._build_right()


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = FoodMatchApp()
    app.mainloop()