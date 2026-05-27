"""
OSINT Engagement Checklist
─────────────────────────
A professional desktop GUI for managing authorised OSINT engagements.

Requirements:
    pip install customtkinter

Run:
    python osint_checklist.py

Data is saved to: osint_saves/ in the same directory as this script.
"""

import json
import os
import sys
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    print("Missing dependency. Run:  pip install customtkinter")
    sys.exit(1)

# ─── Theme ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG        = "#0d0f14"
BG2       = "#13161d"
BG3       = "#1a1e28"
SURFACE   = "#1e2330"
SURFACE2  = "#252b3b"
BORDER    = "#2e3548"
ACCENT    = "#00c8e0"
ACCENT2   = "#7b5ea7"
WARN      = "#ffa94d"
GREEN     = "#3ddc97"
RED       = "#ff6b6b"
BLUE      = "#4dabf7"
TEXT      = "#e8eaf0"
TEXT2     = "#8b92a8"
TEXT3     = "#545c73"
MONO      = ("JetBrains Mono", "Consolas", "Courier New")

# ─── Data ─────────────────────────────────────────────────────────────────────
PHASES = [
    {
        "id": "scope",
        "title": "Phase 0 — Scope & Authorisation",
        "subtitle": "Legal groundwork — complete before any activity",
        "color": "#7b5ea7",
        "items": [
            {"name": "Obtain written authorisation from client",
             "hint": "Letter of engagement or signed scope document", "type": "passive"},
            {"name": "Define target scope — domains, IPs, personnel",
             "hint": "List all in-scope assets explicitly in writing", "type": "passive"},
            {"name": "Confirm legal jurisdiction & applicable laws",
             "hint": "GDPR, Computer Misuse Act 1990, CFAA etc.", "type": "passive"},
            {"name": "Agree on rules of engagement & reporting format",
             "hint": "Deliverables, timeline, escalation path, confidentiality", "type": "passive"},
            {"name": "Set up isolated OSINT workstation / VM",
             "hint": "Separate browser profile, VPN, clean dedicated toolset", "type": "passive"},
        ]
    },
    {
        "id": "passive",
        "title": "Phase 1 — Passive Reconnaissance",
        "subtitle": "No direct interaction with target systems",
        "color": "#4dabf7",
        "items": [
            {"name": "WHOIS lookup on all target domains",
             "hint": "whois.domaintools.com, who.is, ICANN lookup", "type": "passive"},
            {"name": "DNS enumeration — A, MX, TXT, NS, CNAME records",
             "hint": "MXToolbox, dig, dnsx, nslookup", "type": "passive"},
            {"name": "Reverse WHOIS — find related domains by registrant",
             "hint": "ViewDNS.info, DOMARINfo — expand target org footprint", "type": "passive"},
            {"name": "Subdomain discovery via passive sources",
             "hint": "crt.sh, SecurityTrails, Subfinder, Amass (passive mode)", "type": "passive"},
            {"name": "Certificate Transparency log review",
             "hint": "crt.sh, Censys.io — reveals hidden / internal subdomains", "type": "passive"},
            {"name": "Google dorking on target domain",
             "hint": "site: inurl: filetype: intitle: — document exposed assets", "type": "passive"},
            {"name": "Shodan / Censys / FOFA indexed data review",
             "hint": "Review archived banners only — no direct scanning yet", "type": "passive"},
            {"name": "Wayback Machine / Archive.org review",
             "hint": "Historical pages, old endpoints, removed sensitive content", "type": "passive"},
            {"name": "ASN & IP range enumeration",
             "hint": "BGP.he.net, ASNLookup — find all owned IP blocks / netblocks", "type": "passive"},
            {"name": "Email address pattern discovery",
             "hint": "Hunter.io, Phonebook.cz, emailformat.com", "type": "passive"},
            {"name": "Breach & credential data check",
             "hint": "HaveIBeenPwned API, DeHashed — authorised use only", "type": "passive"},
            {"name": "Paste site monitoring",
             "hint": "Pastebin, Ghostbin — leaked keys, credentials, internal code", "type": "passive"},
        ]
    },
    {
        "id": "tech",
        "title": "Phase 2 — Technology Footprint",
        "subtitle": "Identify stack, services, and exposure",
        "color": "#3ddc97",
        "items": [
            {"name": "Identify web technologies & frameworks",
             "hint": "Wappalyzer, BuiltWith, WhatRuns browser extension", "type": "passive"},
            {"name": "CMS / platform detection & version",
             "hint": "WordPress, Joomla, Drupal — check for known CVEs", "type": "passive"},
            {"name": "JavaScript file analysis for endpoints",
             "hint": "LinkFinder, getallurls (gau) — extract hidden API paths", "type": "passive"},
            {"name": "CDN & hosting provider identification",
             "hint": "Security implications of shared / third-party infra", "type": "passive"},
            {"name": "Cloud storage bucket enumeration",
             "hint": "S3Scanner, GrayhatWarfare — public S3 / GCS / Azure blobs", "type": "passive"},
            {"name": "Email security posture assessment",
             "hint": "SPF, DKIM, DMARC — MXToolbox, DMARC Analyser", "type": "passive"},
            {"name": "TLS / SSL certificate deep analysis",
             "hint": "Qualys SSL Labs — cipher suites, expiry dates, chain issues", "type": "passive"},
            {"name": "Open ports & services from Shodan data",
             "hint": "Review without active scanning — document known exposures", "type": "passive"},
        ]
    },
    {
        "id": "people",
        "title": "Phase 3 — People & Social Footprint",
        "subtitle": "OSINT on personnel, accounts, and leaks",
        "color": "#ff6b6b",
        "items": [
            {"name": "Key personnel identification",
             "hint": "LinkedIn, company website, press releases, Companies House", "type": "passive"},
            {"name": "Executive & IT staff profiling",
             "hint": "Job titles, tenure, skills listed — infer internal tech stack", "type": "passive"},
            {"name": "LinkedIn company page analysis",
             "hint": "Employee count, tech skills endorsed, hiring patterns", "type": "passive"},
            {"name": "Job posting analysis for technology clues",
             "hint": "Indeed, LinkedIn Jobs — what tools are they actively hiring for?", "type": "passive"},
            {"name": "Social media footprint audit",
             "hint": "Twitter/X, GitHub, Reddit — employee accounts, code mentions", "type": "passive"},
            {"name": "GitHub / GitLab organisation scan",
             "hint": "Public repos, commit history, truffleHog for leaked secrets", "type": "passive"},
            {"name": "Dark web / forum mention check",
             "hint": "Mention of company, credentials, discussions — if in scope", "type": "passive"},
        ]
    },
    {
        "id": "active",
        "title": "Phase 4 — Active Reconnaissance",
        "subtitle": "⚠  Direct interaction — confirm written authorisation first",
        "color": "#ffa94d",
        "items": [
            {"name": "Port scan all in-scope IP ranges",
             "hint": "Nmap — TCP SYN scan with service & version detection (-sV)", "type": "active"},
            {"name": "Subdomain brute-force enumeration",
             "hint": "Amass (active), Gobuster DNS, ffuf — confirm live hosts only", "type": "active"},
            {"name": "Web directory & file enumeration",
             "hint": "Gobuster, ffuf, dirsearch — common paths, backups, config files", "type": "active"},
            {"name": "Web crawling & spidering",
             "hint": "GoSpider, Hakrawler, katana — map full application surface", "type": "active"},
            {"name": "Screenshot all discovered web assets",
             "hint": "Gowitness, Aquatone — visual inventory of attack surface", "type": "active"},
            {"name": "HTTP security header analysis",
             "hint": "Security headers, server banners, X-Powered-By disclosure", "type": "active"},
            {"name": "WAF / CDN detection",
             "hint": "wafw00f — identify and document protective technologies", "type": "active"},
            {"name": "Reverse DNS & PTR record lookup on found IPs",
             "hint": "Geolocation, abuse contacts, further domain correlation", "type": "active"},
        ]
    },
    {
        "id": "report",
        "title": "Phase 5 — Analysis & Reporting",
        "subtitle": "Structure, evidence, and secure delivery",
        "color": "#00c8e0",
        "items": [
            {"name": "Collate all findings into structured notes",
             "hint": "Markdown, Obsidian, CherryTree, or Notion — dated entries", "type": "passive"},
            {"name": "Create full asset inventory",
             "hint": "All domains, IPs, services, technologies — with metadata", "type": "passive"},
            {"name": "Identify and prioritise highest-risk exposures",
             "hint": "Credentials, exposed services, misconfigs — risk-ranked list", "type": "passive"},
            {"name": "Map attack surface visually",
             "hint": "Network / relationship diagram of all discovered assets", "type": "passive"},
            {"name": "Document all tools and queries used",
             "hint": "Methodology section — reproducibility and transparency", "type": "passive"},
            {"name": "Capture timestamped screenshot evidence",
             "hint": "Organised by category — all findings must have proof", "type": "passive"},
            {"name": "Write executive summary (non-technical)",
             "hint": "Business risk framing for management / stakeholders", "type": "passive"},
            {"name": "Write full technical report",
             "hint": "Asset inventory, exposures, risk ratings, recommendations", "type": "passive"},
            {"name": "Securely deliver report to client",
             "hint": "Encrypted PDF or secure portal — never plain email", "type": "passive"},
            {"name": "Destroy or return sensitive data post-engagement",
             "hint": "Follow agreed data retention and destruction policy", "type": "passive"},
        ]
    },
]

SAVE_DIR = Path(__file__).parent / "osint_saves"


# ─── Helpers ──────────────────────────────────────────────────────────────────
def all_item_keys():
    return [(p["id"], i) for p in PHASES for i in range(len(p["items"]))]

def phase_by_id(pid):
    return next((p for p in PHASES if p["id"] == pid), None)


# ─── Note Dialog ──────────────────────────────────────────────────────────────
class NoteDialog(ctk.CTkToplevel):
    def __init__(self, parent, item_name, existing_note=""):
        super().__init__(parent)
        self.title("Finding Note")
        self.geometry("500x300")
        self.configure(fg_color=BG2)
        self.resizable(False, False)
        self.result = None
        self.grab_set()

        ctk.CTkLabel(self, text=item_name, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT, wraplength=460).pack(padx=20, pady=(18, 6), anchor="w")
        ctk.CTkLabel(self, text="Add your findings / notes for this check:",
                     font=ctk.CTkFont(size=11), text_color=TEXT2).pack(padx=20, anchor="w")

        self.text = ctk.CTkTextbox(self, height=140, fg_color=BG3, border_color=BORDER,
                                   border_width=1, font=ctk.CTkFont(family="Consolas", size=12),
                                   text_color=TEXT)
        self.text.pack(padx=20, pady=10, fill="x")
        if existing_note:
            self.text.insert("1.0", existing_note)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(padx=20, pady=(0, 16), fill="x")
        ctk.CTkButton(btns, text="Save note", fg_color=ACCENT, text_color=BG,
                      hover_color="#00a0b8", command=self._save,
                      font=ctk.CTkFont(size=12)).pack(side="right", padx=(6, 0))
        ctk.CTkButton(btns, text="Clear", fg_color=SURFACE2, text_color=TEXT2,
                      hover_color=SURFACE, command=self._clear,
                      font=ctk.CTkFont(size=12)).pack(side="right")

    def _save(self):
        self.result = self.text.get("1.0", "end").strip()
        self.destroy()

    def _clear(self):
        self.result = ""
        self.destroy()


# ─── CheckItem Widget ─────────────────────────────────────────────────────────
class CheckItem(ctk.CTkFrame):
    def __init__(self, parent, phase_id, item_idx, item_data, app, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.phase_id  = phase_id
        self.item_idx  = item_idx
        self.item_data = item_data
        self.app       = app
        self.key       = (phase_id, item_idx)
        self._build()

    def _build(self):
        self.configure(fg_color=SURFACE, corner_radius=6)
        self.grid_columnconfigure(1, weight=1)

        # Checkbox
        self.cb_var = tk.BooleanVar(value=self.app.check_state.get(self.key, False))
        self.cb = ctk.CTkCheckBox(
            self, variable=self.cb_var, text="",
            width=20, checkbox_width=18, checkbox_height=18,
            fg_color=GREEN, hover_color="#2ab87a", border_color=BORDER,
            command=self._on_toggle
        )
        self.cb.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)

        # Name
        self.name_lbl = ctk.CTkLabel(
            self, text=self.item_data["name"],
            font=ctk.CTkFont(size=13), text_color=TEXT, anchor="w", wraplength=520
        )
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(10, 0))

        # Hint
        self.hint_lbl = ctk.CTkLabel(
            self, text=self.item_data["hint"],
            font=ctk.CTkFont(family="Consolas", size=10), text_color=TEXT3, anchor="w"
        )
        self.hint_lbl.grid(row=1, column=1, sticky="w", pady=(0, 4))

        # Type badge + note button
        badge_frame = ctk.CTkFrame(self, fg_color="transparent")
        badge_frame.grid(row=2, column=1, sticky="w", pady=(0, 8))

        t = self.item_data["type"]
        badge_color = BLUE if t == "passive" else WARN
        badge_bg    = "#0d2233" if t == "passive" else "#2b1e00"
        ctk.CTkLabel(badge_frame, text=t.upper(),
                     font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                     text_color=badge_color, fg_color=badge_bg,
                     corner_radius=3, padx=6, pady=2).pack(side="left", padx=(0, 6))

        self.note_btn = ctk.CTkButton(
            badge_frame, text="📝 Add note", font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="transparent", text_color=TEXT3, hover_color=SURFACE2,
            border_color=BORDER, border_width=1, height=22, width=80,
            command=self._open_note
        )
        self.note_btn.pack(side="left")

        # Note preview label
        self.note_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(family="Consolas", size=10),
            text_color=ACCENT, anchor="w", wraplength=520
        )
        self.note_lbl.grid(row=3, column=1, sticky="w", pady=(0, 6))

        # Right column — note indicator
        self.note_dot = ctk.CTkLabel(self, text="", width=8)
        self.note_dot.grid(row=0, column=2, padx=(0, 8))

        self._refresh_note_display()
        self._refresh_done_style()

    def _on_toggle(self):
        self.app.check_state[self.key] = self.cb_var.get()
        self._refresh_done_style()
        self.app.update_stats()
        self.app.autosave()

    def _refresh_done_style(self):
        done = self.cb_var.get()
        c = TEXT3 if done else TEXT
        self.name_lbl.configure(text_color=c)
        self.configure(fg_color=("#0f1117" if done else SURFACE))

    def _open_note(self):
        existing = self.app.notes.get(self.key, "")
        dlg = NoteDialog(self.app, self.item_data["name"], existing)
        self.app.wait_window(dlg)
        if dlg.result is not None:
            if dlg.result:
                self.app.notes[self.key] = dlg.result
            else:
                self.app.notes.pop(self.key, None)
            self._refresh_note_display()
            self.app.autosave()

    def _refresh_note_display(self):
        note = self.app.notes.get(self.key, "")
        if note:
            preview = note[:80] + ("…" if len(note) > 80 else "")
            self.note_lbl.configure(text=f"📝  {preview}")
            self.note_btn.configure(text="📝 Edit note")
            self.note_dot.configure(text="●", text_color=ACCENT)
        else:
            self.note_lbl.configure(text="")
            self.note_btn.configure(text="📝 Add note")
            self.note_dot.configure(text="")

    def set_visible(self, visible):
        if visible:
            self.pack(fill="x", padx=0, pady=(0, 4))
        else:
            self.pack_forget()

    def matches_filter(self, f):
        done = self.cb_var.get()
        if f == "all":       return True
        if f == "passive":   return self.item_data["type"] == "passive"
        if f == "active":    return self.item_data["type"] == "active"
        if f == "incomplete": return not done
        if f == "complete":  return done
        return True


# ─── Phase Section ────────────────────────────────────────────────────────────
class PhaseSection(ctk.CTkFrame):
    def __init__(self, parent, phase_data, app, **kwargs):
        super().__init__(parent, fg_color=BG2, corner_radius=10, **kwargs)
        self.phase   = phase_data
        self.app     = app
        self.items   = []
        self._open   = True
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG3, corner_radius=8)
        hdr.pack(fill="x", padx=2, pady=(2, 0))
        hdr.grid_columnconfigure(1, weight=1)

        # Colour dot
        dot = tk.Canvas(hdr, width=12, height=12, bg=BG3, highlightthickness=0)
        dot.create_oval(1, 1, 11, 11, fill=self.phase["color"], outline="")
        dot.grid(row=0, column=0, padx=(12, 8), pady=14)

        # Title block
        title_block = ctk.CTkFrame(hdr, fg_color="transparent")
        title_block.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(title_block, text=self.phase["title"],
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(title_block, text=self.phase["subtitle"],
                     font=ctk.CTkFont(family="Consolas", size=10), text_color=TEXT3).pack(anchor="w")

        # Progress label
        self.prog_lbl = ctk.CTkLabel(hdr, text="0/0",
                                     font=ctk.CTkFont(family="Consolas", size=11), text_color=TEXT3)
        self.prog_lbl.grid(row=0, column=2, padx=12)

        # Progress bar
        self.prog_bar = ctk.CTkProgressBar(hdr, width=80, height=4,
                                           fg_color=BORDER, progress_color=self.phase["color"])
        self.prog_bar.set(0)
        self.prog_bar.grid(row=0, column=3, padx=(0, 8))

        # Toggle button
        self.toggle_btn = ctk.CTkButton(
            hdr, text="▾", width=28, height=28, font=ctk.CTkFont(size=14),
            fg_color="transparent", hover_color=SURFACE2, text_color=TEXT3,
            command=self._toggle
        )
        self.toggle_btn.grid(row=0, column=4, padx=(0, 10))
        hdr.bind("<Button-1>", lambda e: self._toggle())

        # Body frame
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="x", padx=8, pady=(6, 8))

        # Build items
        for i, item in enumerate(self.phase["items"]):
            ci = CheckItem(self.body, self.phase["id"], i, item, self.app)
            ci.pack(fill="x", padx=0, pady=(0, 4))
            self.items.append(ci)

        self.update_progress()

    def _toggle(self):
        self._open = not self._open
        if self._open:
            self.body.pack(fill="x", padx=8, pady=(6, 8))
            self.toggle_btn.configure(text="▾")
        else:
            self.body.pack_forget()
            self.toggle_btn.configure(text="▸")

    def update_progress(self):
        done  = sum(1 for ci in self.items if ci.cb_var.get())
        total = len(self.items)
        self.prog_lbl.configure(text=f"{done}/{total}")
        self.prog_bar.set(done / total if total else 0)
        if done == total and total > 0:
            self.prog_bar.configure(progress_color=GREEN)
        else:
            self.prog_bar.configure(progress_color=self.phase["color"])

    def apply_filter(self, f):
        for ci in self.items:
            ci.set_visible(ci.matches_filter(f))


# ─── Main Application ─────────────────────────────────────────────────────────
class OSINTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OSINT Engagement Checklist - Techwin")
        self.geometry("1000x900")
        self.minsize(800, 600)
        self.configure(fg_color=BG)

        self.check_state   = {}   # {(phase_id, item_idx): bool}
        self.notes   = {}   # {(phase_id, item_idx): str}
        self.target  = tk.StringVar()
        self.current_file = None
        self.current_filter = "all"
        self.sections = []

        SAVE_DIR.mkdir(exist_ok=True)
        self._build_ui()
        self._load_last()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_titlebar()
        self._build_main()

    def _build_titlebar(self):
        tb = ctk.CTkFrame(self, fg_color=BG2, corner_radius=0, height=56)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)

        ctk.CTkLabel(tb, text="OSINT//RECON", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                     text_color=ACCENT).pack(side="left", padx=18)
        ctk.CTkLabel(tb, text="Engagement Checklist — AUTHORISED RECONNAISSANCE ONLY",
                     font=ctk.CTkFont(size=11), text_color=TEXT3).pack(side="left")

        btn_frame = ctk.CTkFrame(tb, fg_color="transparent")
        btn_frame.pack(side="right", padx=14)

        for txt, cmd, fg, tc in [
            ("New",       self.new_session,  SURFACE2, TEXT2),
            ("Open…",     self.open_session, SURFACE2, TEXT2),
            ("Save",      self.save_session, SURFACE2, TEXT2),
            ("Save As…",  self.save_as,      SURFACE2, TEXT2),
            ("Export MD", self.export_md,    ACCENT,   BG),
        ]:
            ctk.CTkButton(btn_frame, text=txt, command=cmd, width=82, height=30,
                          fg_color=fg, text_color=tc, hover_color=SURFACE,
                          font=ctk.CTkFont(size=11)).pack(side="left", padx=3)

    def _build_main(self):
        paned = ctk.CTkFrame(self, fg_color="transparent")
        paned.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_sidebar(paned)
        self._build_content(paned)

    def _build_sidebar(self, parent):
        sb = ctk.CTkFrame(parent, fg_color=BG2, corner_radius=0, width=230)
        sb.pack(side="left", fill="y", padx=0, pady=0)
        sb.pack_propagate(False)

        # Target input
        ctk.CTkLabel(sb, text="TARGET", font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                     text_color=TEXT3).pack(anchor="w", padx=16, pady=(16, 2))
        ctk.CTkEntry(sb, textvariable=self.target, placeholder_text="yourdomain.com",
                     fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
                     font=ctk.CTkFont(family="Consolas", size=12)).pack(fill="x", padx=12, pady=(0, 12))

        # Progress ring substitute — big % label
        ring_frame = ctk.CTkFrame(sb, fg_color=SURFACE, corner_radius=10)
        ring_frame.pack(fill="x", padx=12, pady=(0, 12))

        self.pct_lbl = ctk.CTkLabel(ring_frame, text="0%",
                                    font=ctk.CTkFont(family="Consolas", size=40, weight="bold"),
                                    text_color=ACCENT)
        self.pct_lbl.pack(pady=(14, 0))
        ctk.CTkLabel(ring_frame, text="complete",
                     font=ctk.CTkFont(size=10), text_color=TEXT3).pack(pady=(0, 4))

        self.overall_bar = ctk.CTkProgressBar(ring_frame, height=5,
                                              fg_color=BORDER, progress_color=ACCENT)
        self.overall_bar.set(0)
        self.overall_bar.pack(fill="x", padx=14, pady=(4, 14))

        # Stats grid
        stats_frame = ctk.CTkFrame(sb, fg_color=SURFACE, corner_radius=10)
        stats_frame.pack(fill="x", padx=12, pady=(0, 12))
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.stat_labels = {}
        for idx, (key, label, color) in enumerate([
            ("done",    "Completed",   GREEN),
            ("remain",  "Remaining",   TEXT2),
            ("phases",  "Phases done", ACCENT),
            ("active",  "Active done", WARN),
        ]):
            r, c = divmod(idx, 2)
            cell = ctk.CTkFrame(stats_frame, fg_color="transparent")
            cell.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")
            val = ctk.CTkLabel(cell, text="0", font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
                               text_color=color)
            val.pack()
            ctk.CTkLabel(cell, text=label, font=ctk.CTkFont(size=9), text_color=TEXT3).pack()
            self.stat_labels[key] = val

        # Filter
        ctk.CTkLabel(sb, text="FILTER", font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                     text_color=TEXT3).pack(anchor="w", padx=16, pady=(4, 4))

        for label, key in [("All items", "all"), ("Passive only", "passive"),
                            ("Active only", "active"), ("Incomplete", "incomplete"), ("Completed", "complete")]:
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                fg_color=(ACCENT if key == "all" else "transparent"),
                text_color=(BG if key == "all" else TEXT2),
                hover_color=SURFACE2, height=30,
                font=ctk.CTkFont(size=12),
                command=lambda k=key: self.set_filter(k)
            )
            btn.pack(fill="x", padx=12, pady=1)
            setattr(self, f"filter_btn_{key}", btn)

        # Phase nav
        ctk.CTkLabel(sb, text="PHASES", font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                     text_color=TEXT3).pack(anchor="w", padx=16, pady=(12, 4))

        self.phase_nav_labels = {}
        for p in PHASES:
            row = ctk.CTkFrame(sb, fg_color="transparent", height=28)
            row.pack(fill="x", padx=12, pady=1)
            row.pack_propagate(False)

            dot = tk.Canvas(row, width=8, height=8, bg=BG2, highlightthickness=0)
            dot.create_oval(0, 0, 8, 8, fill=p["color"], outline="")
            dot.pack(side="left", padx=(6, 6), pady=10)

            name = p["title"].split("—")[1].strip() if "—" in p["title"] else p["title"]
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=11), text_color=TEXT2,
                         anchor="w").pack(side="left", fill="x", expand=True)

            prog = ctk.CTkLabel(row, text="0/0", font=ctk.CTkFont(family="Consolas", size=9),
                                text_color=TEXT3, width=30)
            prog.pack(side="right", padx=4)
            self.phase_nav_labels[p["id"]] = prog

        # Reset
        ctk.CTkButton(sb, text="⟳  Reset all progress", fg_color="transparent",
                      text_color=RED, hover_color=SURFACE2, border_color=RED, border_width=1,
                      font=ctk.CTkFont(size=11), command=self.reset_all).pack(
                          fill="x", padx=12, pady=(16, 16), side="bottom")

    def _build_content(self, parent):
        content_wrap = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        content_wrap.pack(side="left", fill="both", expand=True)

        # File path bar
        self.file_bar = ctk.CTkLabel(content_wrap, text="No file — use Save As to save to disk",
                                     font=ctk.CTkFont(family="Consolas", size=10), text_color=TEXT3,
                                     anchor="w")
        self.file_bar.pack(fill="x", padx=16, pady=(8, 4))

        # Scrollable area
        self.scroll = ctk.CTkScrollableFrame(content_wrap, fg_color=BG, scrollbar_button_color=BORDER)
        self.scroll.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        for p in PHASES:
            sec = PhaseSection(self.scroll, p, self)
            sec.pack(fill="x", padx=0, pady=(0, 10))
            self.sections.append(sec)

    # ── Filter ────────────────────────────────────────────────────────────────
    def set_filter(self, key):
        self.current_filter = key
        for k in ["all", "passive", "active", "incomplete", "complete"]:
            btn = getattr(self, f"filter_btn_{k}", None)
            if btn:
                active = k == key
                btn.configure(fg_color=(ACCENT if active else "transparent"),
                              text_color=(BG if active else TEXT2))
        for sec in self.sections:
            sec.apply_filter(key)

    # ── Stats ─────────────────────────────────────────────────────────────────
    def update_stats(self):
        done = remain = active_done = 0
        total = sum(len(p["items"]) for p in PHASES)
        phases_done = 0

        for p in PHASES:
            p_done = 0
            for i, item in enumerate(p["items"]):
                key = (p["id"], i)
                if self.check_state.get(key):
                    done += 1
                    p_done += 1
                    if item["type"] == "active":
                        active_done += 1
                else:
                    remain += 1
            if p_done == len(p["items"]):
                phases_done += 1

            lbl = self.phase_nav_labels.get(p["id"])
            if lbl:
                lbl.configure(text=f"{p_done}/{len(p['items'])}")

        pct = int(done / total * 100) if total else 0
        self.pct_lbl.configure(text=f"{pct}%")
        self.pct_lbl.configure(text_color=GREEN if pct == 100 else ACCENT)
        self.overall_bar.set(pct / 100)
        self.stat_labels["done"].configure(text=str(done))
        self.stat_labels["remain"].configure(text=str(remain))
        self.stat_labels["phases"].configure(text=f"{phases_done}/{len(PHASES)}")
        self.stat_labels["active"].configure(text=str(active_done))

        for sec in self.sections:
            sec.update_progress()

    # ── Serialisation ─────────────────────────────────────────────────────────
    def _to_dict(self):
        return {
            "target":  self.target.get(),
            "saved":   datetime.now().isoformat(),
            "version": 1,
            "state":   {f"{k[0]}.{k[1]}": v for k, v in self.check_state.items()},
            "notes":   {f"{k[0]}.{k[1]}": v for k, v in self.notes.items()},
        }

    def _from_dict(self, data):
        self.target.set(data.get("target", ""))
        raw_state = data.get("state", {})
        raw_notes = data.get("notes", {})
        self.check_state = {}
        self.notes = {}
        for k, v in raw_state.items():
            pid, idx = k.rsplit(".", 1)
            self.check_state[(pid, int(idx))] = v
        for k, v in raw_notes.items():
            pid, idx = k.rsplit(".", 1)
            self.notes[(pid, int(idx))] = v

    def _sync_widgets(self):
        for sec in self.sections:
            for ci in sec.items:
                ci.cb_var.set(self.check_state.get(ci.key, False))
                ci._refresh_done_style()
                ci._refresh_note_display()
        self.update_stats()

    # ── File ops ──────────────────────────────────────────────────────────────
    def autosave(self):
        if self.current_file:
            self._write(self.current_file)

    def _write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(), f, indent=2)
        self.file_bar.configure(text=f"📁  {path}")

    def _read(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def new_session(self):
        if not messagebox.askyesno("New Session", "Start a new session? Unsaved changes will be lost."):
            return
        self.check_state = {}
        self.notes = {}
        self.target.set("")
        self.current_file = None
        self.file_bar.configure(text="No file — use Save As to save to disk")
        self._sync_widgets()

    def open_session(self):
        path = filedialog.askopenfilename(
            initialdir=SAVE_DIR, title="Open OSINT session",
            filetypes=[("OSINT JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            data = self._read(path)
            self._from_dict(data)
            self.current_file = path
            self._sync_widgets()
            self.file_bar.configure(text=f"📁  {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    def save_session(self):
        if self.current_file:
            self._write(self.current_file)
            self.file_bar.configure(text=f"📁  {self.current_file}  ✓ saved")
        else:
            self.save_as()

    def save_as(self):
        target_slug = self.target.get().replace(".", "_").replace("/", "_") or "engagement"
        default_name = f"osint_{target_slug}_{datetime.now().strftime('%Y%m%d')}.json"
        path = filedialog.asksaveasfilename(
            initialdir=SAVE_DIR, initialfile=default_name, title="Save OSINT session",
            defaultextension=".json", filetypes=[("OSINT JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        self.current_file = path
        self._write(path)

    def _load_last(self):
        last = SAVE_DIR / ".last"
        if last.exists():
            try:
                lf = last.read_text().strip()
                if lf and Path(lf).exists():
                    data = self._read(lf)
                    self._from_dict(data)
                    self.current_file = lf
                    self._sync_widgets()
                    self.file_bar.configure(text=f"📁  {lf}  (last session)")
                    return
            except Exception:
                pass
        self.update_stats()

    def _save_last_pointer(self):
        if self.current_file:
            (SAVE_DIR / ".last").write_text(str(self.current_file))

    # ── Export ────────────────────────────────────────────────────────────────
    def export_md(self):
        now    = datetime.now().strftime("%d %B %Y %H:%M")
        tgt    = self.target.get() or "[target not specified]"
        total  = sum(len(p["items"]) for p in PHASES)
        done   = sum(1 for v in self.check_state.values() if v)
        pct    = int(done / total * 100) if total else 0

        lines  = [
            "# OSINT Engagement Report",
            f"**Target:** {tgt}  ",
            f"**Date:** {now}  ",
            f"**Completion:** {pct}% ({done}/{total} checks)  ",
            "",
            "---",
            "",
        ]
        for p in PHASES:
            p_done = sum(1 for i in range(len(p["items"])) if self.check_state.get((p["id"], i)))
            lines += [
                f"## {p['title']}",
                f"*{p['subtitle']}*",
                f"",
                f"Progress: {p_done}/{len(p['items'])}",
                "",
            ]
            for i, item in enumerate(p["items"]):
                key  = (p["id"], i)
                done_mark = "x" if self.check_state.get(key) else " "
                lines.append(f"- [{done_mark}] **{item['name']}**")
                note = self.notes.get(key)
                if note:
                    lines.append(f"  - 📝 {note}")
            lines.append("")

        lines += [
            "---",
            "*Generated by OSINT Engagement Checklist — Authorised reconnaissance only*",
        ]
        md = "\n".join(lines)

        target_slug = self.target.get().replace(".", "_").replace("/", "_") or "engagement"
        default_name = f"osint_report_{target_slug}_{datetime.now().strftime('%Y%m%d')}.md"
        path = filedialog.asksaveasfilename(
            initialdir=SAVE_DIR, initialfile=default_name, title="Export Markdown report",
            defaultextension=".md", filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            messagebox.showinfo("Exported", f"Report saved to:\n{path}")

    # ── Reset ─────────────────────────────────────────────────────────────────
    def reset_all(self):
        if not messagebox.askyesno("Reset", "Reset all checkboxes and notes?"):
            return
        self.check_state = {}
        self.notes = {}
        self._sync_widgets()
        self.autosave()

    # ── Close ─────────────────────────────────────────────────────────────────
    def on_close(self):
        self.autosave()
        self._save_last_pointer()
        self.destroy()


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = OSINTApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
