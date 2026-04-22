import ctypes
import json
import queue
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from ctypes import wintypes


CONFIG_PATH = Path(__file__).with_name("autokeyboard_config.json")
DEFAULT_START_DELAY = 3
DEFAULT_INTERVAL_MS = 1000
DEFAULT_SEQUENCE_PAUSE_MS = 1000
KEY_HOLD_SECONDS = 0.03
DEFAULT_USE_SCANCODES = True
KEY_COMBO_OPTIONS = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "space",
    "enter",
    "tab",
    "esc",
    "backspace",
    "delete",
    "insert",
    "home",
    "end",
    "pageup",
    "pagedown",
    "left",
    "right",
    "up",
    "down",
    "ctrl+s",
    "ctrl+c",
    "ctrl+v",
    "ctrl+z",
    "ctrl+shift+s",
    "alt+tab",
    "ctrl+alt+del",
)


@dataclass
class SequenceStep:
    combo: str
    delay_ms: int


def normalize_key_name(token: str) -> str:
    return token.strip().lower().replace(" ", "")


def build_virtual_key_map() -> dict[str, int]:
    mapping = {
        "backspace": 0x08,
        "tab": 0x09,
        "enter": 0x0D,
        "return": 0x0D,
        "shift": 0x10,
        "ctrl": 0x11,
        "control": 0x11,
        "alt": 0x12,
        "pause": 0x13,
        "capslock": 0x14,
        "esc": 0x1B,
        "escape": 0x1B,
        "space": 0x20,
        "pageup": 0x21,
        "pgup": 0x21,
        "pagedown": 0x22,
        "pgdn": 0x22,
        "end": 0x23,
        "home": 0x24,
        "left": 0x25,
        "up": 0x26,
        "right": 0x27,
        "down": 0x28,
        "printscreen": 0x2C,
        "prtsc": 0x2C,
        "insert": 0x2D,
        "ins": 0x2D,
        "delete": 0x2E,
        "del": 0x2E,
        "0": 0x30,
        "1": 0x31,
        "2": 0x32,
        "3": 0x33,
        "4": 0x34,
        "5": 0x35,
        "6": 0x36,
        "7": 0x37,
        "8": 0x38,
        "9": 0x39,
        "win": 0x5B,
        "windows": 0x5B,
        "menu": 0x5D,
        "apps": 0x5D,
        "numpad0": 0x60,
        "numpad1": 0x61,
        "numpad2": 0x62,
        "numpad3": 0x63,
        "numpad4": 0x64,
        "numpad5": 0x65,
        "numpad6": 0x66,
        "numpad7": 0x67,
        "numpad8": 0x68,
        "numpad9": 0x69,
        "multiply": 0x6A,
        "numpadmultiply": 0x6A,
        "add": 0x6B,
        "plus": 0x6B,
        "numpadadd": 0x6B,
        "subtract": 0x6D,
        "minus": 0x6D,
        "numpadsubtract": 0x6D,
        "decimal": 0x6E,
        "numpaddecimal": 0x6E,
        "divide": 0x6F,
        "numpaddivide": 0x6F,
        "numlock": 0x90,
        "scrolllock": 0x91,
        ";": 0xBA,
        "semicolon": 0xBA,
        "=": 0xBB,
        "equals": 0xBB,
        ",": 0xBC,
        "comma": 0xBC,
        "-": 0xBD,
        ".": 0xBE,
        "period": 0xBE,
        "/": 0xBF,
        "slash": 0xBF,
        "`": 0xC0,
        "grave": 0xC0,
        "[": 0xDB,
        "lbracket": 0xDB,
        "\\": 0xDC,
        "backslash": 0xDC,
        "]": 0xDD,
        "rbracket": 0xDD,
        "'": 0xDE,
        "quote": 0xDE,
    }

    for code in range(ord("A"), ord("Z") + 1):
        mapping[chr(code).lower()] = code

    for index in range(1, 25):
        mapping[f"f{index}"] = 0x6F + index

    return mapping


VIRTUAL_KEYS = build_virtual_key_map()
EXTENDED_KEY_CODES = {
    0x21,
    0x22,
    0x23,
    0x24,
    0x25,
    0x26,
    0x27,
    0x28,
    0x2D,
    0x2E,
    0x5B,
    0x5C,
    0x5D,
    0x6F,
    0x90,
}


def parse_key_combo(combo: str) -> list[int]:
    raw_parts = [part for part in combo.split("+") if part.strip()]
    if not raw_parts:
        raise ValueError("Informe ao menos uma tecla.")

    resolved = []
    for raw_part in raw_parts:
        token = normalize_key_name(raw_part)
        if token not in VIRTUAL_KEYS:
            raise ValueError(
                f"Tecla desconhecida: '{raw_part.strip()}'. Use nomes como A, F6, space, enter, ctrl+shift+s."
            )
        resolved.append(VIRTUAL_KEYS[token])
    return resolved


def parse_non_negative_int(value: str, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{label} precisa ser um numero inteiro.") from exc
    if parsed < 0:
        raise ValueError(f"{label} nao pode ser negativo.")
    return parsed


def sleep_interruptible(seconds: float, stop_event: threading.Event) -> bool:
    deadline = time.perf_counter() + max(0.0, seconds)
    while time.perf_counter() < deadline:
        if stop_event.is_set():
            return False
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            break
        time.sleep(min(0.05, remaining))
    return not stop_event.is_set()


class KEYBDINPUT(ctypes.Structure):
    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class MOUSEINPUT(ctypes.Structure):
    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )


class _INPUTUNION(ctypes.Union):
    _fields_ = (
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    )


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = (("type", wintypes.DWORD), ("union", _INPUTUNION))


class KeySender:
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_SCANCODE = 0x0008
    MAPVK_VK_TO_VSC = 0

    def __init__(self) -> None:
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
        self.user32.SendInput.restype = wintypes.UINT
        self.user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)
        self.user32.MapVirtualKeyW.restype = wintypes.UINT

    def _send_virtual_key(self, key_code: int, key_up: bool = False, use_scancodes: bool = False) -> None:
        scan_code = 0
        flags = self.KEYEVENTF_KEYUP if key_up else 0

        if use_scancodes:
            scan_code = self.user32.MapVirtualKeyW(key_code, self.MAPVK_VK_TO_VSC)
            if scan_code == 0:
                raise OSError(f"Nao foi possivel mapear a tecla {key_code} para scan code.")
            flags |= self.KEYEVENTF_SCANCODE
            if key_code in EXTENDED_KEY_CODES:
                flags |= self.KEYEVENTF_EXTENDEDKEY

        payload = KEYBDINPUT(
            wVk=0 if use_scancodes else key_code,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        )
        event = INPUT(type=self.INPUT_KEYBOARD, ki=payload)
        sent = self.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))
        if sent != 1:
            error_code = ctypes.get_last_error()
            raise OSError(f"Falha ao enviar tecla para o Windows. Codigo: {error_code}")

    def send_combo(self, combo: str, use_scancodes: bool = False) -> None:
        virtual_keys = parse_key_combo(combo)
        for key_code in virtual_keys:
            self._send_virtual_key(key_code, key_up=False, use_scancodes=use_scancodes)
        time.sleep(KEY_HOLD_SECONDS)
        for key_code in reversed(virtual_keys):
            self._send_virtual_key(key_code, key_up=True, use_scancodes=use_scancodes)


class AutoKeyboardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Auto Keyboard")
        self.root.geometry("820x610")
        self.root.minsize(760, 560)

        self.single_combo_var = tk.StringVar(value="F6")
        self.interval_var = tk.StringVar(value=str(DEFAULT_INTERVAL_MS))
        self.start_delay_var = tk.StringVar(value=str(DEFAULT_START_DELAY))
        self.sequence_pause_var = tk.StringVar(value=str(DEFAULT_SEQUENCE_PAUSE_MS))
        self.use_scancodes_var = tk.BooleanVar(value=DEFAULT_USE_SCANCODES)
        self.step_combo_var = tk.StringVar()
        self.step_delay_var = tk.StringVar(value="500")
        self.status_var = tk.StringVar(value="Pronto para iniciar.")
        self.mode_hint_var = tk.StringVar(value="Modo atual: tecla unica")

        self.sequence_steps: list[SequenceStep] = []
        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self.sender = KeySender()

        self._build_styles()
        self._build_layout()
        self._load_config()
        self._refresh_sequence_table()
        self._poll_messages()
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#f3efe7")
        style.configure("Panel.TLabelframe", background="#f3efe7", borderwidth=1)
        style.configure("Panel.TLabelframe.Label", background="#f3efe7", foreground="#2b2926")
        style.configure("Body.TLabel", background="#f3efe7", foreground="#2b2926")
        style.configure("Hint.TLabel", background="#f3efe7", foreground="#6d5f50")
        style.configure("Accent.TButton", background="#1d6b57", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#175544")])

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="Root.TFrame", padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        hero = ttk.Frame(container, style="Root.TFrame")
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        hero.columnconfigure(0, weight=1)

        ttk.Label(
            hero,
            text="Auto Keyboard",
            font=("Segoe UI Semibold", 20),
            style="Body.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            hero,
            text=(
                "Configure uma tecla repetida ou monte uma sequencia. "
                "Depois de iniciar, troque o foco para o programa alvo durante a contagem."
            ),
            style="Hint.TLabel",
            wraplength=760,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        config_panel = ttk.LabelFrame(container, text="Execucao rapida", style="Panel.TLabelframe", padding=14)
        config_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        config_panel.columnconfigure(1, weight=1)

        ttk.Label(config_panel, text="Tecla ou atalho", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            config_panel,
            textvariable=self.single_combo_var,
            values=KEY_COMBO_OPTIONS,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(config_panel, text="Intervalo (ms)", style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(config_panel, textvariable=self.interval_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(config_panel, text="Contagem inicial (s)", style="Body.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(config_panel, textvariable=self.start_delay_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(config_panel, text="Pausa apos sequencia (ms)", style="Body.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(config_panel, textvariable=self.sequence_pause_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(
            config_panel,
            text="Exemplos: A, space, enter, ctrl+s, alt+tab, f6",
            style="Hint.TLabel",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Checkbutton(
            config_panel,
            text="Usar scan code (melhor para jogos)",
            variable=self.use_scancodes_var,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))

        sequence_panel = ttk.LabelFrame(container, text="Sequencia personalizada", style="Panel.TLabelframe", padding=14)
        sequence_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        sequence_panel.columnconfigure(0, weight=1)
        sequence_panel.rowconfigure(1, weight=1)

        editor = ttk.Frame(sequence_panel, style="Root.TFrame")
        editor.grid(row=0, column=0, sticky="ew")
        editor.columnconfigure(0, weight=2)
        editor.columnconfigure(1, weight=1)

        ttk.Label(editor, text="Tecla ou atalho", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(editor, text="Aguardar depois (ms)", style="Body.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Combobox(
            editor,
            textvariable=self.step_combo_var,
            values=KEY_COMBO_OPTIONS,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Entry(editor, textvariable=self.step_delay_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))

        action_bar = ttk.Frame(sequence_panel, style="Root.TFrame")
        action_bar.grid(row=2, column=0, sticky="ew", pady=(10, 10))
        for index in range(4):
            action_bar.columnconfigure(index, weight=1)

        ttk.Button(action_bar, text="Adicionar", command=self._add_step, style="Accent.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(action_bar, text="Atualizar", command=self._update_selected_step).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(action_bar, text="Remover", command=self._remove_selected_step).grid(row=0, column=2, sticky="ew", padx=6)
        ttk.Button(action_bar, text="Limpar", command=self._clear_sequence).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        self.sequence_table = ttk.Treeview(
            sequence_panel,
            columns=("combo", "delay"),
            show="headings",
            height=10,
        )
        self.sequence_table.heading("combo", text="Tecla / atalho")
        self.sequence_table.heading("delay", text="Espera depois (ms)")
        self.sequence_table.column("combo", width=220, anchor="w")
        self.sequence_table.column("delay", width=120, anchor="center")
        self.sequence_table.grid(row=1, column=0, sticky="nsew")
        self.sequence_table.bind("<<TreeviewSelect>>", self._populate_editor_from_selection)

        bottom_panel = ttk.LabelFrame(container, text="Controle", style="Panel.TLabelframe", padding=14)
        bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        bottom_panel.columnconfigure(0, weight=1)
        bottom_panel.columnconfigure(1, weight=1)
        bottom_panel.columnconfigure(2, weight=1)

        ttk.Label(bottom_panel, textvariable=self.mode_hint_var, style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(bottom_panel, textvariable=self.status_var, style="Hint.TLabel", wraplength=540).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.start_button = ttk.Button(bottom_panel, text="Iniciar", command=self.start, style="Accent.TButton")
        self.start_button.grid(row=0, column=2, sticky="ew", padx=(12, 6))

        self.stop_button = ttk.Button(bottom_panel, text="Parar", command=self.stop)
        self.stop_button.grid(row=1, column=2, sticky="ew", padx=(12, 6), pady=(8, 0))
        self.stop_button.state(["disabled"])

    def _poll_messages(self) -> None:
        try:
            while True:
                level, message = self.messages.get_nowait()
                self.status_var.set(message)
                if level == "stopped":
                    self._set_running(False)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_messages)

    def _set_running(self, running: bool) -> None:
        if running:
            self.start_button.state(["disabled"])
            self.stop_button.state(["!disabled"])
        else:
            self.start_button.state(["!disabled"])
            self.stop_button.state(["disabled"])

    def _selected_index(self) -> int | None:
        selection = self.sequence_table.selection()
        if not selection:
            return None
        return self.sequence_table.index(selection[0])

    def _populate_editor_from_selection(self, _event: object | None = None) -> None:
        index = self._selected_index()
        if index is None:
            return
        step = self.sequence_steps[index]
        self.step_combo_var.set(step.combo)
        self.step_delay_var.set(str(step.delay_ms))

    def _refresh_sequence_table(self) -> None:
        for item in self.sequence_table.get_children():
            self.sequence_table.delete(item)

        for step in self.sequence_steps:
            self.sequence_table.insert("", "end", values=(step.combo, step.delay_ms))

        if self.sequence_steps:
            self.mode_hint_var.set("Modo atual: sequencia personalizada")
        else:
            self.mode_hint_var.set("Modo atual: tecla unica")

    def _validate_step_inputs(self) -> SequenceStep:
        combo = self.step_combo_var.get().strip()
        delay_ms = parse_non_negative_int(self.step_delay_var.get().strip(), "Espera depois")
        parse_key_combo(combo)
        return SequenceStep(combo=combo, delay_ms=delay_ms)

    def _add_step(self) -> None:
        try:
            step = self._validate_step_inputs()
        except ValueError as exc:
            messagebox.showerror("Sequencia invalida", str(exc), parent=self.root)
            return

        self.sequence_steps.append(step)
        self._refresh_sequence_table()
        self._save_config()
        self.step_combo_var.set("")
        self.step_delay_var.set("500")
        self.status_var.set("Passo adicionado na sequencia.")

    def _update_selected_step(self) -> None:
        index = self._selected_index()
        if index is None:
            messagebox.showinfo("Atualizar passo", "Selecione um passo para atualizar.", parent=self.root)
            return

        try:
            step = self._validate_step_inputs()
        except ValueError as exc:
            messagebox.showerror("Sequencia invalida", str(exc), parent=self.root)
            return

        self.sequence_steps[index] = step
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set("Passo atualizado.")

    def _remove_selected_step(self) -> None:
        index = self._selected_index()
        if index is None:
            messagebox.showinfo("Remover passo", "Selecione um passo para remover.", parent=self.root)
            return

        del self.sequence_steps[index]
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set("Passo removido.")

    def _clear_sequence(self) -> None:
        self.sequence_steps.clear()
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set("Sequencia limpa. O app voltou para o modo de tecla unica.")

    def _validate_run_inputs(self) -> tuple[str, int, int, int, bool, list[SequenceStep]]:
        combo = self.single_combo_var.get().strip()
        interval_ms = parse_non_negative_int(self.interval_var.get().strip(), "Intervalo")
        start_delay = parse_non_negative_int(self.start_delay_var.get().strip(), "Contagem inicial")
        sequence_pause = parse_non_negative_int(self.sequence_pause_var.get().strip(), "Pausa apos sequencia")
        use_scancodes = self.use_scancodes_var.get()

        if self.sequence_steps:
            for step in self.sequence_steps:
                parse_key_combo(step.combo)
            return combo, interval_ms, start_delay, sequence_pause, use_scancodes, list(self.sequence_steps)

        parse_key_combo(combo)
        return combo, interval_ms, start_delay, sequence_pause, use_scancodes, []

    def start(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return

        try:
            combo, interval_ms, start_delay, sequence_pause, use_scancodes, sequence_steps = self._validate_run_inputs()
        except ValueError as exc:
            messagebox.showerror("Configuracao invalida", str(exc), parent=self.root)
            return

        self._save_config()
        self.stop_event.clear()
        self._set_running(True)
        mode_label = "scan code" if use_scancodes else "virtual key"
        self.messages.put(("info", f"Automacao iniciada em modo {mode_label}. Troque o foco para a janela alvo durante a contagem."))
        self.worker_thread = threading.Thread(
            target=self._run_worker,
            args=(combo, interval_ms, start_delay, sequence_pause, use_scancodes, sequence_steps),
            daemon=True,
        )
        self.worker_thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.messages.put(("info", "Parando automacao..."))

    def _run_worker(
        self,
        combo: str,
        interval_ms: int,
        start_delay: int,
        sequence_pause: int,
        use_scancodes: bool,
        sequence_steps: list[SequenceStep],
    ) -> None:
        try:
            for remaining in range(start_delay, 0, -1):
                self.messages.put(("info", f"Iniciando em {remaining}s. Deixe a janela alvo em foco."))
                if not sleep_interruptible(1.0, self.stop_event):
                    self.messages.put(("stopped", "Automacao interrompida antes de iniciar."))
                    return

            if sequence_steps:
                mode_label = "scan code" if use_scancodes else "virtual key"
                self.messages.put(("info", f"Sequencia em execucao ({mode_label})."))
                while not self.stop_event.is_set():
                    for step in sequence_steps:
                        self.sender.send_combo(step.combo, use_scancodes=use_scancodes)
                        if not sleep_interruptible(step.delay_ms / 1000, self.stop_event):
                            self.messages.put(("stopped", "Automacao interrompida."))
                            return
                    if sequence_pause > 0 and not sleep_interruptible(sequence_pause / 1000, self.stop_event):
                        self.messages.put(("stopped", "Automacao interrompida."))
                        return
            else:
                mode_label = "scan code" if use_scancodes else "virtual key"
                self.messages.put(("info", f"Tecla '{combo}' em repeticao ({mode_label})."))
                while not self.stop_event.is_set():
                    self.sender.send_combo(combo, use_scancodes=use_scancodes)
                    if not sleep_interruptible(interval_ms / 1000, self.stop_event):
                        self.messages.put(("stopped", "Automacao interrompida."))
                        return
        except OSError as exc:
            self.messages.put(("stopped", f"Falha ao enviar tecla: {exc}"))
        except Exception as exc:
            self.messages.put(("stopped", f"Erro inesperado: {exc}"))
        else:
            self.messages.put(("stopped", "Automacao finalizada."))

    def _save_config(self) -> None:
        payload = {
            "single_combo": self.single_combo_var.get().strip(),
            "interval_ms": self.interval_var.get().strip(),
            "start_delay": self.start_delay_var.get().strip(),
            "sequence_pause": self.sequence_pause_var.get().strip(),
            "use_scancodes": self.use_scancodes_var.get(),
            "sequence_steps": [asdict(step) for step in self.sequence_steps],
        }
        CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load_config(self) -> None:
        if not CONFIG_PATH.exists():
            return

        try:
            payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.status_var.set("Nao foi possivel carregar a configuracao anterior.")
            return

        self.single_combo_var.set(payload.get("single_combo", self.single_combo_var.get()))
        self.interval_var.set(str(payload.get("interval_ms", self.interval_var.get())))
        self.start_delay_var.set(str(payload.get("start_delay", self.start_delay_var.get())))
        self.sequence_pause_var.set(str(payload.get("sequence_pause", self.sequence_pause_var.get())))
        self.use_scancodes_var.set(bool(payload.get("use_scancodes", self.use_scancodes_var.get())))

        loaded_steps = []
        for raw_step in payload.get("sequence_steps", []):
            combo = str(raw_step.get("combo", "")).strip()
            delay = raw_step.get("delay_ms", 0)
            try:
                delay_ms = int(delay)
            except (TypeError, ValueError):
                continue
            if combo:
                loaded_steps.append(SequenceStep(combo=combo, delay_ms=max(0, delay_ms)))
        self.sequence_steps = loaded_steps

    def _handle_close(self) -> None:
        self.stop_event.set()
        self._save_config()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    AutoKeyboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
