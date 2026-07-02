import tkinter as tk
from password import (
    register_user,
    change_password,
    unlock_account,
    check_password_strength,
    get_connection,
    set_security_question,
    get_security_question,
    reset_password_with_question,
    get_all_users,
    change_user_role,
    get_login_history,
    check_password_expiry,
    send_otp,
    verify_otp
)

# ─────────────────────────────────────────────
#  THEME — Obsidian Gold
#  Deep black-charcoal base · Champagne gold accents · Premium feel
# ─────────────────────────────────────────────
BG          = "#0A0A0E"       # near-black base
SURFACE     = "#131318"       # card surface
SURFACE2    = "#1C1C24"       # input / inner surface
BORDER      = "#2B2B36"       # subtle border
GOLD        = "#D4AF37"       # champagne gold — primary accent
GOLD_DIM    = "#B8942C"       # deeper gold
GOLD_SOFT   = "#F0D584"       # bright gold highlight
EMERALD     = "#34D399"       # success green
ROSE        = "#F0616D"       # error red
AMBER       = "#F5B942"       # warning / notice
PLUM        = "#A78BFA"       # secondary accent
TEXT_HI     = "#F5F1E8"       # warm high-contrast text
TEXT_MID    = "#96969F"       # mid text
TEXT_LO     = "#4B4B57"       # low / placeholder text
HOVER       = "#232330"       # hover state


class PasswordApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Password Protection System")
        self.configure(bg=BG)
        self.current_user = None
        self._timeout_job = None

        # ── Premium sizing: window fills roughly half the screen ──
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.WIN_W = max(980, int(sw * 0.5))
        self.WIN_H = max(760, int(sh * 0.78))
        self.FORM_W = 520                              # fixed width of centered form column
        self.side_pad = max(24, (self.WIN_W - self.FORM_W) // 2)

        self.geometry(f"{self.WIN_W}x{self.WIN_H}")
        self.minsize(900, 700)
        self._center()
        self.show_login()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.WIN_W) // 2
        y = (self.winfo_screenheight() - self.WIN_H) // 2
        self.geometry(f"{self.WIN_W}x{self.WIN_H}+{x}+{y}")

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _reset_timeout(self, event=None):
        if self._timeout_job:
            self.after_cancel(self._timeout_job)
        if self.current_user:
            self._timeout_job = self.after(300000, self._auto_logout)

    def _auto_logout(self):
        self.current_user = None
        self.show_login()

    def _bind_activity(self):
        self.bind_all("<Motion>",   self._reset_timeout)
        self.bind_all("<KeyPress>", self._reset_timeout)
        self.bind_all("<Button>",   self._reset_timeout)

    # ── layout helpers ────────────────────────

    def _scrollable(self, parent, width=None):
        w = width or self.FORM_W
        canvas = tk.Canvas(parent, bg=SURFACE, highlightthickness=0)
        sb     = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame  = tk.Frame(canvas, bg=SURFACE)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw", width=w)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return frame

    # ── widget factory ────────────────────────

    def card(self, parent, pady=24):
        """A fixed-width, centered premium panel on the wider window."""
        f = tk.Frame(parent, bg=SURFACE, bd=0)
        f.pack(fill="both", expand=True, padx=self.side_pad, pady=pady)
        return f

    def lbl(self, parent, text, size=11, color=TEXT_MID, bold=False, anchor="w"):
        tk.Label(parent, text=text,
                 font=("Segoe UI", size, "bold" if bold else "normal"),
                 bg=parent["bg"], fg=color, anchor=anchor
                 ).pack(fill="x", padx=26, pady=(8, 0))

    def divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=26, pady=12)

    def entry(self, parent, hint="", show=""):
        wrap = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                        highlightcolor=GOLD_DIM, highlightthickness=1)
        wrap.pack(fill="x", padx=26, pady=(4, 2))
        e = tk.Entry(wrap, font=("Segoe UI", 11), bg=SURFACE2,
                     fg=TEXT_HI, insertbackground=GOLD,
                     relief="flat", bd=10, show=show)
        e.pack(fill="x")
        if hint:
            e.insert(0, hint); e.config(fg=TEXT_LO)
            def fi(ev):
                if e.get() == hint: e.delete(0, "end"); e.config(fg=TEXT_HI)
            def fo(ev):
                if e.get() == "": e.insert(0, hint); e.config(fg=TEXT_LO)
            e.bind("<FocusIn>", fi); e.bind("<FocusOut>", fo)
        return e

    def pass_entry(self, parent, hint=""):
        wrap = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                        highlightcolor=GOLD_DIM, highlightthickness=1)
        wrap.pack(fill="x", padx=26, pady=(4, 2))
        e = tk.Entry(wrap, font=("Segoe UI", 11), bg=SURFACE2,
                     fg=TEXT_LO, insertbackground=GOLD, relief="flat", bd=10)
        e.pack(side="left", fill="x", expand=True)
        showing = [False]
        def tog():
            if showing[0]:
                e.config(show="●"); eye.config(text="◎"); showing[0] = False
            else:
                e.config(show=""); eye.config(text="◉"); showing[0] = True
        eye = tk.Button(wrap, text="◎", font=("Segoe UI", 12),
                        bg=SURFACE2, fg=TEXT_LO, relief="flat", bd=0,
                        cursor="hand2", command=tog, activebackground=SURFACE2)
        eye.pack(side="right", padx=6)
        if hint:
            e.insert(0, hint)
            def fi(ev):
                if e.get() == hint:
                    e.delete(0, "end"); e.config(fg=TEXT_HI, show="●")
                    showing[0] = False; eye.config(text="◎")
            def fo(ev):
                if e.get() == "": e.insert(0, hint); e.config(fg=TEXT_LO, show="")
            e.bind("<FocusIn>", fi); e.bind("<FocusOut>", fo)
        return e

    def btn(self, parent, text, cmd, bg=GOLD, fg=BG, outline=False):
        if outline:
            b = tk.Button(parent, text=text,
                          font=("Segoe UI", 11, "bold"),
                          bg=SURFACE, fg=GOLD,
                          relief="flat", bd=0, cursor="hand2",
                          activebackground=HOVER, activeforeground=GOLD_SOFT,
                          highlightbackground=GOLD, highlightthickness=1,
                          command=cmd, anchor="center")
        else:
            b = tk.Button(parent, text=text,
                          font=("Segoe UI", 11, "bold"),
                          bg=bg, fg=fg, relief="flat", bd=0,
                          cursor="hand2", activebackground=bg,
                          activeforeground=fg, command=cmd, anchor="center")
        b.pack(fill="x", padx=26, pady=5, ipady=12)
        return b

    def ghost_btn(self, parent, text, cmd, color=GOLD):
        l = tk.Label(parent, text=text, font=("Segoe UI", 10),
                     bg=parent["bg"], fg=color, cursor="hand2")
        l.pack(pady=3)
        l.bind("<Button-1>", lambda e: cmd())

    def toast(self, parent, msg, ok=True):
        color = EMERALD if ok else ROSE
        icon  = "✦" if ok else "✕"
        t = tk.Label(parent, text=f"  {icon}  {msg}",
                     font=("Segoe UI", 10), bg=color, fg=BG, anchor="w")
        t.pack(fill="x", padx=26, pady=(4, 0))
        self.after(3000, t.destroy)

    def header(self, parent, icon, title, sub="", icolor=GOLD):
        tk.Label(parent, text=icon, font=("Segoe UI", 32),
                 bg=parent["bg"], fg=icolor).pack(pady=(32, 4))
        tk.Label(parent, text=title, font=("Segoe UI", 21, "bold"),
                 bg=parent["bg"], fg=TEXT_HI).pack()
        if sub:
            tk.Label(parent, text=sub, font=("Segoe UI", 10),
                     bg=parent["bg"], fg=TEXT_MID).pack(pady=(2, 0))

    def otp_boxes(self, parent):
        wrap = tk.Frame(parent, bg=parent["bg"])
        wrap.pack(pady=12)
        digits = []
        for i in range(6):
            b = tk.Entry(wrap, font=("Segoe UI", 20, "bold"), width=3,
                         bg=SURFACE2, fg=GOLD, insertbackground=GOLD,
                         relief="flat", bd=0, justify="center",
                         highlightbackground=BORDER, highlightthickness=1)
            b.pack(side="left", padx=5, ipady=10)
            digits.append(b)
            def jump(e, idx=i):
                v = digits[idx].get()
                if len(v) > 1: digits[idx].delete(1, "end")
                if len(v) == 1 and idx < 5: digits[idx+1].focus()
                if e.keysym == "BackSpace" and v == "" and idx > 0:
                    digits[idx-1].focus()
            b.bind("<KeyRelease>", jump)
        digits[0].focus()
        return lambda: "".join(d.get() for d in digits)

    # ─────────────────────────────────────────
    #  LOGIN
    # ─────────────────────────────────────────
    def show_login(self):
        self.clear()
        self.current_user = None
        if self._timeout_job: self.after_cancel(self._timeout_job)

        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        c     = self.card(outer, pady=48)
        self.header(c, "♛", "Password System", "Secure · Private · Protected")
        self.divider(c)

        self.lbl(c, "USERNAME")
        u = self.entry(c, "Enter username")

        self.lbl(c, "PASSWORD")
        p = self.pass_entry(c, "Enter password")

        tk.Frame(c, bg=SURFACE, height=6).pack()
        mf = tk.Frame(c, bg=SURFACE); mf.pack(fill="x")

        def do():
            un = u.get().strip(); pw = p.get().strip()
            if not un or un == "Enter username":
                self.toast(mf, "Please enter your username", ok=False); return
            if not pw or pw == "Enter password":
                self.toast(mf, "Please enter your password", ok=False); return
            r = check_creds(un, pw)
            if r == "success":
                sent = send_otp(un)
                if sent: self.show_otp(un)
                else: self.toast(mf, "Failed to send OTP — check your email", ok=False)
            elif r == "locked": self.toast(mf, "Account locked — please contact admin", ok=False)
            elif r == "not_found": self.toast(mf, "Username does not exist", ok=False)
            else: self.toast(mf, "Incorrect password!", ok=False)

        self.btn(c, "Login  →", do)
        self.ghost_btn(c, "Forgot password?", self.show_forgot, color=AMBER)
        self.divider(c)
        row = tk.Frame(c, bg=SURFACE); row.pack()
        tk.Label(row, text="New here?  ", font=("Segoe UI", 10),
                 bg=SURFACE, fg=TEXT_MID).pack(side="left")
        self.ghost_btn(row, "Create account", self.show_register, color=GOLD)

    # ─────────────────────────────────────────
    #  OTP SCREEN
    # ─────────────────────────────────────────
    def show_otp(self, username):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        c     = self.card(outer, pady=40)

        tk.Label(c, text="✉", font=("Segoe UI", 34), bg=SURFACE, fg=GOLD).pack(pady=(28, 2))
        tk.Label(c, text="Check Your Email", font=("Segoe UI", 20, "bold"),
                 bg=SURFACE, fg=TEXT_HI).pack()

        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("select e_mail from users where username = :1", [username])
            row  = cur.fetchone(); cur.close(); conn.close()
            em   = row[0] if row else "your email"
            p    = em.split("@")
            hint = p[0][:2] + "···@" + p[1] if len(p) == 2 else em
        except: hint = "your email"

        tk.Label(c, text=f"OTP sent to  {hint}", font=("Segoe UI", 10),
                 bg=SURFACE, fg=TEXT_MID).pack(pady=(4, 0))

        self.divider(c)
        tk.Label(c, text="ENTER 6-DIGIT CODE", font=("Segoe UI", 10),
                 bg=SURFACE, fg=TEXT_MID).pack()

        get_otp = self.otp_boxes(c)

        timer_lbl = tk.Label(c, text="⧗  5:00", font=("Segoe UI", 10),
                             bg=SURFACE, fg=AMBER)
        timer_lbl.pack(pady=(2, 0))
        secs = [300]
        def tick():
            if secs[0] > 0:
                secs[0] -= 1; m = secs[0]//60; s = secs[0]%60
                timer_lbl.config(text=f"⧗  {m}:{s:02d}",
                                 fg=AMBER if secs[0] > 60 else ROSE)
                self.after(1000, tick)
            else: timer_lbl.config(text="✕  OTP expired", fg=ROSE)
        tick()

        mf = tk.Frame(c, bg=SURFACE); mf.pack(fill="x")

        def verify():
            otp = get_otp()
            if len(otp) < 6: self.toast(mf, "Please enter all 6 digits", ok=False); return
            r = verify_otp(username, otp)
            if r == "success":
                self.current_user = username
                self._bind_activity(); self._reset_timeout()
                self.show_dashboard()
            elif r == "expired":
                self.toast(mf, "OTP has expired", ok=False)
                self.after(1800, self.show_login)
            elif r == "wrong": self.toast(mf, "Incorrect OTP — please check again", ok=False)
            else: self.toast(mf, "No OTP found", ok=False)

        def resend():
            if send_otp(username):
                secs[0] = 300
                self.toast(mf, "New OTP sent!", ok=True)
            else: self.toast(mf, "Failed to send email", ok=False)

        self.btn(c, "✦  Verify & Login", verify)
        row = tk.Frame(c, bg=SURFACE); row.pack(pady=2)
        tk.Label(row, text="Didn't receive OTP?  ", font=("Segoe UI", 10),
                 bg=SURFACE, fg=TEXT_MID).pack(side="left")
        self.ghost_btn(row, "Resend OTP", resend, color=GOLD)
        self.btn(c, "← Back to Login", self.show_login, bg=SURFACE2, fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  FORGOT PASSWORD  (Security Q + Email OTP)
    # ─────────────────────────────────────────
    def show_forgot(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)

        wrap = tk.Frame(outer, bg=SURFACE)
        wrap.pack(fill="both", expand=True, padx=self.side_pad, pady=20)

        canvas = tk.Canvas(wrap, bg=SURFACE, highlightthickness=0)
        sb     = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        c      = tk.Frame(canvas, bg=SURFACE)
        c.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=c, anchor="nw", width=self.FORM_W - 40)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.header(c, "🔑", "Reset Password",
                    "Choose verification method", icolor=AMBER)
        self.divider(c)

        # ── METHOD TABS ──
        tab_frame = tk.Frame(c, bg=SURFACE)
        tab_frame.pack(fill="x", padx=26, pady=(0, 8))

        method = tk.StringVar(value="question")

        def set_tab(val):
            method.set(val)
            if val == "question":
                q_tab.config(bg=GOLD, fg=BG)
                e_tab.config(bg=SURFACE2, fg=TEXT_MID)
                q_section.pack(fill="x")
                e_section.pack_forget()
            else:
                e_tab.config(bg=GOLD, fg=BG)
                q_tab.config(bg=SURFACE2, fg=TEXT_MID)
                e_section.pack(fill="x")
                q_section.pack_forget()

        q_tab = tk.Button(tab_frame, text="Security Question",
                          font=("Segoe UI", 10, "bold"),
                          bg=GOLD, fg=BG, relief="flat", bd=0,
                          cursor="hand2", activebackground=GOLD,
                          command=lambda: set_tab("question"))
        q_tab.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 2))

        e_tab = tk.Button(tab_frame, text="Email OTP",
                          font=("Segoe UI", 10, "bold"),
                          bg=SURFACE2, fg=TEXT_MID, relief="flat", bd=0,
                          cursor="hand2", activebackground=HOVER,
                          command=lambda: set_tab("email"))
        e_tab.pack(side="left", fill="x", expand=True, ipady=8)

        mf = tk.Frame(c, bg=SURFACE); mf.pack(fill="x")

        # ── SECURITY QUESTION SECTION ──
        q_section = tk.Frame(c, bg=SURFACE)

        tk.Label(q_section, text="USERNAME", font=("Segoe UI", 10),
                 bg=SURFACE, fg=TEXT_MID, anchor="w").pack(fill="x", padx=26, pady=(8, 0))

        qu_wrap = tk.Frame(q_section, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        qu_wrap.pack(fill="x", padx=26, pady=(4, 2))
        qu_entry = tk.Entry(qu_wrap, font=("Segoe UI", 11), bg=SURFACE2,
                            fg=TEXT_LO, insertbackground=GOLD, relief="flat", bd=10)
        qu_entry.insert(0, "Enter your username"); qu_entry.pack(fill="x")
        def qu_fi(e):
            if qu_entry.get() == "Enter your username":
                qu_entry.delete(0, "end"); qu_entry.config(fg=TEXT_HI)
        def qu_fo(e):
            if qu_entry.get() == "":
                qu_entry.insert(0, "Enter your username"); qu_entry.config(fg=TEXT_LO)
        qu_entry.bind("<FocusIn>", qu_fi); qu_entry.bind("<FocusOut>", qu_fo)

        q_result_frame = tk.Frame(q_section, bg=SURFACE)
        q_result_frame.pack(fill="x")

        answer_entry   = [None]
        new_pass_entry = [None]
        found          = [False]

        def load_q():
            u = qu_entry.get().strip()
            if not u or u == "Enter your username":
                self.toast(mf, "Please enter username", ok=False); return
            q = get_security_question(u)
            if q is None:
                self.toast(mf, "User not found or security question not set", ok=False); return
            for w in q_result_frame.winfo_children(): w.destroy()

            tk.Label(q_result_frame, text="YOUR SECURITY QUESTION",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_MID,
                     anchor="w").pack(fill="x", padx=26, pady=(10, 2))
            tk.Label(q_result_frame, text=f"  {q}",
                     font=("Segoe UI", 11, "italic"), bg=SURFACE2,
                     fg=AMBER, anchor="w", wraplength=self.FORM_W - 100).pack(fill="x", padx=26, ipady=10)

            tk.Label(q_result_frame, text="ANSWER",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_MID,
                     anchor="w").pack(fill="x", padx=26, pady=(10, 0))
            aw = tk.Frame(q_result_frame, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
            aw.pack(fill="x", padx=26, pady=(4, 2))
            answer_entry[0] = tk.Entry(aw, font=("Segoe UI", 11), bg=SURFACE2,
                                        fg=TEXT_HI, insertbackground=GOLD,
                                        relief="flat", bd=10)
            answer_entry[0].pack(fill="x")

            tk.Label(q_result_frame, text="NEW PASSWORD",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_MID,
                     anchor="w").pack(fill="x", padx=26, pady=(10, 0))
            tk.Label(q_result_frame, text="8+ chars · UPPER · lower · Sp3cial",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_LO,
                     anchor="w").pack(fill="x", padx=26)
            nw = tk.Frame(q_result_frame, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
            nw.pack(fill="x", padx=26, pady=(4, 2))
            new_pass_entry[0] = tk.Entry(nw, font=("Segoe UI", 11), bg=SURFACE2,
                                          fg=TEXT_HI, insertbackground=GOLD,
                                          relief="flat", bd=10, show="●")
            new_pass_entry[0].pack(fill="x")

            reset_btn.pack(fill="x", padx=26, pady=6, ipady=12)
            found[0] = True
            self.toast(mf, "Question loaded! Please answer below", ok=True)

        def do_q_reset():
            if not found[0]:
                self.toast(mf, "Please check username first", ok=False); return
            u = qu_entry.get().strip()
            a = answer_entry[0].get().strip()
            np = new_pass_entry[0].get().strip()
            if not a: self.toast(mf, "Please enter your answer", ok=False); return
            if not check_password_strength(np):
                self.toast(mf, "Please meet password requirements!", ok=False); return
            r = reset_password_with_question(u, a, np)
            if r == "success":
                self.toast(mf, "Password reset successful! Please login", ok=True)
                self.after(1800, self.show_login)
            elif r == "wrong_answer": self.toast(mf, "Incorrect answer!", ok=False)
            else: self.toast(mf, "Something went wrong", ok=False)

        tk.Button(q_section, text="Load Question  →",
                  font=("Segoe UI", 11, "bold"), bg=AMBER, fg=BG,
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=AMBER, command=load_q
                  ).pack(fill="x", padx=26, pady=6, ipady=12)

        reset_btn = tk.Button(q_section, text="✦  Reset Password",
                              font=("Segoe UI", 11, "bold"), bg=EMERALD, fg=BG,
                              relief="flat", bd=0, cursor="hand2",
                              activebackground=EMERALD, command=do_q_reset)

        q_section.pack(fill="x")

        # ── EMAIL OTP SECTION ──
        e_section = tk.Frame(c, bg=SURFACE)

        tk.Label(e_section, text="USERNAME", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT_MID, anchor="w").pack(fill="x", padx=26, pady=(10, 0))
        eu_wrap = tk.Frame(e_section, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        eu_wrap.pack(fill="x", padx=26, pady=(4, 2))
        eu_entry = tk.Entry(eu_wrap, font=("Segoe UI", 11), bg=SURFACE2,
                            fg=TEXT_LO, insertbackground=GOLD, relief="flat", bd=10)
        eu_entry.insert(0, "Enter your username"); eu_entry.pack(fill="x")
        def eu_fi(e):
            if eu_entry.get() == "Enter your username":
                eu_entry.delete(0, "end"); eu_entry.config(fg=TEXT_HI)
        def eu_fo(e):
            if eu_entry.get() == "":
                eu_entry.insert(0, "Enter your username"); eu_entry.config(fg=TEXT_LO)
        eu_entry.bind("<FocusIn>", eu_fi); eu_entry.bind("<FocusOut>", eu_fo)

        e_otp_frame  = tk.Frame(e_section, bg=SURFACE); e_otp_frame.pack(fill="x")
        e_otp_sent   = [False]
        get_e_otp    = [None]
        e_pass_entry = [None]

        def send_reset_otp():
            u = eu_entry.get().strip()
            if not u or u == "Enter your username":
                self.toast(mf, "Please enter username", ok=False); return
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("select count(*) from users where username = :1", [u])
                exists = cur.fetchone()[0]; cur.close(); conn.close()
                if not exists:
                    self.toast(mf, "This username does not exist", ok=False); return
            except: pass

            sent = send_otp(u)
            if not sent: self.toast(mf, "Failed to send email", ok=False); return

            for w in e_otp_frame.winfo_children(): w.destroy()

            tk.Label(e_otp_frame, text="EMAIL OTP",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_MID,
                     anchor="w").pack(fill="x", padx=26, pady=(10, 0))
            get_e_otp[0] = self.otp_boxes(e_otp_frame)

            tk.Label(e_otp_frame, text="NEW PASSWORD",
                     font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_MID,
                     anchor="w").pack(fill="x", padx=26, pady=(10, 0))
            pw = tk.Frame(e_otp_frame, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
            pw.pack(fill="x", padx=26, pady=(4, 2))
            e_pass_entry[0] = tk.Entry(pw, font=("Segoe UI", 11), bg=SURFACE2,
                                        fg=TEXT_HI, insertbackground=GOLD,
                                        relief="flat", bd=10, show="●")
            e_pass_entry[0].pack(fill="x")

            e_reset_btn.pack(fill="x", padx=26, pady=6, ipady=12)
            e_otp_sent[0] = True
            self.toast(mf, "OTP sent! Please check your email", ok=True)

        def do_e_reset():
            if not e_otp_sent[0]:
                self.toast(mf, "Please send OTP first", ok=False); return
            u   = eu_entry.get().strip()
            otp = get_e_otp[0]()
            np  = e_pass_entry[0].get().strip()
            if len(otp) < 6: self.toast(mf, "Please enter the 6-digit OTP", ok=False); return
            if not check_password_strength(np):
                self.toast(mf, "Please meet password requirements!", ok=False); return
            r = verify_otp(u, otp)
            if r == "wrong": self.toast(mf, "Incorrect OTP!", ok=False); return
            if r == "expired":
                self.toast(mf, "OTP has expired", ok=False); return

            from password import hash_password
            new_salt = u + "SALT2024"
            new_hash = hash_password(np, new_salt)
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("update passwords set password_hash=:1,salt=:2,created_at=sysdate where user_id=(select user_id from users where username=:3)", [new_hash, new_salt, u])
                cur.execute("update users set status='active',failed_attempts=0,locked_at=null where username=:1", [u])
                conn.commit(); cur.close(); conn.close()
                self.toast(mf, "Password reset successful! Please login", ok=True)
                self.after(1800, self.show_login)
            except Exception as ex:
                self.toast(mf, f"Error: {ex}", ok=False)

        tk.Button(e_section, text="Send OTP  →",
                  font=("Segoe UI", 11, "bold"), bg=GOLD, fg=BG,
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=GOLD, command=send_reset_otp
                  ).pack(fill="x", padx=26, pady=6, ipady=12)

        e_reset_btn = tk.Button(e_section, text="✦  Reset Password",
                                font=("Segoe UI", 11, "bold"), bg=EMERALD, fg=BG,
                                relief="flat", bd=0, cursor="hand2",
                                activebackground=EMERALD, command=do_e_reset)

        self.btn(c, "← Back to Login", self.show_login, bg=SURFACE2, fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  REGISTER
    # ─────────────────────────────────────────
    def show_register(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        wrap  = tk.Frame(outer, bg=SURFACE)
        wrap.pack(fill="both", expand=True, padx=self.side_pad, pady=20)
        c = self._scrollable(wrap, width=self.FORM_W - 40)

        self.header(c, "✦", "Create Account", "Join the system")
        self.divider(c)

        self.lbl(c, "USERNAME")
        u = self.entry(c, "Choose a username")

        self.lbl(c, "EMAIL")
        tk.Label(c, text="  OTP will be sent here on every login",
                 font=("Segoe UI", 9), bg=SURFACE, fg=AMBER,
                 anchor="w").pack(fill="x", padx=26)
        e = self.entry(c, "your@email.com")

        self.lbl(c, "FULL NAME")
        n = self.entry(c, "Your full name")

        self.lbl(c, "ROLE")
        roles = ["user", "moderator"]
        sel_r = tk.StringVar(value="user")
        rf    = tk.Frame(c, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        rf.pack(fill="x", padx=26, pady=(4, 2))
        rm = tk.OptionMenu(rf, sel_r, *roles)
        rm.config(font=("Segoe UI", 11), bg=SURFACE2, fg=TEXT_HI,
                  relief="flat", bd=0, activebackground=HOVER,
                  highlightthickness=0, width=36)
        rm["menu"].config(bg=SURFACE2, fg=TEXT_HI, font=("Segoe UI", 10))
        rm.pack(fill="x")

        self.lbl(c, "PASSWORD")
        p = self.pass_entry(c, "Strong password")

        s_lbl = tk.Label(c, text="", font=("Segoe UI", 9, "bold"),
                         bg=SURFACE, fg=TEXT_MID)
        s_lbl.pack(padx=26, anchor="w")
        s_bar = tk.Frame(c, bg=BORDER, height=4)
        s_bar.pack(fill="x", padx=26, pady=(2, 4))
        s_fill = tk.Frame(s_bar, bg=BORDER, height=4)
        s_fill.place(x=0, y=0, relheight=1, relwidth=0)

        rq = tk.Frame(c, bg=SURFACE); rq.pack(fill="x", padx=26)
        r1 = tk.Label(rq, text="◌  Min 8 characters", font=("Segoe UI", 9),
                      bg=SURFACE, fg=ROSE, anchor="w"); r1.pack(fill="x")
        r2 = tk.Label(rq, text="◌  Uppercase (A-Z)", font=("Segoe UI", 9),
                      bg=SURFACE, fg=ROSE, anchor="w"); r2.pack(fill="x")
        r3 = tk.Label(rq, text="◌  Special char (!@#$)", font=("Segoe UI", 9),
                      bg=SURFACE, fg=ROSE, anchor="w"); r3.pack(fill="x")

        def strength(ev=None):
            pw = p.get(); sp = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            hu = any(x.isupper() for x in pw)
            hl = any(x.islower() for x in pw)
            hs = any(x in sp for x in pw)
            hln = len(pw) >= 8
            r1.config(text=f"{'●' if hln else '◌'}  Min 8 characters", fg=EMERALD if hln else ROSE)
            r2.config(text=f"{'●' if hu  else '◌'}  Uppercase (A-Z)",  fg=EMERALD if hu  else ROSE)
            r3.config(text=f"{'●' if hs  else '◌'}  Special char (!@#$)", fg=EMERALD if hs else ROSE)
            sc = sum([hu, hl, hs, hln])
            col, tx, wd = (ROSE,"Weak",0.25) if sc<=1 else \
                          (AMBER,"Fair",0.5) if sc==2 else \
                          (PLUM,"Good",0.75) if sc==3 else (EMERALD,"Strong",1.0)
            s_fill.place(relwidth=wd); s_fill.config(bg=col)
            s_lbl.config(text=f"  {tx}", fg=col)
        p.bind("<KeyRelease>", strength)

        self.divider(c)
        tk.Label(c, text="SECURITY QUESTION", font=("Segoe UI", 9, "bold"),
                 bg=SURFACE, fg=AMBER, anchor="w").pack(fill="x", padx=26)
        tk.Label(c, text="  Used for account recovery",
                 font=("Segoe UI", 9), bg=SURFACE, fg=TEXT_LO,
                 anchor="w").pack(fill="x", padx=26)

        qs = ["What is your mother's name?", "What was your first school?",
              "What is your favorite food?", "What is your best friend's name?",
              "What was your first phone?"]
        sel_q = tk.StringVar(value=qs[0])
        qf    = tk.Frame(c, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        qf.pack(fill="x", padx=26, pady=(6, 2))
        qm = tk.OptionMenu(qf, sel_q, *qs)
        qm.config(font=("Segoe UI", 10), bg=SURFACE2, fg=TEXT_HI,
                  relief="flat", bd=0, activebackground=HOVER,
                  highlightthickness=0, width=36)
        qm["menu"].config(bg=SURFACE2, fg=TEXT_HI, font=("Segoe UI", 10))
        qm.pack(fill="x")

        self.lbl(c, "ANSWER")
        a = self.entry(c, "Your answer")

        mf = tk.Frame(c, bg=SURFACE); mf.pack(fill="x")

        def do_reg():
            un=u.get().strip(); em=e.get().strip()
            nm=n.get().strip(); pw=p.get().strip(); ans=a.get().strip()
            ph = ["Choose a username","your@email.com","Your full name","Strong password","Your answer"]
            if un in ph or not un: self.toast(mf,"Please fill all fields",ok=False); return
            if not check_password_strength(pw): self.toast(mf,"Please meet password requirements!",ok=False); return
            if not ans or ans in ph: self.toast(mf,"Please enter security answer",ok=False); return
            try:
                conn=get_connection(); cur=conn.cursor()
                cur.execute("select count(*) from users where username=:1",[un])
                if cur.fetchone()[0]>0:
                    self.toast(mf,"Username already exists!",ok=False)
                    cur.close(); conn.close(); return
                cur.close(); conn.close()
                register_user(un,em,nm,pw)
                set_security_question(un,sel_q.get(),ans)
                conn=get_connection(); cur=conn.cursor()
                cur.execute("select role_id from roles where role_name=:1",[sel_r.get()])
                rl=cur.fetchone()
                if rl:
                    cur.execute("select user_id from users where username=:1",[un])
                    uid=cur.fetchone()
                    if uid:
                        cur.execute("update users set role_id=:1 where user_id=:2",[rl[0],uid[0]])
                        conn.commit()
                cur.close(); conn.close()
                self.toast(mf,"Account created! Please login",ok=True)
                self.after(1500,self.show_login)
            except Exception as ex: self.toast(mf,f"Error: {ex}",ok=False)

        self.btn(c, "Create Account  →", do_reg)
        row = tk.Frame(c, bg=SURFACE); row.pack(pady=4)
        tk.Label(row,text="Already registered?  ",font=("Segoe UI",10),
                 bg=SURFACE,fg=TEXT_MID).pack(side="left")
        self.ghost_btn(row,"Login here",self.show_login,color=GOLD)

    # ─────────────────────────────────────────
    #  DASHBOARD  (premium grid layout)
    # ─────────────────────────────────────────
    def show_dashboard(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)

        # ── Top bar ──
        top = tk.Frame(outer, bg=SURFACE, height=64)
        top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text="♛  Password System", font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=GOLD).pack(side="left", padx=28, pady=20)

        # role for badge + right-side identity
        try:
            conn=get_connection(); cur=conn.cursor()
            cur.execute("select r.role_name from users u join roles r on u.role_id=r.role_id where u.username=:1",[self.current_user])
            rr=cur.fetchone(); cur.close(); conn.close()
            role = rr[0] if rr else "user"
        except: role = "user"

        idbox = tk.Frame(top, bg=SURFACE); idbox.pack(side="right", padx=28)
        tk.Label(idbox, text=(self.current_user[0].upper() if self.current_user else "U"),
                 font=("Segoe UI", 11, "bold"), bg=GOLD, fg=BG, width=2
                 ).pack(side="left", ipady=4, padx=(0, 8))
        namecol = tk.Frame(idbox, bg=SURFACE); namecol.pack(side="left")
        tk.Label(namecol, text=self.current_user, font=("Segoe UI", 10, "bold"),
                 bg=SURFACE, fg=TEXT_HI, anchor="w").pack(anchor="w")
        rc_badge = GOLD if role == "admin" else (PLUM if role == "moderator" else TEXT_MID)
        tk.Label(namecol, text=role.upper(), font=("Segoe UI", 8, "bold"),
                 bg=SURFACE, fg=rc_badge, anchor="w").pack(anchor="w")

        # ── Welcome banner ──
        banner = tk.Frame(outer, bg=BG)
        banner.pack(fill="x", padx=self.side_pad - 20 if self.side_pad > 60 else 40, pady=(28, 4))
        tk.Label(banner, text=f"Welcome back, {self.current_user}",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_HI, anchor="w").pack(anchor="w")
        tk.Label(banner, text="Here's your account control center",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID, anchor="w").pack(anchor="w")

        # expiry warning
        try:
            exp = check_password_expiry(self.current_user)
            if exp and exp["days_left"] <= 7:
                wf = tk.Frame(outer, bg="#241A05")
                wf.pack(fill="x", padx=self.side_pad - 20 if self.side_pad > 60 else 40, pady=(14, 0))
                d = exp["days_left"]
                tk.Label(wf,
                         text=f"  ⚠  Your password expires in {d} day{'s' if d!=1 else ''}!" if d>0 else "  ⚠  Your password expires today!",
                         font=("Segoe UI", 10, "bold"),
                         bg="#241A05", fg=AMBER).pack(padx=16, pady=12, anchor="w")
        except: pass

        # ── Premium card grid ──
        grid_wrap = tk.Frame(outer, bg=BG)
        grid_wrap.pack(fill="both", expand=True,
                       padx=self.side_pad - 20 if self.side_pad > 60 else 40, pady=22)

        items = [
            ("⬢",  "My Profile",       "View your account details",         GOLD,    self.show_profile),
            ("⚿",  "Change Password",  "Update your login credentials",     PLUM,    self.show_change_pw),
            ("◷",  "Login History",    "Review your recent activity",       EMERALD, self.show_history),
            ("⊙",  "Unlock Account",   "Restore access to a locked user",   AMBER,   self.show_unlock),
        ]
        if role == "admin":
            items.append(("♛", "Admin Panel", "Manage users and roles", GOLD, self.show_admin))
        items.append(("⏻", "Sign Out", "End your current session", ROSE, self._logout))

        cols = 2
        for i in range(cols):
            grid_wrap.grid_columnconfigure(i, weight=1, uniform="col")

        def make_card(parent, icon, title, desc, color, cmd):
            card_f = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                              highlightthickness=1, cursor="hand2")
            inner = tk.Frame(card_f, bg=SURFACE, cursor="hand2")
            inner.pack(fill="both", expand=True, padx=20, pady=18)

            top_row = tk.Frame(inner, bg=SURFACE, cursor="hand2")
            top_row.pack(fill="x", anchor="w")
            tk.Label(top_row, text=icon, font=("Segoe UI", 20), bg=SURFACE,
                     fg=color, cursor="hand2").pack(side="left")
            tk.Label(top_row, text="›", font=("Segoe UI", 14, "bold"), bg=SURFACE,
                     fg=TEXT_LO, cursor="hand2").pack(side="right")

            tk.Label(inner, text=title, font=("Segoe UI", 13, "bold"), bg=SURFACE,
                     fg=TEXT_HI, anchor="w", cursor="hand2").pack(fill="x", pady=(12, 2))
            tk.Label(inner, text=desc, font=("Segoe UI", 9), bg=SURFACE,
                     fg=TEXT_MID, anchor="w", wraplength=260, justify="left",
                     cursor="hand2").pack(fill="x")

            widgets = [card_f, inner, top_row] + list(inner.winfo_children()) + list(top_row.winfo_children())

            def on_enter(e):
                card_f.config(bg=HOVER, highlightbackground=color)
                for w in widgets:
                    try: w.config(bg=HOVER)
                    except: pass
            def on_leave(e):
                card_f.config(bg=SURFACE, highlightbackground=BORDER)
                for w in widgets:
                    try: w.config(bg=SURFACE)
                    except: pass
            for w in widgets:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", lambda e: cmd())

            return card_f

        for idx, (icon, title, desc, color, cmd) in enumerate(items):
            r, cidx = divmod(idx, cols)
            card_f = make_card(grid_wrap, icon, title, desc, color, cmd)
            card_f.grid(row=r, column=cidx, sticky="nsew", padx=8, pady=8)

    def _logout(self):
        self.current_user = None
        if self._timeout_job: self.after_cancel(self._timeout_job)
        self.show_login()

    # ─────────────────────────────────────────
    #  MY PROFILE
    # ─────────────────────────────────────────
    def show_profile(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        c = self.card(outer, pady=20)
        self.header(c, "⬢", "My Profile")
        self.divider(c)
        try:
            conn=get_connection(); cur=conn.cursor()
            cur.execute("""
                select u.username,u.e_mail,u.full_name,r.role_name,
                       u.status,u.failed_attempts,u.last_login
                from users u join roles r on u.role_id=r.role_id
                where u.username=:1""",[self.current_user])
            user=cur.fetchone(); cur.close(); conn.close()
            if user:
                av = tk.Frame(c, bg=SURFACE); av.pack(pady=(0,10))
                tk.Label(av, text=user[0][0].upper(),
                         font=("Segoe UI", 26, "bold"),
                         bg=GOLD, fg=BG, width=3).pack(ipady=10)
                fields=[("Username",user[0]),("Email",user[1]),("Full Name",user[2]),
                        ("Role",user[3]),("Status",user[4]),("Failed Attempts",str(user[5])),
                        ("Last Login",str(user[6]) if user[6] else "First time login")]
                inf = tk.Frame(c, bg=SURFACE2); inf.pack(fill="x", padx=26, pady=8)
                for lbl,val in fields:
                    row=tk.Frame(inf,bg=SURFACE2); row.pack(fill="x",padx=16,pady=7)
                    tk.Label(row,text=lbl,font=("Segoe UI",10),
                             bg=SURFACE2,fg=TEXT_MID,width=16,anchor="w").pack(side="left")
                    vc = EMERALD if val=="active" else (ROSE if val=="locked" else TEXT_HI)
                    tk.Label(row,text=val,font=("Segoe UI",10,"bold"),
                             bg=SURFACE2,fg=vc,anchor="w").pack(side="left")
        except Exception as ex:
            tk.Label(c,text=f"Error: {ex}",font=("Segoe UI",10),bg=SURFACE,fg=ROSE).pack()
        self.btn(c,"← Dashboard",self.show_dashboard,bg=SURFACE2,fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  LOGIN HISTORY
    # ─────────────────────────────────────────
    def show_history(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        top = tk.Frame(outer, bg=SURFACE, height=60)
        top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text="◷  Login History", font=("Segoe UI", 12, "bold"),
                 bg=SURFACE, fg=PLUM).pack(side="left", padx=28, pady=18)

        tk.Label(outer,text="Your Recent Activity",font=("Segoe UI",14,"bold"),
                 bg=BG,fg=TEXT_HI).pack(pady=(18,2))
        tk.Label(outer,text="Last 20 attempts",font=("Segoe UI",9),
                 bg=BG,fg=TEXT_MID).pack()

        lf = tk.Frame(outer,bg=BG); lf.pack(fill="both",expand=True,padx=self.side_pad-40 if self.side_pad>80 else 30,pady=10)
        cv = tk.Canvas(lf,bg=BG,highlightthickness=0)
        sb = tk.Scrollbar(lf,orient="vertical",command=cv.yview)
        inn= tk.Frame(cv,bg=BG)
        inn.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0),window=inn,anchor="nw",width=self.FORM_W)
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")

        try:
            hist = get_login_history(self.current_user)
            if not hist:
                tk.Label(inn,text="No history found",font=("Segoe UI",11),
                         bg=BG,fg=TEXT_MID).pack(pady=30)
            else:
                for h in hist[:20]:
                    t=str(h[0]); s=str(h[1]); ip=str(h[2]) if h[2] else "Unknown"
                    rs=str(h[3]) if h[3] else ""
                    sc = EMERALD if s=="success" else (AMBER if s=="locked" else ROSE)
                    si = "●" if s=="success" else ("⊘" if s=="locked" else "✕")
                    row=tk.Frame(inn,bg=SURFACE); row.pack(fill="x",pady=2,padx=4)
                    lft=tk.Frame(row,bg=SURFACE); lft.pack(side="left",fill="x",expand=True,padx=14,pady=9)
                    tk.Label(lft,text=f"{si}  {t[:19]}",font=("Segoe UI",10,"bold"),
                             bg=SURFACE,fg=sc,anchor="w").pack(fill="x")
                    info=f"IP: {ip}" + (f"  ·  {rs}" if rs else "")
                    tk.Label(lft,text=info,font=("Segoe UI",9),
                             bg=SURFACE,fg=TEXT_MID,anchor="w").pack(fill="x")
                    tk.Frame(inn,bg=BORDER,height=1).pack(fill="x",padx=4)
        except Exception as ex:
            tk.Label(inn,text=f"Error: {ex}",font=("Segoe UI",10),bg=BG,fg=ROSE).pack(pady=20)

        self.btn(outer,"← Dashboard",self.show_dashboard,bg=SURFACE2,fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  CHANGE PASSWORD
    # ─────────────────────────────────────────
    def show_change_pw(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        c = self.card(outer, pady=30)
        self.header(c,"⚿","Change Password",icolor=PLUM)
        self.divider(c)
        self.lbl(c,"CURRENT PASSWORD")
        old=self.pass_entry(c,"Current password")
        self.lbl(c,"NEW PASSWORD")
        tk.Label(c,text="  8+ chars · UPPER · lower · Sp3cial",
                 font=("Segoe UI",9),bg=SURFACE,fg=TEXT_LO,anchor="w").pack(fill="x",padx=26)
        new=self.pass_entry(c,"New password")
        mf=tk.Frame(c,bg=SURFACE); mf.pack(fill="x")
        def do():
            o=old.get().strip(); n=new.get().strip()
            if not o or not n: self.toast(mf,"Both fields are required",ok=False); return
            if not check_password_strength(n): self.toast(mf,"Password is too weak!",ok=False); return
            try:
                from password import hash_password
                conn=get_connection(); cur=conn.cursor()
                cur.execute("select password_hash,salt from passwords where user_id=(select user_id from users where username=:1)",[self.current_user])
                row=cur.fetchone(); cur.close(); conn.close()
                if not row or hash_password(o,row[1])!=row[0]:
                    self.toast(mf,"Current password is incorrect!",ok=False); return
                change_password(self.current_user,o,n)
                self.toast(mf,"Password changed successfully!",ok=True)
                self.after(1500,self.show_dashboard)
            except Exception as ex: self.toast(mf,f"Error: {ex}",ok=False)
        self.btn(c,"✦  Update Password",do,bg=PLUM,fg=BG)
        self.btn(c,"← Dashboard",self.show_dashboard,bg=SURFACE2,fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  UNLOCK
    # ─────────────────────────────────────────
    def show_unlock(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        c = self.card(outer, pady=40)
        self.header(c,"⊙","Unlock Account","Admin only",icolor=AMBER)
        self.divider(c)
        self.lbl(c,"ADMIN USERNAME")
        ad=self.entry(c,"Admin username")
        self.lbl(c,"TARGET USERNAME")
        tg=self.entry(c,"Locked user's username")
        mf=tk.Frame(c,bg=SURFACE); mf.pack(fill="x")
        def do():
            a=ad.get().strip(); t=tg.get().strip()
            if a in ["Admin username",""] or t in ["Locked user's username",""]:
                self.toast(mf,"Both fields are required",ok=False); return
            try:
                conn=get_connection(); cur=conn.cursor()
                cur.execute("select role_id from users where username=:1",[a])
                row=cur.fetchone(); cur.close(); conn.close()
                if row is None or row[0]!=4:
                    self.toast(mf,"Admin access required!",ok=False); return
                unlock_account(a,t)
                self.toast(mf,f"{t} has been unlocked!",ok=True)
            except Exception as ex: self.toast(mf,f"Error: {ex}",ok=False)
        self.btn(c,"⊙  Unlock Account",do,bg=AMBER,fg=BG)
        self.btn(c,"← Dashboard",self.show_dashboard,bg=SURFACE2,fg=TEXT_MID)

    # ─────────────────────────────────────────
    #  ADMIN PANEL
    # ─────────────────────────────────────────
    def show_admin(self):
        self.clear()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        top = tk.Frame(outer, bg=SURFACE, height=60)
        top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top,text="♛  Admin Panel",font=("Segoe UI",12,"bold"),
                 bg=SURFACE,fg=GOLD).pack(side="left",padx=28,pady=18)
        tk.Label(top,text=f"◉  {self.current_user}",font=("Segoe UI",10),
                 bg=SURFACE,fg=TEXT_MID).pack(side="right",padx=28)

        tk.Label(outer,text="User Management",font=("Segoe UI",14,"bold"),
                 bg=BG,fg=TEXT_HI).pack(pady=(18,2))
        tk.Label(outer,text="Change roles · Unlock accounts",
                 font=("Segoe UI",9),bg=BG,fg=TEXT_MID).pack()

        lf=tk.Frame(outer,bg=BG); lf.pack(fill="both",expand=True,padx=self.side_pad-40 if self.side_pad>80 else 30,pady=10)
        cv=tk.Canvas(lf,bg=BG,highlightthickness=0)
        sb=tk.Scrollbar(lf,orient="vertical",command=cv.yview)
        inn=tk.Frame(cv,bg=BG)
        inn.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0),window=inn,anchor="nw",width=self.FORM_W)
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")

        try:
            users=get_all_users()
            for u in users:
                uname=u[1]; email=u[2]; role=u[3]; status=u[4]; att=u[5]
                card=tk.Frame(inn,bg=SURFACE); card.pack(fill="x",pady=4,padx=4)
                top2=tk.Frame(card,bg=SURFACE); top2.pack(fill="x",padx=14,pady=(10,2))
                sc = EMERALD if status=="active" else ROSE
                tk.Label(top2,text=f"◉  {uname}",font=("Segoe UI",11,"bold"),
                         bg=SURFACE,fg=TEXT_HI).pack(side="left")
                tk.Label(top2,text=f"● {status}",font=("Segoe UI",9),
                         bg=SURFACE,fg=sc).pack(side="right")
                inf=tk.Frame(card,bg=SURFACE); inf.pack(fill="x",padx=14,pady=(0,6))
                rc = GOLD if role=="admin" else (PLUM if role=="moderator" else TEXT_MID)
                tk.Label(inf,text=f"{email}  ·  ",font=("Segoe UI",9),
                         bg=SURFACE,fg=TEXT_MID).pack(side="left")
                tk.Label(inf,text=role,font=("Segoe UI",9,"bold"),
                         bg=SURFACE,fg=rc).pack(side="left")
                if att>0:
                    tk.Label(inf,text=f"  ·  {att} failed",font=("Segoe UI",9),
                             bg=SURFACE,fg=ROSE).pack(side="left")
                act=tk.Frame(card,bg=SURFACE); act.pack(fill="x",padx=14,pady=(0,10))
                rl=["admin","moderator","user"]; sel=tk.StringVar(value=role)
                rm=tk.OptionMenu(act,sel,*rl)
                rm.config(font=("Segoe UI",9),bg=SURFACE2,fg=TEXT_HI,
                          relief="flat",bd=0,activebackground=HOVER,
                          highlightthickness=0,width=12)
                rm["menu"].config(bg=SURFACE2,fg=TEXT_HI,font=("Segoe UI",9))
                rm.pack(side="left")
                def mkrc(un,v):
                    def do():
                        r=change_user_role(self.current_user,un,v.get())
                        if r=="success": self.show_admin()
                    return do
                tk.Button(act,text="Change Role",font=("Segoe UI",9,"bold"),
                          bg=GOLD,fg=BG,relief="flat",bd=0,cursor="hand2",
                          activebackground=GOLD,command=mkrc(uname,sel),
                          padx=10,pady=4).pack(side="left",padx=6)
                if status=="locked":
                    def mku(un):
                        def do(): unlock_account(self.current_user,un); self.show_admin()
                        return do
                    tk.Button(act,text="⊙ Unlock",font=("Segoe UI",9,"bold"),
                              bg=EMERALD,fg=BG,relief="flat",bd=0,cursor="hand2",
                              activebackground=EMERALD,command=mku(uname),
                              padx=10,pady=4).pack(side="left")
                tk.Frame(inn,bg=BORDER,height=1).pack(fill="x",padx=4)
        except Exception as ex:
            tk.Label(inn,text=f"Error: {ex}",font=("Segoe UI",10),bg=BG,fg=ROSE).pack(pady=20)

        self.btn(outer,"← Dashboard",self.show_dashboard,bg=SURFACE2,fg=TEXT_MID)


# ─────────────────────────────────────────────
#  CREDENTIAL CHECKER
# ─────────────────────────────────────────────
def check_creds(username, password):
    try:
        from password import hash_password
        conn=get_connection(); cur=conn.cursor()
        cur.execute("select user_id,status from users where username=:1",[username])
        user=cur.fetchone()
        if user is None:
            cur.execute("insert into login_attempts(user_id,username_try,status,ip_address,attempt_time,failure_reason) values(null,:1,'failed','127.0.0.1',sysdate,'user not found')",[username])
            conn.commit(); cur.close(); conn.close(); return "not_found"
        uid=user[0]; st=user[1]
        if st=="locked":
            cur.execute("insert into login_attempts(user_id,username_try,status,ip_address,attempt_time,failure_reason) values(:1,:2,'locked','127.0.0.1',sysdate,'account locked')",[uid,username])
            conn.commit(); cur.close(); conn.close(); return "locked"
        cur.execute("select password_hash,salt from passwords where user_id=:1",[uid])
        row=cur.fetchone(); eh=hash_password(password,row[1])
        if eh==row[0]:
            cur.close(); conn.close(); return "success"
        else:
            cur.execute("update users set failed_attempts=failed_attempts+1 where user_id=:1",[uid])
            cur.execute("insert into login_attempts(user_id,username_try,status,ip_address,attempt_time,failure_reason) values(:1,:2,'failed','127.0.0.1',sysdate,'wrong password')",[uid,username])
            conn.commit(); cur.close(); conn.close(); return "wrong"
    except Exception as ex: return f"error:{ex}"


if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()