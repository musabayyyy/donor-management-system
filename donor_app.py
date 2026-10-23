"""
HopeGive - Donation Management System (desktop app)

How to run:   python donor_app.py
Keep this file in the same folder as donor.py (it uses all the logic from there).
Only Python's built-in tkinter is used - nothing to install.

Logins (from project4.py):
    Admin    ->  admin / admin123
    Donor    ->  donor1 / 123
    Receiver ->  receiver1 / 123
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from donor import (System, UserSystem, check_admin,
                      DonorNotFound, ReceiverNotFound, DonationNotFound)

ERRORS = (ValueError, DonorNotFound, ReceiverNotFound, DonationNotFound)

# ---------------------------------------------------------------- theme
PRIMARY = "#0f766e"
PRIMARY_DARK = "#115e59"
SIDEBAR = "#0b2b28"
SIDEBAR_ACTIVE = "#134e4a"
ACCENT = "#f59e0b"
BG = "#f1f5f9"
CARD = "#ffffff"
BORDER = "#e2e8f0"
TEXT = "#0f172a"
MUTED = "#64748b"
DANGER = "#b91c1c"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_TINY = ("Segoe UI", 8, "bold")
FONT_H1 = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 13, "bold")
FONT_BIG = ("Segoe UI", 22, "bold")

AVATAR_COLORS = ["#0f766e", "#2563eb", "#db2777", "#7c3aed", "#ea580c", "#0891b2", "#65a30d"]


# ---------------------------------------------------------------- helpers
def to_amount(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return 0.0


def money(value):
    if isinstance(value, str):
        value = to_amount(value)
    if value == int(value):
        return "Rs. {:,.0f}".format(value)
    return "Rs. {:,.2f}".format(value)


def money_short(value):
    if value >= 1000000:
        return "Rs. {:.1f}M".format(value / 1000000)
    return money(value)


def initials(name):
    parts = name.split()
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:1].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def avatar_color(text):
    return AVATAR_COLORS[sum(ord(c) for c in text) % len(AVATAR_COLORS)]


def next_id(prefix, existing):
    biggest = 0
    for item in existing:
        if item.upper().startswith(prefix):
            tail = item[len(prefix):].lstrip("-")
            if tail.isdigit():
                biggest = max(biggest, int(tail))
    return "{}-{:03d}".format(prefix, biggest + 1)


def center(win, width, height, parent=None):
    win.update_idletasks()
    if parent is not None:
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2 - 20
    win.geometry("{}x{}+{}+{}".format(width, height, max(x, 0), max(y, 0)))


class FlatButton(tk.Label):
    """A flat coloured button that looks the same on Windows, Mac and Linux."""
    STYLES = {
        "primary": ("#0f766e", "#115e59", "white"),
        "secondary": ("#e2e8f0", "#cbd5e1", "#0f172a"),
        "danger": ("#fee2e2", "#fecaca", "#b91c1c"),
        "ghost": ("#134e4a", "#1b6560", "#ccfbf1"),
    }

    def __init__(self, parent, text, command, style="primary", padx=18, pady=8):
        bg, hover, fg = self.STYLES[style]
        super().__init__(parent, text=text, bg=bg, fg=fg, font=FONT_BOLD,
                         padx=padx, pady=pady, cursor="hand2")
        self._bg, self._hover, self._command = bg, hover, command
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", self._click)

    def _click(self, event):
        if self._command:
            self._command()


def make_entry(parent, show="", variable=None):
    return tk.Entry(parent, font=FONT, relief="flat", bg="white", fg=TEXT,
                    insertbackground=TEXT, highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=PRIMARY,
                    show=show, textvariable=variable)


# ---------------------------------------------------------------- form dialog
class FormDialog(tk.Toplevel):
    """Pop-up form used for add / edit. fields = list of dicts:
       key, label, kind ('entry'|'combo'|'text'), value, readonly, options [(id, label)]"""

    def __init__(self, app, title, subtitle, fields, on_submit, submit_text="Save"):
        super().__init__(app)
        self.configure(bg=CARD)
        self.title(title)
        self.resizable(False, False)
        self.transient(app)
        self.on_submit = on_submit
        self.widgets = {}

        head = tk.Frame(self, bg=PRIMARY)
        head.pack(fill="x")
        tk.Label(head, text=title, bg=PRIMARY, fg="white", font=FONT_H2,
                 anchor="w").pack(fill="x", padx=24, pady=(18, 2))
        tk.Label(head, text=subtitle, bg=PRIMARY, fg="#99f6e4", font=FONT_SMALL,
                 anchor="w").pack(fill="x", padx=24, pady=(0, 16))

        body = tk.Frame(self, bg=CARD)
        body.pack(fill="both", expand=True, padx=24, pady=(8, 0))

        first = None
        for f in fields:
            tk.Label(body, text=f["label"], bg=CARD, fg=MUTED, font=FONT_SMALL,
                     anchor="w").pack(fill="x", pady=(10, 3))
            widget = self._build_field(body, f)
            if first is None and not f.get("readonly"):
                first = widget

        self.error = tk.Label(body, text="", bg=CARD, fg=DANGER, font=FONT_SMALL,
                              anchor="w", justify="left", wraplength=400)
        self.error.pack(fill="x", pady=(12, 0))

        buttons = tk.Frame(self, bg=CARD)
        buttons.pack(fill="x", padx=24, pady=(8, 20))
        FlatButton(buttons, submit_text, self._submit).pack(side="right")
        FlatButton(buttons, "Cancel", self.destroy, style="secondary").pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        center(self, 460, self.winfo_reqheight(), app)
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass
        if first is not None:
            first.focus_set()

    def _build_field(self, body, f):
        kind = f.get("kind", "entry")
        key = f["key"]
        if kind == "combo":
            labels = [label for _, label in f["options"]]
            box = ttk.Combobox(body, values=labels, state="readonly", font=FONT)
            for ident, label in f["options"]:
                if ident == f.get("value"):
                    box.set(label)
            box.pack(fill="x", ipady=4)
            self.widgets[key] = ("combo", box, {label: ident for ident, label in f["options"]})
            return box
        if kind == "text":
            box = tk.Text(body, height=3, font=FONT, relief="flat", wrap="word", bg="white",
                          fg=TEXT, insertbackground=TEXT, highlightthickness=1,
                          highlightbackground=BORDER, highlightcolor=PRIMARY, padx=6, pady=6)
            box.insert("1.0", f.get("value", ""))
            box.pack(fill="x")
            self.widgets[key] = ("text", box, None)
            return box
        entry = make_entry(body)
        entry.insert(0, f.get("value", ""))
        if f.get("readonly"):
            entry.config(state="readonly", readonlybackground="#f1f5f9", fg=MUTED)
        else:
            entry.bind("<Return>", self._submit)
        entry.pack(fill="x", ipady=6)
        self.widgets[key] = ("entry", entry, None)
        return entry

    def _values(self):
        out = {}
        for key, (kind, widget, extra) in self.widgets.items():
            if kind == "text":
                out[key] = widget.get("1.0", "end").strip()
            elif kind == "combo":
                out[key] = extra.get(widget.get(), "")
            else:
                out[key] = widget.get().strip()
        return out

    def _submit(self, event=None):
        try:
            self.on_submit(self._values())
        except ERRORS as e:
            self.error.config(text=str(e))
            return
        self.destroy()


# ---------------------------------------------------------------- login screen
class LoginView(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        self.mode = tk.StringVar(value="user")

        # left brand panel
        left = tk.Frame(self, bg=PRIMARY_DARK, width=430)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="\u2665", bg=PRIMARY_DARK, fg=ACCENT,
                 font=("Segoe UI", 44)).pack(anchor="w", padx=48, pady=(90, 0))
        tk.Label(left, text="HopeGive", bg=PRIMARY_DARK, fg="white",
                 font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=48)
        tk.Label(left, text="Connecting generous donors with\npeople who need a helping hand.",
                 bg=PRIMARY_DARK, fg="#99f6e4", font=("Segoe UI", 12),
                 justify="left").pack(anchor="w", padx=48, pady=(8, 40))
        for line in ("Track every donation in one place",
                     "Manage donors and receivers easily",
                     "Clear, transparent records"):
            row = tk.Frame(left, bg=PRIMARY_DARK)
            row.pack(anchor="w", padx=48, pady=5)
            tk.Label(row, text="\u2713", bg=PRIMARY_DARK, fg=ACCENT, font=FONT_BOLD).pack(side="left")
            tk.Label(row, text="  " + line, bg=PRIMARY_DARK, fg="white", font=FONT).pack(side="left")
        tk.Label(left, text="Donation Management System", bg=PRIMARY_DARK, fg="#5eead4",
                 font=FONT_SMALL).pack(side="bottom", anchor="w", padx=48, pady=28)

        # right login card
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        card = tk.Frame(right, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=400)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", padx=34, pady=32)

        tk.Label(inner, text="Welcome back", bg=CARD, fg=TEXT, font=FONT_H1, anchor="w").pack(fill="x")
        tk.Label(inner, text="Sign in to continue to your account", bg=CARD, fg=MUTED,
                 font=FONT, anchor="w").pack(fill="x", pady=(2, 18))

        # segmented switch
        seg = tk.Frame(inner, bg="#f1f5f9")
        seg.pack(fill="x")
        self.seg_buttons = {}
        for key, text in (("user", "Donor / Receiver"), ("admin", "Administrator")):
            b = tk.Label(seg, text=text, font=FONT_BOLD, pady=8, cursor="hand2")
            b.pack(side="left", fill="x", expand=True, padx=3, pady=3)
            b.bind("<Button-1>", lambda e, k=key: self.set_mode(k))
            self.seg_buttons[key] = b
        self.set_mode("user")

        tk.Label(inner, text="Username", bg=CARD, fg=MUTED, font=FONT_SMALL,
                 anchor="w").pack(fill="x", pady=(16, 3))
        self.user_var = tk.StringVar()
        self.user_entry = make_entry(inner, variable=self.user_var)
        self.user_entry.pack(fill="x", ipady=7)

        tk.Label(inner, text="Password", bg=CARD, fg=MUTED, font=FONT_SMALL,
                 anchor="w").pack(fill="x", pady=(12, 3))
        self.pass_var = tk.StringVar()
        self.pass_entry = make_entry(inner, show="\u2022", variable=self.pass_var)
        self.pass_entry.pack(fill="x", ipady=7)

        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(inner, text="Show password", variable=self.show_var, bg=CARD,
                       fg=MUTED, activebackground=CARD, selectcolor="white", font=FONT_SMALL,
                       command=self.toggle_password, anchor="w", bd=0,
                       highlightthickness=0).pack(fill="x", pady=(8, 0))

        self.error = tk.Label(inner, text="", bg=CARD, fg=DANGER, font=FONT_SMALL, anchor="w")
        self.error.pack(fill="x", pady=(8, 0))

        FlatButton(inner, "Sign In", self.submit, pady=11).pack(fill="x", pady=(8, 0))

        for entry in (self.user_entry, self.pass_entry):
            entry.bind("<Return>", self.submit)
        self.user_entry.focus_set()

    def set_mode(self, mode):
        self.mode.set(mode)
        for key, button in self.seg_buttons.items():
            if key == mode:
                button.config(bg="white", fg=PRIMARY_DARK)
            else:
                button.config(bg="#f1f5f9", fg=MUTED)

    def toggle_password(self):
        self.pass_entry.config(show="" if self.show_var.get() else "\u2022")

    def submit(self, event=None):
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        if not username or not password:
            self.error.config(text="Please enter your username and password.")
            return
        if self.mode.get() == "admin":
            role = "admin" if check_admin(username, password) else None
        else:
            role = self.app.users.check_login(username, password)
        if role is None:
            self.error.config(text="Wrong username or password.")
            self.pass_var.set("")
            return
        self.app.start_session(username, role)


# ---------------------------------------------------------------- dashboard
class DashboardPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        stats = tk.Frame(self, bg=BG)
        stats.pack(fill="x")
        for c in range(4):
            stats.columnconfigure(c, weight=1, uniform="stat")
        self.cards = {}
        defs = (("raised", "Total raised", PRIMARY), ("donations", "Donations", ACCENT),
                ("donors", "Donors", "#2563eb"), ("receivers", "Receivers", "#db2777"))
        for i, (key, label, color) in enumerate(defs):
            card = tk.Frame(stats, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=label.upper(), bg=CARD, fg=MUTED, font=FONT_TINY,
                     anchor="w").pack(fill="x", padx=18, pady=(14, 0))
            value = tk.Label(card, text="0", bg=CARD, fg=TEXT, font=FONT_BIG, anchor="w")
            value.pack(fill="x", padx=18)
            note = tk.Label(card, text="", bg=CARD, fg=MUTED, font=FONT_SMALL, anchor="w")
            note.pack(fill="x", padx=18, pady=(0, 14))
            self.cards[key] = (value, note)

        lower = tk.Frame(self, bg=BG)
        lower.pack(fill="both", expand=True, pady=(16, 0))
        lower.rowconfigure(0, weight=1)
        lower.columnconfigure(0, weight=3, uniform="low")
        lower.columnconfigure(1, weight=2, uniform="low")
        self.recent = self._panel(lower, "Recent donations", "The latest contributions", 0)
        self.top = self._panel(lower, "Top donors", "Ranked by total amount given", 1)

    def _panel(self, parent, title, subtitle, column):
        card = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0 if column == 0 else 8, 0 if column == 1 else 8))
        tk.Label(card, text=title, bg=CARD, fg=TEXT, font=FONT_H2,
                 anchor="w").pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(card, text=subtitle, bg=CARD, fg=MUTED, font=FONT_SMALL,
                 anchor="w").pack(fill="x", padx=20, pady=(0, 8))
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        return body

    @staticmethod
    def _clear(frame):
        for child in frame.winfo_children():
            child.destroy()

    @staticmethod
    def _empty(frame, text):
        tk.Label(frame, text=text, bg=CARD, fg=MUTED, font=FONT).pack(pady=40)

    def refresh(self):
        s = self.app.system
        total = s.total_amount()
        count = len(s.donations)
        self.cards["raised"][0].config(text=money_short(total))
        self.cards["raised"][1].config(text=money(total) + " in total")
        self.cards["donations"][0].config(text=str(count))
        average = money(total / count) if count else "No donations yet"
        self.cards["donations"][1].config(text=("Average " + average) if count else average)
        self.cards["donors"][0].config(text=str(len(s.donors)))
        self.cards["donors"][1].config(text="Registered donors")
        self.cards["receivers"][0].config(text=str(len(s.receivers)))
        self.cards["receivers"][1].config(text="People being supported")

        # recent donations
        self._clear(self.recent)
        if not s.donations:
            self._empty(self.recent, "No donations recorded yet.")
        for i, don in enumerate(reversed(s.donations[-6:])):
            if i:
                tk.Frame(self.recent, bg=BORDER, height=1).pack(fill="x")
            row = tk.Frame(self.recent, bg=CARD)
            row.pack(fill="x", pady=7)
            name = s.donor_name(don.donor_id)
            tk.Label(row, text=initials(name), bg=avatar_color(don.donor_id), fg="white",
                     font=FONT_BOLD, width=4, pady=6).pack(side="left")
            text = tk.Frame(row, bg=CARD)
            text.pack(side="left", padx=12)
            tk.Label(text, text=name, bg=CARD, fg=TEXT, font=FONT_BOLD, anchor="w").pack(fill="x")
            tk.Label(text, text="to " + s.receiver_name(don.receiver_id), bg=CARD, fg=MUTED,
                     font=FONT_SMALL, anchor="w").pack(fill="x")
            tk.Label(row, text=money(don.amount), bg=CARD, fg=PRIMARY,
                     font=FONT_BOLD).pack(side="right")

        # top donors
        self._clear(self.top)
        totals = {}
        for don in s.donations:
            totals[don.donor_id] = totals.get(don.donor_id, 0.0) + to_amount(don.amount)
        ranking = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]
        if not ranking:
            self._empty(self.top, "Top donors will appear here.")
        biggest = ranking[0][1] if ranking else 1
        for donor_id, amount in ranking:
            row = tk.Frame(self.top, bg=CARD)
            row.pack(fill="x", pady=7)
            line = tk.Frame(row, bg=CARD)
            line.pack(fill="x")
            tk.Label(line, text=s.donor_name(donor_id), bg=CARD, fg=TEXT, font=FONT_BOLD,
                     anchor="w").pack(side="left")
            tk.Label(line, text=money(amount), bg=CARD, fg=MUTED, font=FONT_SMALL).pack(side="right")
            track = tk.Frame(row, bg="#e2e8f0", height=8)
            track.pack(fill="x", pady=(4, 0))
            fill = tk.Frame(track, bg=avatar_color(donor_id), height=8)
            fill.place(x=0, y=0, relheight=1, relwidth=max(amount / biggest, 0.03) if biggest else 0.03)


# ---------------------------------------------------------------- table pages
class TablePage(tk.Frame):
    columns = ()          # (key, heading, width, anchor)
    noun = "record"

    def __init__(self, parent, app, can_edit):
        super().__init__(parent, bg=BG)
        self.app = app
        self.can_edit = can_edit
        self.row_ids = {}
        self.sort_col = 0
        self.sort_reverse = False

        card = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="both", expand=True)

        bar = tk.Frame(card, bg=CARD)
        bar.pack(fill="x", padx=18, pady=(16, 12))
        tk.Label(bar, text="Search", bg=CARD, fg=MUTED, font=FONT_SMALL).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh())
        search = make_entry(bar, variable=self.search_var)
        search.pack(side="left", ipady=6, ipadx=4)
        search.config(width=32)

        if can_edit:
            FlatButton(bar, "Delete", self.delete_selected, style="danger").pack(side="right")
            FlatButton(bar, "Edit", self.edit_selected, style="secondary").pack(side="right", padx=8)
            FlatButton(bar, "+ Add " + self.noun, self.add_new).pack(side="right")

        wrap = tk.Frame(card, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=1)
        keys = [c[0] for c in self.columns]
        self.tree = ttk.Treeview(wrap, columns=keys, show="headings", selectmode="browse")
        for i, (key, heading, width, anchor) in enumerate(self.columns):
            self.tree.heading(key, text=heading, anchor="w", command=lambda n=i: self.sort_by(n))
            self.tree.column(key, width=width, anchor=anchor, minwidth=70, stretch=True)
        self.tree.tag_configure("even", background="white")
        self.tree.tag_configure("odd", background="#f8fafc")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        if can_edit:
            self.tree.bind("<Double-1>", self.edit_selected)

        self.empty = tk.Label(wrap, text="", bg=CARD, fg=MUTED, font=FONT, justify="center")
        self.footer = tk.Label(card, text="", bg=CARD, fg=MUTED, font=FONT_SMALL, anchor="w")
        self.footer.pack(fill="x", padx=18, pady=10)

    # --- to be provided by each page
    def rows(self):
        return []

    def form_spec(self, item_id):
        raise NotImplementedError

    def submit(self, item_id, values):
        raise NotImplementedError

    def remove(self, item_id):
        raise NotImplementedError

    # --- shared behaviour
    @staticmethod
    def _sort_value(text):
        cleaned = str(text).replace("Rs.", "").replace(",", "").strip()
        try:
            return (0, float(cleaned), "")
        except ValueError:
            return (1, 0.0, str(text).lower())

    def sort_by(self, index):
        if self.sort_col == index:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col, self.sort_reverse = index, False
        self.refresh()

    def refresh(self):
        term = self.search_var.get().strip().lower()
        all_rows = self.rows()
        rows = all_rows
        if term:
            rows = [r for r in all_rows if any(term in str(v).lower() for v in r[1])]
        rows = sorted(rows, key=lambda r: self._sort_value(r[1][self.sort_col]),
                      reverse=self.sort_reverse)

        self.tree.delete(*self.tree.get_children())
        self.row_ids = {}
        for i, (record_id, values) in enumerate(rows):
            iid = str(i)
            self.row_ids[iid] = record_id
            self.tree.insert("", "end", iid=iid, values=values, tags=("odd" if i % 2 else "even",))

        if rows:
            self.empty.place_forget()
        else:
            if term:
                text = "No results for \u201c" + self.search_var.get().strip() + "\u201d"
            elif self.can_edit:
                text = "No {}s yet.\nClick \u201c+ Add {}\u201d to create the first one.".format(self.noun.lower(), self.noun.lower())
            else:
                text = "Nothing to show yet."
            self.empty.config(text=text)
            self.empty.place(relx=0.5, rely=0.4, anchor="center")
        self.footer.config(text="Showing {} of {} {}s".format(len(rows), len(all_rows), self.noun.lower()))

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self.row_ids.get(selection[0])

    def add_new(self):
        self.open_form(None)

    def edit_selected(self, event=None):
        record_id = self.selected_id()
        if record_id is None:
            self.app.toast("Select a row first", "warn")
            return
        self.open_form(record_id)

    def open_form(self, item_id):
        try:
            title, subtitle, fields = self.form_spec(item_id)
        except ValueError as e:
            self.app.toast(str(e), "warn")
            return

        def on_submit(values):
            self.submit(item_id, values)
            self.app.refresh_all()
            self.app.toast(self.noun + (" updated" if item_id else " added"))

        FormDialog(self.app, title, subtitle, fields, on_submit,
                   "Save changes" if item_id else "Add " + self.noun.lower())

    def delete_selected(self):
        record_id = self.selected_id()
        if record_id is None:
            self.app.toast("Select a row first", "warn")
            return
        if not messagebox.askyesno("Delete " + self.noun.lower(),
                                   "Delete {} {}?\nThis cannot be undone.".format(self.noun.lower(), record_id),
                                   parent=self.app):
            return
        try:
            self.remove(record_id)
        except ERRORS as e:
            messagebox.showwarning("Cannot delete", str(e), parent=self.app)
            return
        self.app.refresh_all()
        self.app.toast(self.noun + " deleted")


class DonorsPage(TablePage):
    noun = "Donor"
    columns = (("id", "Donor ID", 100, "w"), ("name", "Name", 170, "w"), ("cnic", "CNIC", 150, "w"),
               ("phone", "Phone", 130, "w"), ("address", "Address", 260, "w"))

    def rows(self):
        return [(d.donor_id, (d.donor_id, d.name, d.cnic, d.phone, d.address))
                for d in self.app.system.donors]

    def form_spec(self, item_id):
        s = self.app.system
        if item_id is None:
            fields = [
                {"key": "donor_id", "label": "Donor ID", "value": next_id("DNR", [d.donor_id for d in s.donors])},
                {"key": "name", "label": "Full name"},
                {"key": "cnic", "label": "CNIC (13 digits)"},
                {"key": "phone", "label": "Phone"},
                {"key": "address", "label": "Address"},
            ]
            return "Add donor", "Register a new donor", fields
        d = s.find_donor(item_id)
        fields = [
            {"key": "donor_id", "label": "Donor ID", "value": d.donor_id, "readonly": True},
            {"key": "name", "label": "Full name", "value": d.name},
            {"key": "cnic", "label": "CNIC", "value": d.cnic, "readonly": True},
            {"key": "phone", "label": "Phone", "value": d.phone},
            {"key": "address", "label": "Address", "value": d.address},
        ]
        return "Edit donor", d.donor_id + " \u2022 " + d.name, fields

    def submit(self, item_id, v):
        s = self.app.system
        if item_id is None:
            s.add_donor_record(v["cnic"], v["name"], v["address"], v["phone"], v["donor_id"])
        else:
            s.update_donor_record(item_id, name=v["name"], address=v["address"], phone=v["phone"])

    def remove(self, item_id):
        self.app.system.delete_donor_record(item_id)


class ReceiversPage(TablePage):
    noun = "Receiver"
    columns = (("id", "Receiver ID", 100, "w"), ("name", "Name", 150, "w"), ("cnic", "CNIC", 140, "w"),
               ("phone", "Phone", 120, "w"), ("address", "Address", 170, "w"), ("reason", "Reason", 200, "w"))

    def rows(self):
        return [(r.receiver_id, (r.receiver_id, r.name, r.cnic, r.phone, r.address, r.reason))
                for r in self.app.system.receivers]

    def form_spec(self, item_id):
        s = self.app.system
        if item_id is None:
            fields = [
                {"key": "receiver_id", "label": "Receiver ID", "value": next_id("RCV", [r.receiver_id for r in s.receivers])},
                {"key": "name", "label": "Full name"},
                {"key": "cnic", "label": "CNIC (13 digits)"},
                {"key": "phone", "label": "Phone"},
                {"key": "address", "label": "Address"},
                {"key": "reason", "label": "Reason for support", "kind": "text"},
            ]
            return "Add receiver", "Register a person in need", fields
        r = s.find_receiver(item_id)
        fields = [
            {"key": "receiver_id", "label": "Receiver ID", "value": r.receiver_id, "readonly": True},
            {"key": "name", "label": "Full name", "value": r.name},
            {"key": "cnic", "label": "CNIC", "value": r.cnic, "readonly": True},
            {"key": "phone", "label": "Phone", "value": r.phone},
            {"key": "address", "label": "Address", "value": r.address},
            {"key": "reason", "label": "Reason for support", "kind": "text", "value": r.reason},
        ]
        return "Edit receiver", r.receiver_id + " \u2022 " + r.name, fields

    def submit(self, item_id, v):
        s = self.app.system
        if item_id is None:
            s.add_receiver_record(v["cnic"], v["name"], v["address"], v["phone"], v["receiver_id"], v["reason"])
        else:
            s.update_receiver_record(item_id, name=v["name"], address=v["address"],
                                     phone=v["phone"], reason=v["reason"])

    def remove(self, item_id):
        self.app.system.delete_receiver_record(item_id)


class DonationsPage(TablePage):
    noun = "Donation"
    columns = (("id", "Donation ID", 110, "w"), ("donor", "Donor", 220, "w"),
               ("receiver", "Receiver", 220, "w"), ("amount", "Amount", 130, "e"))

    def rows(self):
        s = self.app.system
        return [(d.donation_id, (d.donation_id,
                                 "{} ({})".format(s.donor_name(d.donor_id), d.donor_id),
                                 "{} ({})".format(s.receiver_name(d.receiver_id), d.receiver_id),
                                 money(d.amount)))
                for d in s.donations]

    def form_spec(self, item_id):
        s = self.app.system
        if not s.donors or not s.receivers:
            raise ValueError("Add at least one donor and one receiver first")
        donors = [(d.donor_id, "{} ({})".format(d.name, d.donor_id)) for d in s.donors]
        receivers = [(r.receiver_id, "{} ({})".format(r.name, r.receiver_id)) for r in s.receivers]
        if item_id is None:
            fields = [
                {"key": "donation_id", "label": "Donation ID",
                 "value": next_id("DON", [d.donation_id for d in s.donations])},
                {"key": "donor_id", "label": "Donor", "kind": "combo", "options": donors},
                {"key": "receiver_id", "label": "Receiver", "kind": "combo", "options": receivers},
                {"key": "amount", "label": "Amount (Rs.)"},
            ]
            return "Record donation", "Log a new contribution", fields
        d = s.find_donation(item_id)
        fields = [
            {"key": "donation_id", "label": "Donation ID", "value": d.donation_id, "readonly": True},
            {"key": "donor_id", "label": "Donor", "kind": "combo", "options": donors, "value": d.donor_id},
            {"key": "receiver_id", "label": "Receiver", "kind": "combo", "options": receivers, "value": d.receiver_id},
            {"key": "amount", "label": "Amount (Rs.)", "value": d.amount},
        ]
        return "Edit donation", d.donation_id, fields

    def submit(self, item_id, v):
        s = self.app.system
        if item_id is None:
            s.add_donation_record(v["donation_id"], v["donor_id"], v["receiver_id"], v["amount"])
        else:
            s.update_donation_record(item_id, donor_id=v["donor_id"],
                                     receiver_id=v["receiver_id"], amount=v["amount"])

    def remove(self, item_id):
        self.app.system.delete_donation_record(item_id)


# ---------------------------------------------------------------- main screen
class NavItem(tk.Frame):
    def __init__(self, parent, text, command):
        super().__init__(parent, bg=SIDEBAR, cursor="hand2")
        self.command = command
        self.active = False
        self.strip = tk.Frame(self, bg=SIDEBAR, width=4)
        self.strip.pack(side="left", fill="y")
        self.label = tk.Label(self, text=text, bg=SIDEBAR, fg="#99f6e4", font=FONT_BOLD,
                              anchor="w", padx=20, pady=11)
        self.label.pack(side="left", fill="x", expand=True)
        for widget in (self, self.label, self.strip):
            widget.bind("<Button-1>", lambda e: self.command())
            widget.bind("<Enter>", lambda e: self._paint(True))
            widget.bind("<Leave>", lambda e: self._paint(False))

    def _paint(self, hover):
        bg = SIDEBAR_ACTIVE if (self.active or hover) else SIDEBAR
        self.config(bg=bg)
        self.label.config(bg=bg, fg="white" if self.active else "#99f6e4")
        self.strip.config(bg=ACCENT if self.active else bg)

    def set_active(self, active):
        self.active = active
        self._paint(False)


class MainView(tk.Frame):
    ROLE_PAGES = {
        "admin": ("dashboard", "donors", "receivers", "donations"),
        "donor": ("dashboard", "donations", "receivers"),
        "receiver": ("dashboard", "donations", "donors"),
    }
    PAGE_INFO = {
        "dashboard": ("Dashboard", "Overview"),
        "donors": ("Donors", "People who give generously"),
        "receivers": ("Receivers", "People and families receiving support"),
        "donations": ("Donations", "Every contribution, recorded"),
    }

    def __init__(self, app, username, role):
        super().__init__(app, bg=BG)
        self.app = app
        self.role = role
        self.username = username
        self.toast_job = None
        can_edit = role == "admin"

        # sidebar
        side = tk.Frame(self, bg=SIDEBAR, width=240)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        brand = tk.Frame(side, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(26, 28))
        tk.Label(brand, text="\u2665", bg=SIDEBAR, fg=ACCENT, font=("Segoe UI", 22)).pack(side="left")
        names = tk.Frame(brand, bg=SIDEBAR)
        names.pack(side="left", padx=10)
        tk.Label(names, text="HopeGive", bg=SIDEBAR, fg="white", font=("Segoe UI", 15, "bold"),
                 anchor="w").pack(fill="x")
        tk.Label(names, text="Donation Management", bg=SIDEBAR, fg="#5eead4", font=FONT_SMALL,
                 anchor="w").pack(fill="x")

        self.nav = {}
        for key in self.ROLE_PAGES[role]:
            item = NavItem(side, self.PAGE_INFO[key][0], lambda k=key: self.show(k))
            item.pack(fill="x")
            self.nav[key] = item

        user_box = tk.Frame(side, bg=SIDEBAR)
        user_box.pack(side="bottom", fill="x", padx=20, pady=20)
        FlatButton(user_box, "Log out", app.show_login, style="ghost").pack(fill="x", pady=(14, 0))
        who = tk.Frame(user_box, bg=SIDEBAR)
        who.pack(fill="x")
        tk.Label(who, text=initials(username), bg=avatar_color(username), fg="white", font=FONT_BOLD,
                 width=4, pady=6).pack(side="left")
        info = tk.Frame(who, bg=SIDEBAR)
        info.pack(side="left", padx=10)
        tk.Label(info, text=username, bg=SIDEBAR, fg="white", font=FONT_BOLD, anchor="w").pack(fill="x")
        tk.Label(info, text=role.capitalize(), bg=SIDEBAR, fg="#5eead4", font=FONT_SMALL,
                 anchor="w").pack(fill="x")

        # content
        content = tk.Frame(self, bg=BG)
        content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(content, bg=BG)
        header.pack(fill="x", padx=32, pady=(26, 16))
        titles = tk.Frame(header, bg=BG)
        titles.pack(side="left")
        self.title_label = tk.Label(titles, text="", bg=BG, fg=TEXT, font=FONT_H1, anchor="w")
        self.title_label.pack(fill="x")
        self.sub_label = tk.Label(titles, text="", bg=BG, fg=MUTED, font=FONT, anchor="w")
        self.sub_label.pack(fill="x")
        tk.Label(header, text=role.upper(), bg="#ccfbf1", fg=PRIMARY_DARK, font=FONT_TINY,
                 padx=12, pady=5).pack(side="right")

        body = tk.Frame(content, bg=BG)
        body.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)

        all_pages = {
            "dashboard": DashboardPage(body, app),
            "donors": DonorsPage(body, app, can_edit),
            "receivers": ReceiversPage(body, app, can_edit),
            "donations": DonationsPage(body, app, can_edit),
        }
        self.pages = {key: all_pages[key] for key in self.ROLE_PAGES[role]}
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.toast_label = tk.Label(content, text="", font=FONT_BOLD, padx=18, pady=10)
        self.show("dashboard")

    def greeting(self):
        hour = datetime.now().hour
        part = "morning" if hour < 12 else ("afternoon" if hour < 18 else "evening")
        return "Good {}, {}. Here is how things look today.".format(part, self.username)

    def show(self, key):
        for name, item in self.nav.items():
            item.set_active(name == key)
        title, subtitle = self.PAGE_INFO[key]
        self.title_label.config(text=title)
        self.sub_label.config(text=self.greeting() if key == "dashboard" else subtitle)
        self.pages[key].refresh()
        self.pages[key].tkraise()

    def refresh_all(self):
        for page in self.pages.values():
            page.refresh()

    def show_toast(self, message, kind="ok"):
        colors = {"ok": ("#065f46", "#d1fae5"), "warn": ("#92400e", "#fef3c7")}
        fg, bg = colors.get(kind, colors["ok"])
        self.toast_label.config(text=message, fg=fg, bg=bg)
        self.toast_label.place(relx=1.0, rely=1.0, x=-28, y=-22, anchor="se")
        self.toast_label.lift()
        if self.toast_job:
            self.after_cancel(self.toast_job)
        self.toast_job = self.after(2800, self.toast_label.place_forget)


# ---------------------------------------------------------------- application
class DonorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HopeGive \u2013 Donation Management System")
        self.configure(bg=BG)
        self.minsize(1000, 640)
        center(self, 1200, 720)

        self.system = System()
        self.users = UserSystem(self.system)
        self.view = None
        self.setup_styles()
        self.show_login()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        style.configure("Treeview", background="white", fieldbackground="white", foreground=TEXT,
                        rowheight=36, borderwidth=0, font=FONT)
        style.configure("Treeview.Heading", background="#f8fafc", foreground=MUTED, font=FONT_BOLD,
                        relief="flat", padding=(10, 9), borderwidth=0)
        style.map("Treeview", background=[("selected", "#ccfbf1")], foreground=[("selected", TEXT)])
        style.map("Treeview.Heading", background=[("active", "#f1f5f9")])
        style.configure("Vertical.TScrollbar", background="#cbd5e1", troughcolor="white",
                        bordercolor="white", arrowcolor="white", relief="flat")
        style.configure("TCombobox", padding=4)
        self.option_add("*TCombobox*Listbox.font", FONT)

    def _set_view(self, view):
        if self.view is not None:
            self.view.destroy()
        self.view = view
        self.view.pack(fill="both", expand=True)

    def show_login(self):
        self._set_view(LoginView(self))

    def start_session(self, username, role):
        self._set_view(MainView(self, username, role))

    def refresh_all(self):
        if isinstance(self.view, MainView):
            self.view.refresh_all()

    def toast(self, message, kind="ok"):
        if isinstance(self.view, MainView):
            self.view.show_toast(message, kind)


if __name__ == "__main__":
    DonorApp().mainloop()
