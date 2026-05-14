import tkinter as tk
from tkinter import font as tkfont
import re


# ── Colour palette ────────────────────────────────────────────
BG          = "#0f0f0f"
DISPLAY_BG  = "#1a1a1a"
BTN_NUM     = "#1e1e1e"
BTN_OP      = "#2a2a2a"
BTN_EQUAL   = "#f5a623"
BTN_CLEAR   = "#c0392b"
TEXT_MAIN   = "#ffffff"
TEXT_SUB    = "#888888"
TEXT_EQUAL  = "#0f0f0f"


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._expression   = ""
        self._result_shown = False

        self._build_fonts()
        self._build_display()
        self._build_buttons()
        self._bind_keyboard()

        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # ── Fonts ─────────────────────────────────────────────────
    def _build_fonts(self):
        self.font_display = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.font_sub     = tkfont.Font(family="Helvetica", size=13)
        self.font_btn     = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.font_btn_sm  = tkfont.Font(family="Helvetica", size=13, weight="bold")

    # ── Display ───────────────────────────────────────────────
    def _build_display(self):
        frame = tk.Frame(self, bg=DISPLAY_BG, pady=18, padx=22)
        frame.pack(fill="x")

        self._sub_var  = tk.StringVar(value="")
        self._main_var = tk.StringVar(value="0")

        tk.Label(
            frame, textvariable=self._sub_var,
            font=self.font_sub, bg=DISPLAY_BG,
            fg=TEXT_SUB, anchor="e"
        ).pack(fill="x")

        tk.Label(
            frame, textvariable=self._main_var,
            font=self.font_display, bg=DISPLAY_BG,
            fg=TEXT_MAIN, anchor="e"
        ).pack(fill="x")

    # ── Buttons ───────────────────────────────────────────────
    def _build_buttons(self):
        frame = tk.Frame(self, bg=BG, padx=10, pady=10)
        frame.pack()

        layout = [
            [("C", "clear"), ("±", "fn"), ("%", "fn"), ("÷", "op")],
            [("7", "num"),   ("8", "num"), ("9", "num"), ("×", "op")],
            [("4", "num"),   ("5", "num"), ("6", "num"), ("−", "op")],
            [("1", "num"),   ("2", "num"), ("3", "num"), ("+", "op")],
            [("0", "zero"),  (".", "num"),               ("=", "eq")],
        ]

        color_map = {
            "num":   (BTN_NUM,   TEXT_MAIN),
            "op":    (BTN_OP,    BTN_EQUAL),
            "eq":    (BTN_EQUAL, TEXT_EQUAL),
            "clear": (BTN_CLEAR, TEXT_MAIN),
            "fn":    (BTN_NUM,   TEXT_MAIN),
            "zero":  (BTN_NUM,   TEXT_MAIN),
        }

        for r, row in enumerate(layout):
            col = 0
            for item in row:
                label, kind = item
                span = 2 if label == "0" else 1
                bg, fg = color_map[kind]
                f = self.font_btn_sm if kind in ("clear", "fn") else self.font_btn

                btn = tk.Button(
                    frame, text=label,
                    font=f, bg=bg, fg=fg,
                    activebackground=self._lighten(bg),
                    activeforeground=TEXT_MAIN,
                    bd=0, relief="flat", cursor="hand2",
                    command=lambda l=label: self._on_press(l)
                )
                btn.grid(
                    row=r, column=col, columnspan=span,
                    padx=4, pady=4, sticky="nsew", ipady=16
                )
                btn.bind("<Enter>", lambda e, b=btn, c=self._lighten(bg): b.config(bg=c))
                btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
                col += span

        for i in range(4):
            frame.columnconfigure(i, weight=1, minsize=74)

    # ── Keyboard ──────────────────────────────────────────────
    def _bind_keyboard(self):
        pairs = {
            "Return": "=", "Escape": "C",
            "plus": "+", "minus": "−",
            "asterisk": "×", "slash": "÷",
        }
        for k, v in pairs.items():
            self.bind(f"<{k}>", lambda e, a=v: self._on_press(a))
        for d in "0123456789":
            self.bind(d, lambda e, a=d: self._on_press(a))
        self.bind(".", lambda e: self._on_press("."))
        self.bind("<BackSpace>", lambda e: self._backspace())

    # ── Logic ─────────────────────────────────────────────────
    _OP_MAP = {"÷": "/", "×": "*", "−": "-"}

    def _on_press(self, label):
        if label == "C":
            self._expression   = ""
            self._result_shown = False
            self._main_var.set("0")
            self._sub_var.set("")

        elif label == "=":
            self._calculate()

        elif label == "±":
            self._toggle_sign()

        elif label == "%":
            self._percent()

        elif label in self._OP_MAP or label == "+":
            sym = self._OP_MAP.get(label, label)
            if self._result_shown:
                self._expression   = self._main_var.get()
                self._result_shown = False
            if self._expression and self._expression[-1] not in "+-*/":
                self._expression += sym
            self._sub_var.set(self._expression)
            self._main_var.set(label)

        else:
            if self._result_shown:
                self._expression   = ""
                self._result_shown = False
            cur = self._last_number()
            if label == "." and "." in cur:
                return
            self._expression += label
            self._main_var.set(self._last_number())
            self._sub_var.set(self._expression)

    def _calculate(self):
        expr = self._expression
        if not expr:
            return
        self._sub_var.set(expr + " =")
        try:
            safe_expr = expr.replace("^", "**")
            result = eval(safe_expr, {"__builtins__": {}})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)
            self._main_var.set(result)
            self._expression   = str(result)
            self._result_shown = True
        except ZeroDivisionError:
            self._main_var.set("Can't ÷ 0")
            self._expression   = ""
            self._result_shown = True
        except Exception:
            self._main_var.set("Error")
            self._expression   = ""
            self._result_shown = True

    def _toggle_sign(self):
        num = self._last_number()
        if not num or num == "0":
            return
        new = num[1:] if num.startswith("-") else "-" + num
        self._expression = self._expression[: len(self._expression) - len(num)] + new
        self._main_var.set(new)

    def _percent(self):
        num = self._last_number()
        if not num:
            return
        try:
            val = float(num) / 100
            val = int(val) if float(val).is_integer() else val
            new = str(val)
            self._expression = self._expression[: len(self._expression) - len(num)] + new
            self._main_var.set(new)
        except Exception:
            pass

    def _backspace(self):
        if self._result_shown:
            return
        self._expression = self._expression[:-1]
        num = self._last_number()
        self._main_var.set(num if num else "0")
        self._sub_var.set(self._expression)

    def _last_number(self):
        parts = re.split(r"(?<!\d)[+\-*/]", self._expression)
        return parts[-1] if parts else ""

    @staticmethod
    def _lighten(hex_color):
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(
            min(255, r + 28),
            min(255, g + 28),
            min(255, b + 28)
        )


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()