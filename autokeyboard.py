import ctypes
import json
import locale
import queue
import threading
import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ctypes import wintypes


CONFIG_PATH = Path(__file__).with_name("autokeyboard_config.json")
STRINGS_PATH = Path(__file__).with_name("strings.json")
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ENGLISH_FLAG_PATH = ASSETS_DIR / "english.png"
PORTUGUESE_FLAG_PATH = ASSETS_DIR / "portuguese.png"
DEFAULT_START_DELAY = 3
DEFAULT_INTERVAL_MS = 1000
DEFAULT_SEQUENCE_PAUSE_MS = 1000
KEY_HOLD_SECONDS = 0.03
DEFAULT_USE_SCANCODES = True
ENGLISH_LANGUAGE = "en"
PORTUGUESE_LANGUAGE = "pt-BR"
LANGUAGE_ASSETS = {
    "pt-BR": PORTUGUESE_FLAG_PATH,
    "en": ENGLISH_FLAG_PATH,
}
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

DEFAULT_TRANSLATIONS = {
    "pt-BR": {
        "app": {"title": "Auto Keyboard", "version": "v1.0"},
        "status": {
            "ready": "Pronto para iniciar.",
            "language_changed": "Idioma alterado para {language_name}.",
            "profile_saved": "Perfil salvo no painel atual.",
            "profile_imported": "Perfil importado com sucesso.",
            "profile_exported": "Perfil exportado com sucesso.",
            "profile_import_cancelled": "Importação cancelada.",
            "profile_export_cancelled": "Exportação cancelada.",
            "step_added": "Passo adicionado na sequência.",
            "step_updated": "Passo atualizado.",
            "step_removed": "Passo removido.",
            "sequence_cleared": "Sequência limpa. O app voltou para o modo de tecla única.",
            "stopping": "Parando automação...",
            "starting_mode": "Automação iniciada em modo {mode_label}. Troque o foco para a janela alvo durante a contagem.",
            "countdown": "Iniciando em {remaining}s. Deixe a janela alvo em foco.",
            "stopped_before_start": "Automação interrompida antes de iniciar.",
            "sequence_running": "Sequência em execução ({mode_label}).",
            "single_running": "Tecla '{combo}' em repeticao ({mode_label}).",
            "automation_stopped": "Automação interrompida.",
            "send_failure": "Falha ao enviar tecla: {error}",
            "unexpected_error": "Erro inesperado: {error}",
            "automation_finished": "Automação finalizada.",
            "config_load_failed": "Não foi possível carregar a configuração anterior."
        },
        "labels": {
            "mode_single": "MODO TECLA ÚNICA",
            "mode_sequence": "MODO SEQUÊNCIA ATIVO",
            "profile_name": "Profile1",
            "profile_state_ready": "PRONTO",
            "profile_state_active": "ATIVO",
            "profile_meta": "Perfil de automação precisa",
            "engine_scan_code": "SCAN CODE",
            "engine_virtual_key": "VIRTUAL KEY",
            "brand": "Auto Keyboard",
            "nav_title": "Slots da sequência",
            "metric_actions": "TOTAL DE AÇÕES",
            "metric_cycle": "TEMPO DE CICLO",
            "panel_sequence_title": "CONSTRUTOR DE SEQUÊNCIA",
            "panel_sequence_subtitle": "Monte e ajuste sua rotação de teclas com módulos inspirados em hardware.",
            "panel_execution_title": "EXECUÇÃO DO SISTEMA",
            "panel_execution_subtitle": "Controles de alto contraste com telemetria do motor em tempo real.",
            "panel_config_title": "PARÂMETROS DE CONFIGURAÇÃO",
            "panel_config_subtitle": "Tempos, fallback e compatibilidade do motor de automação.",
            "header_key_hotkey": "TECLA / ATALHO",
            "header_delay": "ATRASO",
            "table_id": "ID",
            "table_action": "AÇÃO",
            "table_wait": "ESPERA",
            "button_remove": "REMOVER",
            "button_import": "IMPORTAR",
            "button_export": "EXPORTAR",
            "button_add_action": "ADICIONAR AÇÃO",
            "button_add": "ADD",
            "button_update": "UPDATE",
            "button_up": "UP",
            "button_down": "DOWN",
            "button_clear": "CLEAR",
            "button_start": "INICIAR",
            "button_stop": "PARAR",
            "label_global_interval": "INTERVALO GLOBAL",
            "label_initial_delay": "ATRASO INICIAL",
            "label_sequence_loop_pause": "PAUSA DO LOOP",
            "label_single_key_fallback": "TECLA DE FALLBACK",
            "checkbox_scancode": "Usar scan code (melhor para jogos)",
            "unit_ms": "ms",
            "unit_sec": "seg",
            "summary_no_fallback": "Sem tecla de fallback",
            "summary_profile_meta": "{actions} ação(ões) configurada(s) • Fallback: {combo_display} • {mode_name}",
            "mode_scan_code_lower": "scan code",
            "mode_virtual_key_lower": "virtual key",
            "language_portuguese": "Português",
            "language_english": "English"
        },
        "dialogs": {
            "move_title": "Mover passo",
            "move_select": "Selecione um passo para mover.",
            "invalid_sequence_title": "Sequência inválida",
            "update_title": "Atualizar passo",
            "update_select": "Selecione um passo para atualizar.",
            "remove_title": "Remover passo",
            "remove_select": "Selecione um passo para remover.",
            "invalid_config_title": "Configuração inválida",
            "import_title": "Importar perfil",
            "export_title": "Exportar perfil"
        },
        "validation": {
            "missing_key": "Informe ao menos uma tecla.",
            "unknown_key": "Tecla desconhecida: '{key}'. Use nomes como A, F6, space, enter, ctrl+shift+s.",
            "integer_required": "{label} precisa ser um número inteiro.",
            "non_negative_required": "{label} não pode ser negativo.",
            "label_step_delay": "Espera depois",
            "label_interval": "Intervalo",
            "label_start_delay": "Contagem inicial",
            "label_sequence_pause": "Pausa após sequência",
            "scancode_mapping_failed": "Não foi possível mapear a tecla {key_code} para scan code.",
            "send_input_failed": "Falha ao enviar tecla para o Windows. Codigo: {error_code}",
            "profile_invalid": "O arquivo de perfil é inválido.",
            "profile_export_failed": "Não foi possível exportar o perfil: {error}"
        }
    },
    "en": {
        "app": {"title": "Auto Keyboard", "version": "v1.0"},
        "status": {
            "ready": "Ready to start.",
            "language_changed": "Language changed to {language_name}.",
            "profile_saved": "Profile saved to the current panel.",
            "profile_imported": "Profile imported successfully.",
            "profile_exported": "Profile exported successfully.",
            "profile_import_cancelled": "Import cancelled.",
            "profile_export_cancelled": "Export cancelled.",
            "step_added": "Step added to the sequence.",
            "step_updated": "Step updated.",
            "step_removed": "Step removed.",
            "sequence_cleared": "Sequence cleared. The app returned to single-key mode.",
            "stopping": "Stopping automation...",
            "starting_mode": "Automation started in {mode_label} mode. Switch focus to the target window during the countdown.",
            "countdown": "Starting in {remaining}s. Keep the target window focused.",
            "stopped_before_start": "Automation stopped before starting.",
            "sequence_running": "Sequence running ({mode_label}).",
            "single_running": "Repeating key '{combo}' ({mode_label}).",
            "automation_stopped": "Automation stopped.",
            "send_failure": "Failed to send key: {error}",
            "unexpected_error": "Unexpected error: {error}",
            "automation_finished": "Automation finished.",
            "config_load_failed": "Could not load the previous configuration."
        },
        "labels": {
            "mode_single": "SINGLE KEY FALLBACK",
            "mode_sequence": "SEQUENCE MODE ACTIVE",
            "profile_name": "Profile1",
            "profile_state_ready": "READY",
            "profile_state_active": "ACTIVE",
            "profile_meta": "Precision automation profile",
            "engine_scan_code": "SCAN CODE",
            "engine_virtual_key": "VIRTUAL KEY",
            "brand": "Auto Keyboard",
            "nav_title": "Sequence slots",
            "metric_actions": "TOTAL ACTIONS",
            "metric_cycle": "CYCLE TIME",
            "panel_sequence_title": "SEQUENCE_BUILDER",
            "panel_sequence_subtitle": "Build and tune your key rotation sequence with hardware-style modules.",
            "panel_execution_title": "SYSTEM_EXECUTION",
            "panel_execution_subtitle": "High-contrast controls with live engine telemetry.",
            "panel_config_title": "CONFIG PARAMETERS",
            "panel_config_subtitle": "Precision timing, fallback behavior, and compatibility settings.",
            "header_key_hotkey": "KEY / HOTKEY",
            "header_delay": "DELAY",
            "table_id": "ID",
            "table_action": "ACTION",
            "table_wait": "WAIT",
            "button_remove": "REMOVE",
            "button_import": "IMPORT",
            "button_export": "EXPORT",
            "button_add_action": "ADD ACTION",
            "button_add": "ADD",
            "button_update": "UPDATE",
            "button_up": "UP",
            "button_down": "DOWN",
            "button_clear": "CLEAR",
            "button_start": "START",
            "button_stop": "STOP",
            "label_global_interval": "GLOBAL INTERVAL",
            "label_initial_delay": "INITIAL DELAY",
            "label_sequence_loop_pause": "SEQUENCE LOOP PAUSE",
            "label_single_key_fallback": "SINGLE KEY FALLBACK",
            "checkbox_scancode": "Use scan code (better for games)",
            "unit_ms": "ms",
            "unit_sec": "sec",
            "summary_no_fallback": "No fallback key",
            "summary_profile_meta": "{actions} action(s) configured • Fallback: {combo_display} • {mode_name}",
            "mode_scan_code_lower": "scan code",
            "mode_virtual_key_lower": "virtual key",
            "language_portuguese": "Portuguese",
            "language_english": "English"
        },
        "dialogs": {
            "move_title": "Move step",
            "move_select": "Select a step to move.",
            "invalid_sequence_title": "Invalid sequence",
            "update_title": "Update step",
            "update_select": "Select a step to update.",
            "remove_title": "Remove step",
            "remove_select": "Select a step to remove.",
            "invalid_config_title": "Invalid configuration",
            "import_title": "Import profile",
            "export_title": "Export profile"
        },
        "validation": {
            "missing_key": "Enter at least one key.",
            "unknown_key": "Unknown key: '{key}'. Use names like A, F6, space, enter, ctrl+shift+s.",
            "integer_required": "{label} must be an integer.",
            "non_negative_required": "{label} cannot be negative.",
            "label_step_delay": "Delay after",
            "label_interval": "Interval",
            "label_start_delay": "Initial countdown",
            "label_sequence_pause": "Sequence pause",
            "scancode_mapping_failed": "Could not map key {key_code} to scan code.",
            "send_input_failed": "Failed to send key to Windows. Code: {error_code}",
            "profile_invalid": "The profile file is invalid.",
            "profile_export_failed": "Could not export the profile: {error}"
        }
    }
}


def _merge_strings(base: dict, override: dict) -> dict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_strings(merged[key], value)
        else:
            merged[key] = value
    return merged


def detect_system_language() -> str:
    locale_candidates: list[str] = []

    try:
        language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except (AttributeError, OSError):
        language_id = 0

    if language_id:
        windows_locale = locale.windows_locale.get(language_id)
        if windows_locale:
            locale_candidates.append(windows_locale)

    for getter_name in ("getlocale", "getdefaultlocale"):
        getter = getattr(locale, getter_name, None)
        if getter is None:
            continue
        try:
            values = getter()
        except (ValueError, TypeError):
            continue

        if isinstance(values, tuple):
            for value in values:
                if isinstance(value, str) and value:
                    locale_candidates.append(value)
        elif isinstance(values, str) and values:
            locale_candidates.append(values)

    for locale_name in locale_candidates:
        normalized = locale_name.lower().replace("_", "-")
        if normalized.startswith("pt"):
            return PORTUGUESE_LANGUAGE

    return ENGLISH_LANGUAGE


DEFAULT_LANGUAGE = detect_system_language()
APP_TRANSLATIONS = deepcopy(DEFAULT_TRANSLATIONS)
APP_STRINGS = deepcopy(DEFAULT_TRANSLATIONS[DEFAULT_LANGUAGE])
CURRENT_LANGUAGE = DEFAULT_LANGUAGE


def load_app_strings(language: str | None = None) -> dict:
    global APP_TRANSLATIONS, APP_STRINGS, CURRENT_LANGUAGE
    translations = deepcopy(DEFAULT_TRANSLATIONS)

    if STRINGS_PATH.exists():
        try:
            payload = json.loads(STRINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = None

        if isinstance(payload, dict):
            for locale, values in payload.items():
                if isinstance(values, dict):
                    base = translations.get(locale, {})
                    translations[locale] = _merge_strings(base, values)

    selected_language = language or CURRENT_LANGUAGE
    if selected_language not in translations:
        selected_language = DEFAULT_LANGUAGE

    APP_TRANSLATIONS = translations
    APP_STRINGS = _merge_strings(translations[DEFAULT_LANGUAGE], translations[selected_language])
    CURRENT_LANGUAGE = selected_language
    return APP_STRINGS


def tr(path: str, **kwargs: object) -> str:
    value: object = APP_STRINGS
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return path
        value = value[part]
    if not isinstance(value, str):
        return path
    return value.format(**kwargs) if kwargs else value


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
        raise ValueError(tr("validation.missing_key"))

    resolved = []
    for raw_part in raw_parts:
        token = normalize_key_name(raw_part)
        if token not in VIRTUAL_KEYS:
            raise ValueError(tr("validation.unknown_key", key=raw_part.strip()))
        resolved.append(VIRTUAL_KEYS[token])
    return resolved


def parse_non_negative_int(value: str, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(tr("validation.integer_required", label=label)) from exc
    if parsed < 0:
        raise ValueError(tr("validation.non_negative_required", label=label))
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
                raise OSError(tr("validation.scancode_mapping_failed", key_code=key_code))
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
            raise OSError(tr("validation.send_input_failed", error_code=error_code))

    def send_combo(self, combo: str, use_scancodes: bool = False) -> None:
        virtual_keys = parse_key_combo(combo)
        for key_code in virtual_keys:
            self._send_virtual_key(key_code, key_up=False, use_scancodes=use_scancodes)
        time.sleep(KEY_HOLD_SECONDS)
        for key_code in reversed(virtual_keys):
            self._send_virtual_key(key_code, key_up=True, use_scancodes=use_scancodes)


class AutoKeyboardApp:
    def __init__(self, root: tk.Tk) -> None:
        load_app_strings()
        self.current_language = CURRENT_LANGUAGE
        self.language_images: dict[str, tk.PhotoImage] = {}
        self._responsive_mode = ""
        self._resize_after_id: str | None = None
        self.root = root
        self.root.title(tr("app.title"))
        self.root.geometry("1360x860")
        self.root.minsize(920, 860)

        self.single_combo_var = tk.StringVar(value="F6")
        self.interval_var = tk.StringVar(value=str(DEFAULT_INTERVAL_MS))
        self.start_delay_var = tk.StringVar(value=str(DEFAULT_START_DELAY))
        self.sequence_pause_var = tk.StringVar(value=str(DEFAULT_SEQUENCE_PAUSE_MS))
        self.use_scancodes_var = tk.BooleanVar(value=DEFAULT_USE_SCANCODES)
        self.step_combo_var = tk.StringVar()
        self.step_delay_var = tk.StringVar(value="500")
        self.status_var = tk.StringVar(value=tr("status.ready"))
        self.mode_hint_var = tk.StringVar(value=tr("labels.mode_single"))
        self.profile_name_var = tk.StringVar(value=tr("labels.profile_name"))
        self.profile_state_var = tk.StringVar(value=tr("labels.profile_state_ready"))
        self.profile_meta_var = tk.StringVar(value=tr("labels.profile_meta"))
        self.actions_count_var = tk.StringVar(value="0")
        self.cycle_time_var = tk.StringVar(value="0ms")
        self.engine_mode_var = tk.StringVar(value=tr("labels.engine_scan_code"))

        self.sequence_steps: list[SequenceStep] = []
        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self.sender = KeySender()
        self.profile_name_entry_var = tk.StringVar(value=self.profile_name_var.get())
        self._profile_name_before_edit = self.profile_name_var.get()

        self._build_styles()
        self._build_layout()
        self._load_config()
        self._refresh_sequence_table()
        self._refresh_dashboard_summary()
        self._poll_messages()
        self.root.bind("<Configure>", self._handle_root_configure)
        self.root.after_idle(lambda: self._apply_responsive_layout(force=True))
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

        for variable in (
            self.single_combo_var,
            self.interval_var,
            self.start_delay_var,
            self.sequence_pause_var,
            self.use_scancodes_var,
        ):
            variable.trace_add("write", lambda *_args: self._refresh_dashboard_summary())

    def _build_styles(self) -> None:
        self.colors = {
            "background": "#081425",
            "panel": "#152031",
            "panel_high": "#1f2a3c",
            "panel_line": "#2a3548",
            "field": "#091527",
            "disabled_button": "#0d1624",
            "text": "#d8e3fb",
            "muted": "#93a1bd",
            "subtle": "#6d7b98",
            "accent": "#35c8bb",
            "accent_soft": "#1f8f86",
            "danger": "#93000a",
            "danger_soft": "#c44751",
            "outline": "#324156",
        }
        self.fonts = {
            "brand": ("Space Grotesk", 18, "bold"),
            "nav": ("Space Grotesk", 12, "bold"),
            "headline": ("Space Grotesk", 18, "bold"),
            "section": ("Space Grotesk", 11, "bold"),
            "body": ("Inter", 12),
            "body_bold": ("Inter", 12, "bold"),
            "metric": ("Space Grotesk", 18, "bold"),
            "mono": ("Space Grotesk", 12, "bold"),
        }

        style = ttk.Style()
        style.theme_use("clam")
        self.root.configure(bg=self.colors["background"])
        self.root.option_add("*TCombobox*Listbox.background", self.colors["field"])
        self.root.option_add("*TCombobox*Listbox.foreground", self.colors["text"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.colors["panel_line"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.colors["text"])
        self.root.option_add("*TCombobox*Listbox.borderWidth", 0)

        style.configure(
            "Console.TEntry",
            fieldbackground=self.colors["field"],
            background=self.colors["field"],
            foreground=self.colors["text"],
            bordercolor=self.colors["outline"],
            insertcolor=self.colors["accent"],
            lightcolor=self.colors["outline"],
            darkcolor=self.colors["outline"],
            padding=10,
        )
        style.configure(
            "Console.TCombobox",
            fieldbackground=self.colors["field"],
            background=self.colors["field"],
            foreground=self.colors["text"],
            bordercolor=self.colors["outline"],
            lightcolor=self.colors["outline"],
            darkcolor=self.colors["outline"],
            arrowbackground=self.colors["field"],
            arrowcolor=self.colors["accent"],
            insertcolor=self.colors["accent"],
            padding=8,
        )
        style.map(
            "Console.TCombobox",
            background=[("active", self.colors["field"]), ("pressed", self.colors["field"])],
            fieldbackground=[("active", self.colors["field"]), ("pressed", self.colors["field"]), ("readonly", self.colors["field"])],
            arrowbackground=[("active", self.colors["field"]), ("pressed", self.colors["field"]), ("readonly", self.colors["field"])],
            selectbackground=[("readonly", self.colors["field"])],
            selectforeground=[("readonly", self.colors["text"])],
        )
        style.configure(
            "Console.Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=self.fonts["body"],
        )
        style.layout(
            "Console.Treeview",
            [("Treeview.treearea", {"sticky": "nswe"})],
        )
        style.configure(
            "Console.Treeview.Heading",
            background=self.colors["panel_high"],
            foreground=self.colors["muted"],
            borderwidth=0,
            relief="flat",
            font=self.fonts["section"],
        )
        style.map(
            "Console.Treeview.Heading",
            background=[("active", self.colors["panel_line"])],
            foreground=[("active", self.colors["text"])],
        )
        style.map(
            "Console.Treeview",
            background=[("selected", self.colors["panel_line"])],
            foreground=[("selected", self.colors["text"])],
        )
        style.configure(
            "Primary.TButton",
            background=self.colors["accent"],
            foreground=self.colors["background"],
            bordercolor=self.colors["accent_soft"],
            focuscolor=self.colors["accent"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
            padding=(28, 28),
            font=self.fonts["nav"],
        )
        style.map(
            "Primary.TButton",
            background=[("disabled", self.colors["disabled_button"]), ("active", "#58e2d4")],
            foreground=[("disabled", self.colors["text"])],
            bordercolor=[("disabled", self.colors["outline"])],
            lightcolor=[("disabled", self.colors["disabled_button"])],
            darkcolor=[("disabled", self.colors["disabled_button"])],
        )
        style.configure(
            "Danger.TButton",
            background=self.colors["danger"],
            foreground=self.colors["text"],
            bordercolor=self.colors["danger_soft"],
            focuscolor=self.colors["danger"],
            lightcolor=self.colors["danger"],
            darkcolor=self.colors["danger"],
            padding=(28, 28),
            font=self.fonts["nav"],
        )
        style.map(
            "Danger.TButton",
            background=[("disabled", self.colors["disabled_button"]), ("active", "#b51523")],
            foreground=[("disabled", self.colors["text"])],
            bordercolor=[("disabled", self.colors["outline"])],
            lightcolor=[("disabled", self.colors["disabled_button"])],
            darkcolor=[("disabled", self.colors["disabled_button"])],
        )
        style.configure(
            "Ghost.TButton",
            background=self.colors["panel_high"],
            foreground=self.colors["text"],
            bordercolor=self.colors["outline"],
            focuscolor=self.colors["panel_high"],
            lightcolor=self.colors["panel_high"],
            darkcolor=self.colors["panel_high"],
            padding=(14, 10),
            font=self.fonts["section"],
        )
        style.map(
            "Ghost.TButton",
            background=[("disabled", self.colors["disabled_button"]), ("active", self.colors["panel_line"])],
            foreground=[("disabled", self.colors["text"])],
            bordercolor=[("disabled", self.colors["outline"])],
            lightcolor=[("disabled", self.colors["disabled_button"])],
            darkcolor=[("disabled", self.colors["disabled_button"])],
        )
        style.configure(
            "Slim.TButton",
            background=self.colors["panel_high"],
            foreground=self.colors["text"],
            bordercolor=self.colors["outline"],
            focuscolor=self.colors["panel_high"],
            lightcolor=self.colors["panel_high"],
            darkcolor=self.colors["panel_high"],
            padding=(10, 8),
            font=self.fonts["section"],
        )
        style.map(
            "Slim.TButton",
            background=[("disabled", self.colors["disabled_button"]), ("active", self.colors["panel_line"])],
            foreground=[("disabled", self.colors["text"])],
            bordercolor=[("disabled", self.colors["outline"])],
            lightcolor=[("disabled", self.colors["disabled_button"])],
            darkcolor=[("disabled", self.colors["disabled_button"])],
        )
        style.layout(
            "Primary.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout(
            "Danger.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout(
            "ActionPrimary.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout(
            "ActionDanger.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout(
            "Ghost.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout(
            "Slim.TButton",
            [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "nswe"})],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.configure(
            "Console.TCheckbutton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=self.fonts["body"],
            indicatorcolor=self.colors["field"],
            indicatordiameter=14,
            bordercolor=self.colors["outline"],
            focuscolor=self.colors["panel"],
        )
        style.map(
            "Console.TCheckbutton",
            background=[("active", self.colors["panel"])],
            foreground=[("active", self.colors["text"])],
            indicatorbackground=[("active", self.colors["field"])],
        )

    def _load_language_image(self, language_code: str) -> tk.PhotoImage | None:
        image_path = LANGUAGE_ASSETS.get(language_code)
        if image_path is None or not image_path.exists():
            return None

        try:
            image = tk.PhotoImage(file=image_path)
        except tk.TclError:
            return None

        max_width = 26
        max_height = 18
        shrink_x = max(1, (image.width() + max_width - 1) // max_width)
        shrink_y = max(1, (image.height() + max_height - 1) // max_height)
        shrink = max(shrink_x, shrink_y)
        if shrink > 1:
            image = image.subsample(shrink, shrink)

        self.language_images[language_code] = image
        return image

    def _build_language_switcher(self, parent: tk.Misc) -> None:
        for language_code in ("en", "pt-BR"):
            image = self._load_language_image(language_code)
            is_selected = self.current_language == language_code
            button = tk.Button(
                parent,
                image=image,
                text="" if image is not None else ("EN" if language_code == "en" else "PT"),
                command=lambda code=language_code: self._set_language(code),
                bg=self.colors["accent_soft"] if is_selected else self.colors["panel_high"],
                fg=self.colors["text"],
                activebackground=self.colors["panel_line"],
                activeforeground=self.colors["text"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                highlightbackground=self.colors["background"],
                highlightcolor=self.colors["background"],
                takefocus=0,
                padx=8,
                pady=6,
                cursor="hand2",
            )
            button.pack(side="right", padx=(8, 0))

    def _rebuild_ui(self) -> None:
        running = self.worker_thread is not None and self.worker_thread.is_alive()
        self.root.title(tr("app.title"))
        for child in list(self.root.winfo_children()):
            child.destroy()
        self.language_images.clear()
        self._build_styles()
        self._build_layout()
        self._refresh_sequence_table()
        self._refresh_dashboard_summary()
        self._set_running(running)
        self.root.after_idle(lambda: self._apply_responsive_layout(force=True))

    def _set_language(self, language_code: str) -> None:
        if language_code == self.current_language:
            return

        load_app_strings(language_code)
        self.current_language = CURRENT_LANGUAGE
        self.status_var.set(
            tr(
                "status.language_changed",
                language_name=tr("labels.language_english") if language_code == "en" else tr("labels.language_portuguese"),
            )
        )
        self._rebuild_ui()
        self._save_config()

    def _create_panel(
        self,
        parent: tk.Misc,
        row: int,
        column: int,
        *,
        rowspan: int = 1,
        title: str,
        subtitle: str | None = None,
        sticky: str = "nsew",
    ) -> tuple[tk.Frame, tk.Frame, tk.Label | None]:
        outer = tk.Frame(parent, bg=self.colors["outline"], bd=0, highlightthickness=0)
        outer.grid(row=row, column=column, rowspan=rowspan, sticky=sticky, padx=6, pady=6)

        panel = tk.Frame(outer, bg=self.colors["panel"], padx=20, pady=18)
        panel.pack(fill="both", expand=True, padx=1, pady=1)

        header = tk.Frame(panel, bg=self.colors["panel"])
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text=title,
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=self.fonts["section"],
        ).pack(anchor="w")

        subtitle_label = None
        if subtitle:
            subtitle_label = tk.Label(
                header,
                text=subtitle,
                bg=self.colors["panel"],
                fg=self.colors["subtle"],
                font=self.fonts["body"],
                justify="left",
            )
            subtitle_label.pack(anchor="w", pady=(4, 0))

        return outer, panel, subtitle_label

    def _create_metric_card(self, parent: tk.Misc, title: str, variable: tk.StringVar, column: int) -> tk.Frame:
        outer = tk.Frame(parent, bg=self.colors["outline"])
        outer.grid(row=0, column=column, sticky="ew", padx=(0, 12 if column == 0 else 0))

        body = tk.Frame(outer, bg=self.colors["panel_high"], padx=18, pady=12)
        body.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(
            body,
            text=title,
            bg=self.colors["panel_high"],
            fg=self.colors["subtle"],
            font=self.fonts["section"],
        ).pack(anchor="w")
        tk.Label(
            body,
            textvariable=variable,
            bg=self.colors["panel_high"],
            fg=self.colors["accent"],
            font=self.fonts["metric"],
        ).pack(anchor="w", pady=(6, 0))
        return outer

    def _build_layout(self) -> None:
        self.shell = tk.Frame(self.root, bg=self.colors["background"], padx=18, pady=16)
        self.shell.pack(fill="both", expand=True)
        self.shell.grid_columnconfigure(0, weight=3)
        self.shell.grid_columnconfigure(1, weight=2)
        self.shell.grid_rowconfigure(2, weight=1)

        self.nav = tk.Frame(self.shell, bg=self.colors["background"])
        self.nav.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.nav.grid_columnconfigure(1, weight=1)
        self.nav.grid_columnconfigure(2, weight=0)
        self.nav.grid_columnconfigure(3, weight=0)

        self.brand = tk.Frame(self.nav, bg=self.colors["background"])
        self.brand.grid(row=0, column=0, sticky="w")
        tk.Label(
            self.brand,
            text=tr("labels.brand"),
            bg=self.colors["background"],
            fg=self.colors["accent"],
            font=self.fonts["brand"],
        ).pack(side="left")
        tk.Label(
            self.brand,
            text=tr("app.version"),
            bg=self.colors["background"],
            fg=self.colors["subtle"],
            font=self.fonts["nav"],
            padx=10,
        ).pack(side="left")

        self.nav_actions = tk.Frame(self.nav, bg=self.colors["background"])
        self.nav_actions.grid(row=0, column=2, sticky="e", padx=(0, 12))
        ttk.Button(self.nav_actions, text=tr("labels.button_import"), command=self._import_profile, style="Slim.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(self.nav_actions, text=tr("labels.button_export"), command=self._export_profile, style="Slim.TButton").pack(side="left")

        self.language_switcher = tk.Frame(self.nav, bg=self.colors["background"])
        self.language_switcher.grid(row=0, column=3, sticky="e", padx=(0, 6))
        self._build_language_switcher(self.language_switcher)

        self.summary_outer = tk.Frame(self.shell, bg=self.colors["outline"])
        self.summary_outer.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12), padx=6)
        self.summary = tk.Frame(self.summary_outer, bg=self.colors["panel_high"], padx=20, pady=18)
        self.summary.pack(fill="both", expand=True, padx=1, pady=1)
        self.summary.grid_columnconfigure(0, weight=1)
        self.summary.grid_columnconfigure(1, weight=0)

        self.summary_left = tk.Frame(self.summary, bg=self.colors["panel_high"])
        self.summary_left.grid(row=0, column=0, sticky="w")

        profile_icon = tk.Canvas(self.summary_left, width=52, height=52, bg=self.colors["panel_high"], highlightthickness=0)
        profile_icon.create_oval(4, 4, 48, 48, fill=self.colors["panel"], outline=self.colors["accent_soft"], width=2)
        profile_icon.create_polygon(20, 16, 20, 36, 36, 26, fill=self.colors["accent"], outline="")
        profile_icon.pack(side="left", padx=(0, 16))

        self.profile_text = tk.Frame(self.summary_left, bg=self.colors["panel_high"])
        self.profile_text.pack(side="left", fill="x", expand=True)
        self.title_row = tk.Frame(self.profile_text, bg=self.colors["panel_high"])
        self.title_row.pack(anchor="w")
        self.profile_name_label = tk.Label(
            self.title_row,
            textvariable=self.profile_name_var,
            bg=self.colors["panel_high"],
            fg=self.colors["text"],
            font=("Space Grotesk", 20, "bold"),
            cursor="hand2",
        )
        self.profile_name_label.pack(side="left")
        self.profile_name_label.bind("<Button-1>", self._begin_profile_name_edit)

        self.profile_name_entry_var.set(self.profile_name_var.get())
        self.profile_name_entry = ttk.Entry(self.title_row, textvariable=self.profile_name_entry_var, style="Console.TEntry")
        self.profile_name_entry.bind("<Return>", self._commit_profile_name_edit)
        self.profile_name_entry.bind("<Escape>", self._cancel_profile_name_edit)
        self.profile_name_entry.bind("<FocusOut>", self._commit_profile_name_edit)
        self.profile_badge = tk.Label(
            self.title_row,
            textvariable=self.profile_state_var,
            bg=self.colors["accent_soft"],
            fg=self.colors["background"],
            font=self.fonts["section"],
            padx=10,
            pady=4,
        )
        self.profile_badge.pack(side="left", padx=(10, 0))
        self.profile_meta_label = tk.Label(
            self.profile_text,
            textvariable=self.profile_meta_var,
            bg=self.colors["panel_high"],
            fg=self.colors["muted"],
            font=self.fonts["body"],
            justify="left",
        )
        self.profile_meta_label.pack(anchor="w", pady=(6, 0), fill="x")

        self.metrics = tk.Frame(self.summary, bg=self.colors["panel_high"])
        self.metrics.grid(row=0, column=1, sticky="e")
        self.metrics.grid_columnconfigure(0, weight=1)
        self.metrics.grid_columnconfigure(1, weight=1)
        self.metric_cards = [
            self._create_metric_card(self.metrics, tr("labels.metric_actions"), self.actions_count_var, 0),
            self._create_metric_card(self.metrics, tr("labels.metric_cycle"), self.cycle_time_var, 1),
        ]

        self.sequence_panel_outer, sequence_panel, self.sequence_subtitle_label = self._create_panel(
            self.shell,
            row=2,
            column=0,
            rowspan=3,
            title=tr("labels.panel_sequence_title"),
            subtitle=tr("labels.panel_sequence_subtitle"),
        )
        sequence_panel.grid_rowconfigure(2, weight=1)
        sequence_panel.grid_columnconfigure(0, weight=1)

        sequence_header = tk.Frame(sequence_panel, bg=self.colors["panel"])
        sequence_header.pack(fill="x", pady=(0, 10))
        tk.Label(
            sequence_header,
            text=tr("labels.nav_title"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=self.fonts["headline"],
        ).pack(side="left")
        self.header_actions = tk.Frame(sequence_header, bg=self.colors["panel"])
        self.header_actions.pack(side="right")
        ttk.Button(self.header_actions, text=tr("labels.button_remove"), command=self._remove_selected_step, style="Ghost.TButton").pack(side="right")
        ttk.Button(self.header_actions, text=tr("labels.button_add_action"), command=self._add_step, style="Ghost.TButton").pack(side="right", padx=(0, 8))

        self.editor_block = tk.Frame(sequence_panel, bg=self.colors["panel"])
        self.editor_block.pack(fill="x", pady=(0, 12))
        self.editor_block.grid_columnconfigure(0, weight=2)
        self.editor_block.grid_columnconfigure(1, weight=1)

        self.step_combo_label = tk.Label(self.editor_block, text=tr("labels.header_key_hotkey"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.step_combo_label.grid(row=0, column=0, sticky="w")
        self.step_delay_label = tk.Label(self.editor_block, text=tr("labels.header_delay"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.step_delay_label.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.step_combo_field = tk.Frame(self.editor_block, bg=self.colors["outline"])
        self.step_combo_field.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        step_combo_inner = tk.Frame(self.step_combo_field, bg=self.colors["field"])
        step_combo_inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.step_combo_box = ttk.Combobox(
            step_combo_inner,
            textvariable=self.step_combo_var,
            values=KEY_COMBO_OPTIONS,
            style="Console.TCombobox",
        )
        self.step_combo_box.pack(fill="x", expand=True)

        self.step_delay_field = tk.Frame(self.editor_block, bg=self.colors["outline"])
        self.step_delay_field.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        delay_inner = tk.Frame(self.step_delay_field, bg=self.colors["field"])
        delay_inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.step_delay_entry = ttk.Entry(delay_inner, textvariable=self.step_delay_var, style="Console.TEntry")
        self.step_delay_entry.pack(side="left", fill="x", expand=True)
        tk.Label(delay_inner, text=tr("labels.unit_ms"), bg=self.colors["field"], fg=self.colors["subtle"], font=self.fonts["mono"], padx=10).pack(side="right")

        sequence_table_field = tk.Frame(sequence_panel, bg=self.colors["outline"])
        sequence_table_field.pack(fill="both", expand=True)
        sequence_table_inner = tk.Frame(sequence_table_field, bg=self.colors["panel"])
        sequence_table_inner.pack(fill="both", expand=True, padx=1, pady=1)

        self.sequence_table = ttk.Treeview(
            sequence_table_inner,
            columns=("order", "combo", "delay"),
            show="headings",
            height=11,
            style="Console.Treeview",
        )
        self.sequence_table.heading("order", text=tr("labels.table_id"))
        self.sequence_table.heading("combo", text=tr("labels.table_action"))
        self.sequence_table.heading("delay", text=tr("labels.table_wait"))
        self.sequence_table.column("order", width=70, anchor="center")
        self.sequence_table.column("combo", width=250, anchor="w")
        self.sequence_table.column("delay", width=130, anchor="center")
        self.sequence_table.pack(fill="both", expand=True)
        self.sequence_table.bind("<<TreeviewSelect>>", self._populate_editor_from_selection)

        self.action_bar = tk.Frame(sequence_panel, bg=self.colors["panel"])
        self.action_bar.pack(fill="x", pady=(12, 0))
        for index in range(6):
            self.action_bar.grid_columnconfigure(index, weight=1)

        self.action_buttons = [
            ttk.Button(self.action_bar, text=tr("labels.button_add"), command=self._add_step, style="Ghost.TButton"),
            ttk.Button(self.action_bar, text=tr("labels.button_update"), command=self._update_selected_step, style="Ghost.TButton"),
            ttk.Button(self.action_bar, text=tr("labels.button_remove"), command=self._remove_selected_step, style="Ghost.TButton"),
            ttk.Button(self.action_bar, text=tr("labels.button_up"), command=lambda: self._move_selected_step(-1), style="Slim.TButton"),
            ttk.Button(self.action_bar, text=tr("labels.button_down"), command=lambda: self._move_selected_step(1), style="Slim.TButton"),
            ttk.Button(self.action_bar, text=tr("labels.button_clear"), command=self._clear_sequence, style="Ghost.TButton"),
        ]

        self.execution_panel_outer, execution_panel, self.execution_subtitle_label = self._create_panel(
            self.shell,
            row=2,
            column=1,
            title=tr("labels.panel_execution_title"),
            subtitle=tr("labels.panel_execution_subtitle"),
        )

        self.controls_row = tk.Frame(execution_panel, bg=self.colors["panel"])
        self.controls_row.pack(fill="x", pady=(0, 14))
        self.controls_row.grid_columnconfigure(0, weight=1)
        self.controls_row.grid_columnconfigure(1, weight=1)

        self.start_button = ttk.Button(self.controls_row, text=tr("labels.button_start"), command=self.start, style="Primary.TButton")
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.stop_button = ttk.Button(self.controls_row, text=tr("labels.button_stop"), command=self.stop, style="Danger.TButton")
        self.stop_button.grid(row=0, column=1, sticky="ew")
        self.stop_button.state(["disabled"])

        status_strip = tk.Frame(execution_panel, bg=self.colors["field"], padx=14, pady=12)
        status_strip.pack(fill="x")
        self.status_led = tk.Canvas(status_strip, width=18, height=18, bg=self.colors["field"], highlightthickness=0)
        self.status_led.pack(side="left")
        self.status_led_dot = self.status_led.create_oval(4, 4, 14, 14, fill=self.colors["subtle"], outline="")
        tk.Label(status_strip, textvariable=self.status_var, bg=self.colors["field"], fg=self.colors["text"], font=self.fonts["body"]).pack(side="left", padx=(8, 0))
        tk.Label(status_strip, textvariable=self.engine_mode_var, bg=self.colors["field"], fg=self.colors["subtle"], font=self.fonts["section"]).pack(side="right")

        self.config_panel_outer, config_panel, self.config_subtitle_label = self._create_panel(
            self.shell,
            row=3,
            column=1,
            title=tr("labels.panel_config_title"),
            subtitle=tr("labels.panel_config_subtitle"),
        )

        self.fields = tk.Frame(config_panel, bg=self.colors["panel"])
        self.fields.pack(fill="x")
        self.fields.grid_columnconfigure(0, weight=1)
        self.fields.grid_columnconfigure(1, weight=1)

        self.interval_label = tk.Label(self.fields, text=tr("labels.label_global_interval"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.interval_label.grid(row=0, column=0, sticky="w")
        self.start_delay_label = tk.Label(self.fields, text=tr("labels.label_initial_delay"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.start_delay_label.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.interval_field = tk.Frame(self.fields, bg=self.colors["outline"])
        self.interval_field.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        interval_inner = tk.Frame(self.interval_field, bg=self.colors["field"])
        interval_inner.pack(fill="both", expand=True, padx=1, pady=1)
        ttk.Entry(interval_inner, textvariable=self.interval_var, style="Console.TEntry").pack(side="left", fill="x", expand=True)
        tk.Label(interval_inner, text=tr("labels.unit_ms"), bg=self.colors["field"], fg=self.colors["subtle"], font=self.fonts["mono"], padx=10).pack(side="right")

        self.start_delay_field = tk.Frame(self.fields, bg=self.colors["outline"])
        self.start_delay_field.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(8, 12))
        delay_inner = tk.Frame(self.start_delay_field, bg=self.colors["field"])
        delay_inner.pack(fill="both", expand=True, padx=1, pady=1)
        ttk.Entry(delay_inner, textvariable=self.start_delay_var, style="Console.TEntry").pack(side="left", fill="x", expand=True)
        tk.Label(delay_inner, text=tr("labels.unit_sec"), bg=self.colors["field"], fg=self.colors["subtle"], font=self.fonts["mono"], padx=10).pack(side="right")

        self.sequence_pause_label = tk.Label(self.fields, text=tr("labels.label_sequence_loop_pause"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.sequence_pause_label.grid(row=2, column=0, sticky="w")
        self.single_fallback_label = tk.Label(self.fields, text=tr("labels.label_single_key_fallback"), bg=self.colors["panel"], fg=self.colors["muted"], font=self.fonts["section"])
        self.single_fallback_label.grid(row=2, column=1, sticky="w", padx=(12, 0))

        self.sequence_pause_field = tk.Frame(self.fields, bg=self.colors["outline"])
        self.sequence_pause_field.grid(row=3, column=0, sticky="ew", pady=(8, 12))
        sequence_pause_inner = tk.Frame(self.sequence_pause_field, bg=self.colors["field"])
        sequence_pause_inner.pack(fill="both", expand=True, padx=1, pady=1)
        ttk.Entry(sequence_pause_inner, textvariable=self.sequence_pause_var, style="Console.TEntry").pack(side="left", fill="x", expand=True)
        tk.Label(sequence_pause_inner, text=tr("labels.unit_ms"), bg=self.colors["field"], fg=self.colors["subtle"], font=self.fonts["mono"], padx=10).pack(side="right")

        self.single_field = tk.Frame(self.fields, bg=self.colors["outline"])
        self.single_field.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(8, 12))
        single_combo_inner = tk.Frame(self.single_field, bg=self.colors["field"])
        single_combo_inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.single_combo_box = ttk.Combobox(
            single_combo_inner,
            textvariable=self.single_combo_var,
            values=KEY_COMBO_OPTIONS,
            style="Console.TCombobox",
        )
        self.single_combo_box.pack(fill="x", expand=True)

        ttk.Checkbutton(
            config_panel,
            text=tr("labels.checkbox_scancode"),
            variable=self.use_scancodes_var,
            style="Console.TCheckbutton",
        ).pack(anchor="w", pady=(8, 6))

        tk.Label(
            config_panel,
            textvariable=self.mode_hint_var,
            bg=self.colors["panel"],
            fg=self.colors["accent"],
            font=self.fonts["section"],
        ).pack(anchor="w")

        self._update_status_indicator(False)
        self._apply_action_bar_layout(False)

    def _handle_root_configure(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(50, self._apply_responsive_layout)

    def _apply_responsive_layout(self, force: bool = False) -> None:
        if not hasattr(self, "shell"):
            return

        self._resize_after_id = None
        width = max(self.root.winfo_width(), self.root.winfo_reqwidth())
        stacked = width < 1120
        compact_metrics = width < 980
        mode = "stacked" if stacked else "wide"

        if force or mode != self._responsive_mode:
            if stacked:
                self.shell.grid_columnconfigure(0, weight=1)
                self.shell.grid_columnconfigure(1, weight=0)
                self.nav.grid_columnconfigure(0, weight=1)
                self.nav.grid_columnconfigure(1, weight=0)
                self.nav.grid_columnconfigure(2, weight=0)
                self.nav.grid_columnconfigure(3, weight=0)
                self.brand.grid_configure(row=0, column=0, columnspan=4, sticky="w")
                self.nav_actions.grid_configure(row=1, column=0, sticky="w", padx=(0, 0), pady=(10, 0))
                self.language_switcher.grid_configure(row=1, column=3, sticky="e", padx=(0, 6), pady=(10, 0))

                self.summary_outer.grid_configure(row=1, column=0, columnspan=2)
                self.summary_left.grid_configure(row=0, column=0, sticky="ew")
                self.metrics.grid_configure(row=1, column=0, sticky="ew", pady=(16, 0))

                self.sequence_panel_outer.grid_configure(row=2, column=0, columnspan=2, rowspan=1, sticky="nsew")
                self.execution_panel_outer.grid_configure(row=3, column=0, columnspan=2, sticky="nsew")
                self.config_panel_outer.grid_configure(row=4, column=0, columnspan=2, sticky="nsew")

                self.controls_row.grid_columnconfigure(0, weight=1)
                self.controls_row.grid_columnconfigure(1, weight=1)
                self.start_button.grid_configure(row=0, column=0, columnspan=2, padx=(0, 0), pady=(0, 10))
                self.stop_button.grid_configure(row=1, column=0, columnspan=2, padx=(0, 0))

                self.step_combo_label.grid_configure(row=0, column=0, columnspan=2, padx=(0, 0))
                self.step_combo_field.grid_configure(row=1, column=0, columnspan=2, padx=(0, 0))
                self.step_delay_label.grid_configure(row=2, column=0, columnspan=2, padx=(0, 0), pady=(12, 0))
                self.step_delay_field.grid_configure(row=3, column=0, columnspan=2, padx=(0, 0))

                self.interval_label.grid_configure(row=0, column=0, columnspan=2, padx=(0, 0))
                self.interval_field.grid_configure(row=1, column=0, columnspan=2, padx=(0, 0))
                self.start_delay_label.grid_configure(row=2, column=0, columnspan=2, padx=(0, 0))
                self.start_delay_field.grid_configure(row=3, column=0, columnspan=2, padx=(0, 0))
                self.sequence_pause_label.grid_configure(row=4, column=0, columnspan=2, padx=(0, 0))
                self.sequence_pause_field.grid_configure(row=5, column=0, columnspan=2, padx=(0, 0))
                self.single_fallback_label.grid_configure(row=6, column=0, columnspan=2, padx=(0, 0))
                self.single_field.grid_configure(row=7, column=0, columnspan=2, padx=(0, 0))
            else:
                self.shell.grid_columnconfigure(0, weight=3)
                self.shell.grid_columnconfigure(1, weight=2)
                self.nav.grid_columnconfigure(0, weight=0)
                self.nav.grid_columnconfigure(1, weight=1)
                self.nav.grid_columnconfigure(2, weight=0)
                self.nav.grid_columnconfigure(3, weight=0)
                self.brand.grid_configure(row=0, column=0, columnspan=1, sticky="w")
                self.nav_actions.grid_configure(row=0, column=2, sticky="e", padx=(0, 12), pady=(0, 0))
                self.language_switcher.grid_configure(row=0, column=3, sticky="e", padx=(0, 6), pady=(0, 0))

                self.summary_outer.grid_configure(row=1, column=0, columnspan=2)
                self.summary_left.grid_configure(row=0, column=0, sticky="w")
                self.metrics.grid_configure(row=0, column=1, sticky="e", pady=(0, 0))

                self.sequence_panel_outer.grid_configure(row=2, column=0, columnspan=1, rowspan=3, sticky="nsew")
                self.execution_panel_outer.grid_configure(row=2, column=1, columnspan=1, sticky="nsew")
                self.config_panel_outer.grid_configure(row=3, column=1, columnspan=1, sticky="nsew")

                self.start_button.grid_configure(row=0, column=0, columnspan=1, padx=(0, 10), pady=(0, 0))
                self.stop_button.grid_configure(row=0, column=1, columnspan=1, padx=(0, 0), pady=(0, 0))

                self.step_combo_label.grid_configure(row=0, column=0, columnspan=1, padx=(0, 0), pady=(0, 0))
                self.step_combo_field.grid_configure(row=1, column=0, columnspan=1, padx=(0, 0))
                self.step_delay_label.grid_configure(row=0, column=1, columnspan=1, padx=(12, 0), pady=(0, 0))
                self.step_delay_field.grid_configure(row=1, column=1, columnspan=1, padx=(12, 0))

                self.interval_label.grid_configure(row=0, column=0, columnspan=1, padx=(0, 0))
                self.interval_field.grid_configure(row=1, column=0, columnspan=1, padx=(0, 0))
                self.start_delay_label.grid_configure(row=0, column=1, columnspan=1, padx=(12, 0))
                self.start_delay_field.grid_configure(row=1, column=1, columnspan=1, padx=(12, 0))
                self.sequence_pause_label.grid_configure(row=2, column=0, columnspan=1, padx=(0, 0))
                self.sequence_pause_field.grid_configure(row=3, column=0, columnspan=1, padx=(0, 0))
                self.single_fallback_label.grid_configure(row=2, column=1, columnspan=1, padx=(12, 0))
                self.single_field.grid_configure(row=3, column=1, columnspan=1, padx=(12, 0))

            self._responsive_mode = mode

        self._apply_metric_layout(compact_metrics)
        self._apply_action_bar_layout(stacked)
        self._update_responsive_copy(width, stacked)
        self._update_treeview_columns(width, stacked)

    def _apply_metric_layout(self, compact: bool) -> None:
        layout = ((0, 0), (1, 0)) if compact else ((0, 0), (0, 1))
        for column in range(2):
            self.metrics.grid_columnconfigure(column, weight=1 if not compact or column == 0 else 0)
        for index, card in enumerate(self.metric_cards):
            row, column = layout[index]
            card.grid_configure(row=row, column=column, sticky="ew", padx=(0, 0), pady=(0, 12 if compact and index == 0 else 0))

    def _apply_action_bar_layout(self, stacked: bool) -> None:
        for index in range(6):
            self.action_bar.grid_columnconfigure(index, weight=0)
            self.action_bar.grid_rowconfigure(index, weight=0)

        if stacked:
            positions = ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2))
            for column in range(3):
                self.action_bar.grid_columnconfigure(column, weight=1)
            for button, (row, column) in zip(self.action_buttons, positions):
                button.grid(row=row, column=column, sticky="ew", padx=4, pady=4)
        else:
            for column in range(6):
                self.action_bar.grid_columnconfigure(column, weight=1)
            for index, button in enumerate(self.action_buttons):
                left = 0 if index == 0 else 6
                right = 0 if index == len(self.action_buttons) - 1 else 6
                button.grid(row=0, column=index, sticky="ew", padx=(left, right), pady=(0, 0))

    def _update_responsive_copy(self, width: int, stacked: bool) -> None:
        profile_wrap = max(320, width - 220) if stacked else max(360, int(width * 0.32))
        subtitle_wrap = max(280, width - 140) if stacked else max(320, int(width * 0.28))
        self.profile_meta_label.configure(wraplength=profile_wrap)
        for label in (self.sequence_subtitle_label, self.execution_subtitle_label, self.config_subtitle_label):
            if label is not None:
                label.configure(wraplength=subtitle_wrap)

    def _update_treeview_columns(self, width: int, stacked: bool) -> None:
        available = self.sequence_table.winfo_width()
        if available <= 1:
            available = width - (140 if stacked else 720)
        available = max(available, 320)
        order_width = 72
        delay_width = 110 if stacked else 130
        combo_width = max(160 if stacked else 220, available - order_width - delay_width)
        self.sequence_table.column("order", width=order_width, minwidth=64, anchor="center", stretch=False)
        self.sequence_table.column("delay", width=delay_width, minwidth=96, anchor="center", stretch=False)
        self.sequence_table.column("combo", width=combo_width, minwidth=160, anchor="w", stretch=True)

    def _save_profile(self) -> None:
        self._save_config()
        self.status_var.set(tr("status.profile_saved"))

    def _begin_profile_name_edit(self, _event: object | None = None) -> None:
        self._profile_name_before_edit = self.profile_name_var.get()
        self.profile_name_entry_var.set(self.profile_name_var.get())
        self.profile_name_label.pack_forget()
        self.profile_name_entry.pack(side="left", before=self.profile_badge)
        self.profile_name_entry.focus_set()
        self.profile_name_entry.selection_range(0, "end")

    def _commit_profile_name_edit(self, _event: object | None = None) -> None:
        new_name = self.profile_name_entry_var.get().strip() or tr("labels.profile_name")
        self.profile_name_var.set(new_name)
        self.profile_name_entry_var.set(new_name)
        if self.profile_name_entry.winfo_manager():
            self.profile_name_entry.pack_forget()
            self.profile_name_label.pack(side="left", before=self.profile_badge)
        self._save_config()

    def _cancel_profile_name_edit(self, _event: object | None = None) -> None:
        self.profile_name_entry_var.set(self._profile_name_before_edit)
        if self.profile_name_entry.winfo_manager():
            self.profile_name_entry.pack_forget()
            self.profile_name_label.pack(side="left", before=self.profile_badge)

    def _profile_payload(self) -> dict[str, object]:
        return {
            "language": self.current_language,
            "profile_name": self.profile_name_var.get().strip(),
            "single_combo": self.single_combo_var.get().strip(),
            "interval_ms": self.interval_var.get().strip(),
            "start_delay": self.start_delay_var.get().strip(),
            "sequence_pause": self.sequence_pause_var.get().strip(),
            "use_scancodes": self.use_scancodes_var.get(),
            "sequence_steps": [asdict(step) for step in self.sequence_steps],
        }

    def _apply_profile_payload(self, payload: dict[str, object], rebuild_language: bool = True) -> None:
        configured_language = str(payload.get("language", self.current_language)).strip()
        if rebuild_language and configured_language and configured_language != self.current_language:
            load_app_strings(configured_language)
            self.current_language = CURRENT_LANGUAGE
            self._rebuild_ui()

        self.profile_name_var.set(str(payload.get("profile_name", self.profile_name_var.get())).strip() or tr("labels.profile_name"))
        self.profile_name_entry_var.set(self.profile_name_var.get())
        self.single_combo_var.set(str(payload.get("single_combo", self.single_combo_var.get())))
        self.interval_var.set(str(payload.get("interval_ms", self.interval_var.get())))
        self.start_delay_var.set(str(payload.get("start_delay", self.start_delay_var.get())))
        self.sequence_pause_var.set(str(payload.get("sequence_pause", self.sequence_pause_var.get())))

        raw_use_scancodes = payload.get("use_scancodes", self.use_scancodes_var.get())
        if isinstance(raw_use_scancodes, str):
            self.use_scancodes_var.set(raw_use_scancodes.strip().lower() in {"1", "true", "yes", "on"})
        else:
            self.use_scancodes_var.set(bool(raw_use_scancodes))

        loaded_steps = []
        for raw_step in payload.get("sequence_steps", []):
            if not isinstance(raw_step, dict):
                continue
            combo = str(raw_step.get("combo", "")).strip()
            delay = raw_step.get("delay_ms", 0)
            try:
                delay_ms = int(delay)
            except (TypeError, ValueError):
                continue
            if combo:
                loaded_steps.append(SequenceStep(combo=combo, delay_ms=max(0, delay_ms)))
        self.sequence_steps = loaded_steps
        self._refresh_sequence_table()

    def _import_profile(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title=tr("dialogs.import_title"),
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            self.status_var.set(tr("status.profile_import_cancelled"))
            return

        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            messagebox.showerror(tr("dialogs.invalid_config_title"), tr("validation.profile_invalid"), parent=self.root)
            return

        if not isinstance(payload, dict):
            messagebox.showerror(tr("dialogs.invalid_config_title"), tr("validation.profile_invalid"), parent=self.root)
            return

        self._apply_profile_payload(payload, rebuild_language=True)
        self._save_config()
        self.status_var.set(tr("status.profile_imported"))

    def _export_profile(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=tr("dialogs.export_title"),
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            self.status_var.set(tr("status.profile_export_cancelled"))
            return

        try:
            Path(path).write_text(json.dumps(self._profile_payload(), indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror(
                tr("dialogs.invalid_config_title"),
                tr("validation.profile_export_failed", error=exc),
                parent=self.root,
            )
            return

        self.status_var.set(tr("status.profile_exported"))

    def _move_selected_step(self, offset: int) -> None:
        index = self._selected_index()
        if index is None:
            messagebox.showinfo(tr("dialogs.move_title"), tr("dialogs.move_select"), parent=self.root)
            return

        target_index = index + offset
        if target_index < 0 or target_index >= len(self.sequence_steps):
            return

        self.sequence_steps[index], self.sequence_steps[target_index] = (
            self.sequence_steps[target_index],
            self.sequence_steps[index],
        )
        self._refresh_sequence_table()
        self._save_config()
        self._select_sequence_row(target_index)

    def _select_sequence_row(self, index: int) -> None:
        children = self.sequence_table.get_children()
        if index < 0 or index >= len(children):
            return
        item_id = children[index]
        self.sequence_table.selection_set(item_id)
        self.sequence_table.focus(item_id)
        self.sequence_table.see(item_id)

    def _refresh_dashboard_summary(self) -> None:
        if self.sequence_steps:
            actions = len(self.sequence_steps)
            cycle_ms = sum(step.delay_ms for step in self.sequence_steps)
            try:
                cycle_ms += parse_non_negative_int(self.sequence_pause_var.get().strip(), tr("validation.label_sequence_pause"))
            except ValueError:
                cycle_ms += 0
            self.mode_hint_var.set(tr("labels.mode_sequence"))
        else:
            actions = 1 if self.single_combo_var.get().strip() else 0
            try:
                cycle_ms = parse_non_negative_int(self.interval_var.get().strip(), tr("validation.label_interval"))
            except ValueError:
                cycle_ms = 0
            self.mode_hint_var.set(tr("labels.mode_single"))

        self.actions_count_var.set(f"{actions:02d}")
        self.cycle_time_var.set(f"{cycle_ms / 1000:.1f}s" if cycle_ms >= 1000 else f"{cycle_ms}ms")
        mode_name = tr("labels.engine_scan_code") if self.use_scancodes_var.get() else tr("labels.engine_virtual_key")
        self.engine_mode_var.set(mode_name)
        combo_display = self.single_combo_var.get().strip() or tr("labels.summary_no_fallback")
        self.profile_meta_var.set(tr("labels.summary_profile_meta", actions=actions, combo_display=combo_display, mode_name=mode_name))

    def _update_status_indicator(self, running: bool) -> None:
        led_color = self.colors["accent"] if running else self.colors["subtle"]
        self.status_led.itemconfigure(self.status_led_dot, fill=led_color)
        self.profile_state_var.set(tr("labels.profile_state_active") if running else tr("labels.profile_state_ready"))
        self.profile_badge.configure(
            bg=self.colors["accent_soft"] if running else self.colors["outline"],
            fg=self.colors["background"] if running else self.colors["text"],
        )

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
        self._update_status_indicator(running)

    def _selected_index(self) -> int | None:
        selection = self.sequence_table.selection()
        if not selection:
            return None
        return self.sequence_table.index(selection[0])

    def _selected_indices(self) -> list[int]:
        selection = self.sequence_table.selection()
        if not selection:
            return []
        return sorted((self.sequence_table.index(item_id) for item_id in selection), reverse=True)

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

        for index, step in enumerate(self.sequence_steps, start=1):
            self.sequence_table.insert("", "end", values=(f"{index:02d}", step.combo, f"{step.delay_ms} ms"))

        self._refresh_dashboard_summary()

    def _validate_step_inputs(self) -> SequenceStep:
        combo = self.step_combo_var.get().strip()
        delay_ms = parse_non_negative_int(self.step_delay_var.get().strip(), tr("validation.label_step_delay"))
        parse_key_combo(combo)
        return SequenceStep(combo=combo, delay_ms=delay_ms)

    def _add_step(self) -> None:
        try:
            step = self._validate_step_inputs()
        except ValueError as exc:
            messagebox.showerror(tr("dialogs.invalid_sequence_title"), str(exc), parent=self.root)
            return

        self.sequence_steps.append(step)
        self._refresh_sequence_table()
        self._save_config()
        self.step_combo_var.set("")
        self.step_delay_var.set("500")
        self.status_var.set(tr("status.step_added"))

    def _update_selected_step(self) -> None:
        index = self._selected_index()
        if index is None:
            messagebox.showinfo(tr("dialogs.update_title"), tr("dialogs.update_select"), parent=self.root)
            return

        try:
            step = self._validate_step_inputs()
        except ValueError as exc:
            messagebox.showerror(tr("dialogs.invalid_sequence_title"), str(exc), parent=self.root)
            return

        self.sequence_steps[index] = step
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set(tr("status.step_updated"))

    def _remove_selected_step(self) -> None:
        indices = self._selected_indices()
        if not indices:
            messagebox.showinfo(tr("dialogs.remove_title"), tr("dialogs.remove_select"), parent=self.root)
            return

        for index in indices:
            del self.sequence_steps[index]
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set(tr("status.step_removed"))

    def _clear_sequence(self) -> None:
        self.sequence_steps.clear()
        self._refresh_sequence_table()
        self._save_config()
        self.status_var.set(tr("status.sequence_cleared"))

    def _validate_run_inputs(self) -> tuple[str, int, int, int, bool, list[SequenceStep]]:
        combo = self.single_combo_var.get().strip()
        interval_ms = parse_non_negative_int(self.interval_var.get().strip(), tr("validation.label_interval"))
        start_delay = parse_non_negative_int(self.start_delay_var.get().strip(), tr("validation.label_start_delay"))
        sequence_pause = parse_non_negative_int(self.sequence_pause_var.get().strip(), tr("validation.label_sequence_pause"))
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
            messagebox.showerror(tr("dialogs.invalid_config_title"), str(exc), parent=self.root)
            return

        self._save_config()
        self.stop_event.clear()
        self._set_running(True)
        mode_label = tr("labels.mode_scan_code_lower") if use_scancodes else tr("labels.mode_virtual_key_lower")
        self.messages.put(("info", tr("status.starting_mode", mode_label=mode_label)))
        self.worker_thread = threading.Thread(
            target=self._run_worker,
            args=(combo, interval_ms, start_delay, sequence_pause, use_scancodes, sequence_steps),
            daemon=True,
        )
        self.worker_thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.messages.put(("info", tr("status.stopping")))

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
                self.messages.put(("info", tr("status.countdown", remaining=remaining)))
                if not sleep_interruptible(1.0, self.stop_event):
                    self.messages.put(("stopped", tr("status.stopped_before_start")))
                    return

            if sequence_steps:
                mode_label = tr("labels.mode_scan_code_lower") if use_scancodes else tr("labels.mode_virtual_key_lower")
                self.messages.put(("info", tr("status.sequence_running", mode_label=mode_label)))
                while not self.stop_event.is_set():
                    for step in sequence_steps:
                        self.sender.send_combo(step.combo, use_scancodes=use_scancodes)
                        if not sleep_interruptible(step.delay_ms / 1000, self.stop_event):
                            self.messages.put(("stopped", tr("status.automation_stopped")))
                            return
                    if sequence_pause > 0 and not sleep_interruptible(sequence_pause / 1000, self.stop_event):
                        self.messages.put(("stopped", tr("status.automation_stopped")))
                        return
            else:
                mode_label = tr("labels.mode_scan_code_lower") if use_scancodes else tr("labels.mode_virtual_key_lower")
                self.messages.put(("info", tr("status.single_running", combo=combo, mode_label=mode_label)))
                while not self.stop_event.is_set():
                    self.sender.send_combo(combo, use_scancodes=use_scancodes)
                    if not sleep_interruptible(interval_ms / 1000, self.stop_event):
                        self.messages.put(("stopped", tr("status.automation_stopped")))
                        return
        except OSError as exc:
            self.messages.put(("stopped", tr("status.send_failure", error=exc)))
        except Exception as exc:
            self.messages.put(("stopped", tr("status.unexpected_error", error=exc)))
        else:
            self.messages.put(("stopped", tr("status.automation_finished")))

    def _save_config(self) -> None:
        payload = self._profile_payload()
        CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load_config(self) -> None:
        if not CONFIG_PATH.exists():
            return

        try:
            payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.status_var.set(tr("status.config_load_failed"))
            return

        self._apply_profile_payload(payload, rebuild_language=True)

    def _handle_close(self) -> None:
        self.stop_event.set()
        self._save_config()
        self.root.destroy()


def main() -> None:
    load_app_strings()
    root = tk.Tk()
    AutoKeyboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
