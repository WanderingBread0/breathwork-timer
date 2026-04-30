"""Breathwork Timer — Morning Rise (Wim Hof) and Deep Calm (4-7-8)."""
import tkinter as tk
import tkinter.font as tkfont
import time
import math


THEMES = {
    "morning_rise": {
        "bg":        "#1a1612",
        "panel":     "#221d18",
        "circle_lo": "#2a241d",
        "circle_hi": "#4a3e2a",
        "accent":    "#d4a64a",
        "accent_dim":"#8a6e2e",
        "text":      "#ebe1c6",
        "text_dim":  "#8c7d5d",
        "btn_off":   "#2c2620",
    },
    "deep_calm": {
        "bg":        "#141822",
        "panel":     "#1b202c",
        "circle_lo": "#1f2433",
        "circle_hi": "#324464",
        "accent":    "#5b8fc4",
        "accent_dim":"#3a5d82",
        "text":      "#d3dceb",
        "text_dim":  "#6b7a92",
        "btn_off":   "#222836",
    },
}


TECHNIQUES = {
    "morning_rise": {
        "name":   "Morning Rise",
        "tag":    "Wim Hof  -  3 rounds  -  30 breaths each",
        "rounds": 3,
    },
    "deep_calm": {
        "name":   "Deep Calm",
        "tag":    "4-7-8 breathing  -  4 rounds",
        "rounds": 4,
    },
}


CANVAS_SIZE = 380
RADIUS_MIN  = 70
RADIUS_MAX  = 165
TICK_MS     = 33

# Morning Rise (Wim Hof) breath cadence: deep inhale, passive let-go exhale.
MR_INHALE_S        = 3.5
MR_EXHALE_S        = 2.2
MR_RECOVERY_HOLD_S = 15.0
MR_BREATHS         = 30

# Deep Calm (4-7-8) cadence.
DC_INHALE_S = 4.0
DC_HOLD_S   = 7.0
DC_EXHALE_S = 8.0


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


class BreathworkApp:
    def __init__(self, root):
        self.root = root
        root.title("Breathwork Timer")
        root.geometry("520x720")
        root.minsize(480, 680)

        self.technique = "morning_rise"
        self.theme = THEMES[self.technique]

        self.running = False
        self.phase = "idle"
        self.phase_start = 0.0
        self.phase_duration = 0.0
        self.round_idx = 0
        self.breath_idx = 0
        self.exhale_hold_elapsed = 0.0

        self.radius_from = RADIUS_MIN
        self.radius_to = RADIUS_MIN
        self.radius_now = RADIUS_MIN

        self._build_fonts()
        self._build_ui()
        self._apply_theme()
        self._draw_idle()

        root.bind("<space>", lambda e: self._on_space())
        root.bind("<Escape>", lambda e: self.reset())

    def _build_fonts(self):
        self.f_title = tkfont.Font(family="DejaVu Sans", size=22, weight="bold")
        self.f_tag   = tkfont.Font(family="DejaVu Sans", size=11)
        self.f_phase = tkfont.Font(family="DejaVu Sans", size=20, weight="bold")
        self.f_count = tkfont.Font(family="DejaVu Sans", size=58, weight="bold")
        self.f_round = tkfont.Font(family="DejaVu Sans", size=13)
        self.f_btn   = tkfont.Font(family="DejaVu Sans", size=12, weight="bold")
        self.f_hint  = tkfont.Font(family="DejaVu Sans", size=10)

    def _build_ui(self):
        self.root.configure(bg=THEMES["morning_rise"]["bg"])

        self.title_lbl = tk.Label(self.root, text="Morning Rise",
                                  font=self.f_title, bd=0)
        self.title_lbl.pack(pady=(28, 2))

        self.tag_lbl = tk.Label(self.root, font=self.f_tag, bd=0)
        self.tag_lbl.pack(pady=(0, 14))

        self.canvas = tk.Canvas(self.root, width=CANVAS_SIZE, height=CANVAS_SIZE,
                                bd=0, highlightthickness=0)
        self.canvas.pack(pady=(2, 6))

        self.round_lbl = tk.Label(self.root, font=self.f_round, bd=0)
        self.round_lbl.pack(pady=(2, 6))

        self.hint_lbl = tk.Label(self.root, font=self.f_hint, bd=0)
        self.hint_lbl.pack(pady=(0, 10))

        tech_frame = tk.Frame(self.root, bd=0)
        tech_frame.pack(pady=(4, 10))
        self.tech_buttons = {}
        for key in ("morning_rise", "deep_calm"):
            b = tk.Button(tech_frame, text=TECHNIQUES[key]["name"],
                         font=self.f_btn, bd=0, padx=18, pady=8,
                         relief="flat", activeforeground="#ffffff",
                         command=lambda k=key: self.set_technique(k))
            b.pack(side="left", padx=6)
            self.tech_buttons[key] = b

        ctrl_frame = tk.Frame(self.root, bd=0)
        ctrl_frame.pack(pady=(2, 18))
        self.start_btn = tk.Button(ctrl_frame, text="Start", font=self.f_btn,
                                   bd=0, padx=26, pady=10, relief="flat",
                                   activeforeground="#ffffff",
                                   command=self.toggle_start)
        self.start_btn.pack(side="left", padx=6)
        self.reset_btn = tk.Button(ctrl_frame, text="Reset", font=self.f_btn,
                                   bd=0, padx=26, pady=10, relief="flat",
                                   activeforeground="#ffffff",
                                   command=self.reset)
        self.reset_btn.pack(side="left", padx=6)

        self.canvas.bind("<Button-1>", lambda e: self._on_space())

    def _apply_theme(self):
        t = self.theme
        self.root.configure(bg=t["bg"])
        for w in (self.title_lbl, self.tag_lbl, self.round_lbl, self.hint_lbl):
            w.configure(bg=t["bg"], fg=t["text"])
        self.tag_lbl.configure(fg=t["text_dim"])
        self.hint_lbl.configure(fg=t["text_dim"])
        self.canvas.configure(bg=t["bg"])

        for parent in (self.start_btn, self.reset_btn):
            parent.configure(bg=t["panel"], fg=t["text"],
                             activebackground=t["accent_dim"])
        self.start_btn.configure(bg=t["accent"], fg=t["bg"],
                                 activebackground=t["accent_dim"])

        for key, btn in self.tech_buttons.items():
            if key == self.technique:
                btn.configure(bg=t["accent"], fg=t["bg"],
                              activebackground=t["accent_dim"])
            else:
                btn.configure(bg=t["btn_off"], fg=t["text_dim"],
                              activebackground=t["panel"])

        self.title_lbl.configure(text=TECHNIQUES[self.technique]["name"],
                                 fg=t["accent"])
        self.tag_lbl.configure(text=TECHNIQUES[self.technique]["tag"])

    # ------------------------------------------------------------------ controls
    def set_technique(self, key):
        if key == self.technique:
            return
        self.technique = key
        self.theme = THEMES[key]
        self.reset()
        self._apply_theme()

    def toggle_start(self):
        if self.running:
            self.running = False
            self.start_btn.configure(text="Start")
            return
        if self.phase == "idle" or self.phase == "done":
            self._begin_session()
        else:
            self.running = True
            self.phase_start = time.monotonic() - self._phase_progress_pause
            self.start_btn.configure(text="Pause")
            self._tick()

    def reset(self):
        self.running = False
        self.phase = "idle"
        self.round_idx = 0
        self.breath_idx = 0
        self.exhale_hold_elapsed = 0.0
        self.radius_now = RADIUS_MIN
        self.start_btn.configure(text="Start")
        self.hint_lbl.configure(text="")
        self.round_lbl.configure(text="")
        self._draw_idle()

    def _on_space(self):
        if self.phase == "exhale_hold" and self.running:
            self._next_phase()
        elif not self.running and self.phase in ("idle", "done"):
            self.toggle_start()

    # ------------------------------------------------------------- session flow
    def _begin_session(self):
        self.round_idx = 1
        self.breath_idx = 0
        self.running = True
        self.start_btn.configure(text="Pause")
        if self.technique == "morning_rise":
            self._enter_phase("inhale", MR_INHALE_S, RADIUS_MIN, RADIUS_MAX)
        else:
            self._enter_phase("inhale", DC_INHALE_S, RADIUS_MIN, RADIUS_MAX)
        self._tick()

    def _enter_phase(self, name, duration, r_from, r_to):
        self.phase = name
        self.phase_duration = duration
        self.phase_start = time.monotonic()
        self._phase_progress_pause = 0.0
        self.radius_from = r_from
        self.radius_to = r_to

    def _next_phase(self):
        if self.technique == "morning_rise":
            self._next_morning_rise()
        else:
            self._next_deep_calm()

    def _next_morning_rise(self):
        if self.phase == "inhale":
            self._enter_phase("exhale", MR_EXHALE_S, RADIUS_MAX, RADIUS_MIN)
        elif self.phase == "exhale":
            self.breath_idx += 1
            if self.breath_idx < MR_BREATHS:
                self._enter_phase("inhale", MR_INHALE_S, RADIUS_MIN, RADIUS_MAX)
            else:
                self.exhale_hold_elapsed = 0.0
                self._enter_phase("exhale_hold", 0.0, RADIUS_MIN, RADIUS_MIN)
        elif self.phase == "exhale_hold":
            self._enter_phase("inhale_hold", MR_RECOVERY_HOLD_S, RADIUS_MAX, RADIUS_MAX)
            self.radius_now = RADIUS_MAX
        elif self.phase == "inhale_hold":
            if self.round_idx < TECHNIQUES["morning_rise"]["rounds"]:
                self.round_idx += 1
                self.breath_idx = 0
                self._enter_phase("inhale", MR_INHALE_S, RADIUS_MIN, RADIUS_MAX)
            else:
                self._finish()

    def _next_deep_calm(self):
        if self.phase == "inhale":
            self._enter_phase("hold", DC_HOLD_S, RADIUS_MAX, RADIUS_MAX)
        elif self.phase == "hold":
            self._enter_phase("exhale", DC_EXHALE_S, RADIUS_MAX, RADIUS_MIN)
        elif self.phase == "exhale":
            if self.round_idx < TECHNIQUES["deep_calm"]["rounds"]:
                self.round_idx += 1
                self._enter_phase("inhale", DC_INHALE_S, RADIUS_MIN, RADIUS_MAX)
            else:
                self._finish()

    def _finish(self):
        self.running = False
        self.phase = "done"
        self.radius_now = RADIUS_MIN
        self.start_btn.configure(text="Start")
        self.hint_lbl.configure(text="")
        self._draw_done()

    # ------------------------------------------------------------- main loop
    def _tick(self):
        if not self.running:
            return
        now = time.monotonic()
        elapsed = now - self.phase_start

        if self.phase == "exhale_hold":
            self.exhale_hold_elapsed = elapsed
            self.radius_now = RADIUS_MIN
        elif self.phase_duration > 0:
            t = elapsed / self.phase_duration
            if t >= 1.0:
                self._next_phase()
                self.root.after(TICK_MS, self._tick)
                return
            self.radius_now = lerp(self.radius_from, self.radius_to, smooth(t))
        else:
            self.radius_now = self.radius_to

        self._draw()
        self.root.after(TICK_MS, self._tick)

    # ------------------------------------------------------------- drawing
    def _draw_idle(self):
        self.canvas.delete("all")
        cx = cy = CANVAS_SIZE // 2
        t = self.theme
        self._draw_circle(cx, cy, RADIUS_MIN + 25, t["circle_lo"], t["accent_dim"])
        self.canvas.create_text(cx, cy - 6, text="Ready", font=self.f_phase,
                                fill=t["accent"])
        self.canvas.create_text(cx, cy + 28, text="Press Start", font=self.f_hint,
                                fill=t["text_dim"])
        rounds = TECHNIQUES[self.technique]["rounds"]
        self.round_lbl.configure(text=f"Round 0 / {rounds}")
        self.hint_lbl.configure(text="Space = start/release   -   Esc = reset")

    def _draw_done(self):
        self.canvas.delete("all")
        cx = cy = CANVAS_SIZE // 2
        t = self.theme
        self._draw_circle(cx, cy, RADIUS_MIN + 35, t["circle_lo"], t["accent"])
        self.canvas.create_text(cx, cy - 4, text="Complete", font=self.f_phase,
                                fill=t["accent"])
        self.canvas.create_text(cx, cy + 30, text="Well done", font=self.f_hint,
                                fill=t["text_dim"])
        rounds = TECHNIQUES[self.technique]["rounds"]
        self.round_lbl.configure(text=f"Round {rounds} / {rounds}")

    def _draw(self):
        self.canvas.delete("all")
        cx = cy = CANVAS_SIZE // 2
        t = self.theme
        rounds = TECHNIQUES[self.technique]["rounds"]

        outer_r = RADIUS_MAX + 10
        self._draw_ring(cx, cy, outer_r, t["circle_lo"])

        self._draw_circle(cx, cy, int(self.radius_now), t["circle_hi"], t["accent"])

        phase_label, countdown_text, hint = self._phase_text()
        self.canvas.create_text(cx, cy - 56, text=phase_label,
                                font=self.f_phase, fill=t["accent"])
        self.canvas.create_text(cx, cy, text=countdown_text,
                                font=self.f_count, fill=t["text"])

        if self.technique == "morning_rise" and self.phase in ("inhale", "exhale"):
            self.canvas.create_text(cx, cy + 56,
                                    text=f"Breath {self.breath_idx + 1} / {MR_BREATHS}",
                                    font=self.f_hint, fill=t["text_dim"])

        self.round_lbl.configure(text=f"Round {self.round_idx} / {rounds}")
        self.hint_lbl.configure(text=hint)

    def _phase_text(self):
        if self.phase == "inhale":
            remaining = max(0.0, self.phase_duration - (time.monotonic() - self.phase_start))
            return "Inhale", f"{math.ceil(remaining)}", ""
        if self.phase == "exhale":
            remaining = max(0.0, self.phase_duration - (time.monotonic() - self.phase_start))
            return "Exhale", f"{math.ceil(remaining)}", ""
        if self.phase == "hold":
            remaining = max(0.0, self.phase_duration - (time.monotonic() - self.phase_start))
            return "Hold", f"{math.ceil(remaining)}", "Hold full"
        if self.phase == "exhale_hold":
            return ("Exhale Hold",
                    f"{int(self.exhale_hold_elapsed)}",
                    "Click circle / Space when ready to inhale")
        if self.phase == "inhale_hold":
            remaining = max(0.0, self.phase_duration - (time.monotonic() - self.phase_start))
            return "Recovery Hold", f"{math.ceil(remaining)}", "Hold the inhale"
        return "", "", ""

    def _draw_circle(self, cx, cy, r, fill, outline):
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill=fill, outline=outline, width=3)

    def _draw_ring(self, cx, cy, r, color):
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline=color, width=2)


def main():
    root = tk.Tk()
    BreathworkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
