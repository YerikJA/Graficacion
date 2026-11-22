# Actions/audio.py — Proyecto Combinado
"""
Sistema de audio — Plasma Pea + Optimus Prime
Combina los sonidos de ambos personajes en un solo módulo.
"""
import os
import pygame
from Actions import state

_ACTIONS_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_ACTIONS_DIR)
_SOUNDS_DIR   = os.path.join(_PROJECT_ROOT, "Utils", "sounds")
_ENGLISH_DIR  = os.path.join(_SOUNDS_DIR, "english_words")

# ── Sonidos de palabras en inglés ──────────────────────────────────────
_english_sounds = {}  # "hello" -> pygame.mixer.Sound

# Mapeo nombre-lógico → archivo (de ambos proyectos)
_SOUND_FILES = {
    # Plasma Pea — expresiones
    "enojo"    : "Enojo_1_.mp3",
    "miedo"    : "Miedo_1_.mp3",
    "tristeza" : "Tristeza_1_.mp3",
    "guino"    : "Guino_1_.mp3",
    "alegria"  : "Felicidsd_1_.mp3",
    "sorpresa" : "Asombro_1_.mp3",
    "normal"   : "Felicidsd_1_.mp3",
    # Plasma Pea — movimientos
    "pasos"    : "Caminata_1_.mp3",
    "salto"    : "Salto_1_.mp3",
    "disparo"  : "Disparo_1_.mp3",
    "victoria" : "Victoria_1_.mp3",
    "agachar"  : "Agachao_1_.mp3",
    "saludo"   : "Saludar_1_.mp3",
    "spin"     : "Giro_1_.mp3",
    "cabeza"   : "Girar_cabeza_1_.mp3",
    # Plasma Pea — colisiones
    "hit_zombie" : "Disparo_1_.mp3",
    "hit_caja"   : "Victoria_1_.mp3",
    "hit_valla"  : "Miedo_1_.mp3",
    # Optimus Prime — sonidos propios (fallback al equivalente Plasma si no existe)
    "brazos"     : "brazos.mp3",
    "pasos_opt"  : "pasos.mp3",
    "salto_opt"  : "jump.mp3",
    "agachar_opt": "pasos.mp3",
    "cabeza_opt" : "cabeza.mp3",
    "normal_opt" : "normal.mp3",
    "enojo_opt"  : "enojo.mp3",
    "miedo_opt"  : "Miedo.mp3",
    "tristeza_opt": "Triszteza.mp3",
    "guino_opt"  : "Guino_1_.mp3",
}

_BG_FILES = {
    1: "bg_1.mp3",
    2: "bg_2.mp3",
    3: "bg_3.mp3",
    4: "bg_4.mp3",
    6: "bg_6.mp3",
    7: "bg_pox.mp3",
    8: "bg_fox.mp3",
}

_current_bg = None

def play_rope_music():
    if state.sonido_activado:
        _play_bg(8)
        # Set volume lower to not interfere with words
        try: pygame.mixer.music.set_volume(0.20)
        except Exception: pass

def play_tetris_music():
    if state.sonido_activado:
        _play_bg(7)
        try: pygame.mixer.music.set_volume(0.20)
        except Exception: pass


def init_audio():
    try:
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.mixer.set_num_channels(16)
        pygame.mixer.init()
    except Exception as e:
        print(f"[Audio] Error al inicializar: {e}")
        return

    for name, filename in _SOUND_FILES.items():
        path = os.path.join(_SOUNDS_DIR, filename)
        if os.path.exists(path):
            try:
                state.sounds[name] = pygame.mixer.Sound(path)
                state.sounds[name].set_volume(0.85)
            except Exception as e:
                print(f"[Audio] No se pudo cargar '{filename}': {e}")
                state.sounds[name] = None
        else:
            state.sounds[name] = None

    if os.path.exists(_SOUNDS_DIR):
        for filename in os.listdir(_SOUNDS_DIR):
            if filename.endswith(".mp3") or filename.endswith(".wav"):
                name = os.path.splitext(filename)[0].lower()
                path = os.path.join(_SOUNDS_DIR, filename)
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(0.85)
                    if name not in state.sounds:
                        state.sounds[name] = snd
                    state.sounds[filename] = snd
                except Exception:
                    pass

    # ── Cargar sonidos de palabras en inglés (.m4a) ───────────────────
    if os.path.exists(_ENGLISH_DIR):
        for filename in os.listdir(_ENGLISH_DIR):
            if filename.lower().endswith(('.m4a', '.mp3', '.wav')):
                name_key = os.path.splitext(filename)[0].lower().strip()
                path = os.path.join(_ENGLISH_DIR, filename)
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(1.0)
                    _english_sounds[name_key] = snd
                except Exception as e:
                    print(f"[Audio] No se pudo cargar palabra '{filename}': {e}")
        print(f"[Audio] Palabras en inglés cargadas: {len(_english_sounds)}")

    _play_bg(state.escenario_actual)


def play_english_word(word):
    """Reproduce el sonido de una palabra en inglés en canal dedicado (14).
    No interrumpe otros sonidos del juego."""
    if not state.sonido_activado:
        return
    key = word.lower().strip()
    
    _ALIASES = {
        "excuse me": "excuseme",
        "eat": "eaat",
        "have": "habe",
        "school": "schoole",
        "six": "sic",
        "you're welcome": "your welcome",
    }
    key = _ALIASES.get(key, key)
    
    snd = _english_sounds.get(key)
    if snd is None:
        # Intento de fallback sin espacios (ej. "thank you" -> "thankyou")
        no_space = key.replace(" ", "")
        snd = _english_sounds.get(no_space)
        if snd is None:
            print(f"[Audio] Palabra no encontrada: '{key}' (original: '{word}')")
            return
    try:
        ch = pygame.mixer.Channel(14)
        ch.stop()
        ch.set_volume(1.0)
        ch.play(snd)
    except Exception as e:
        print(f"[Audio] Error reproduciendo '{key}': {e}")


def _play_bg(scenario_num):
    global _current_bg
    filename = _BG_FILES.get(scenario_num)
    if not filename or _current_bg == filename:
        return
    path = os.path.join(_SOUNDS_DIR, filename)
    _current_bg = filename
    if os.path.exists(path):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            # Volumen bajo para Tetris y Cuerda para no tapar los audios de palabras
            vol = 0.15 if scenario_num in (7, 8) else 0.30
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[Audio] Error fondo '{filename}': {e}")
    else:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass


def stop_bg_music():
    """Detiene completamente la música de fondo (rope/tetris/escenario).
    Llamar al volver al menú desde cualquier nivel."""
    global _current_bg
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    _current_bg = None  # Permite que el siguiente _play_bg cargue aunque sea el mismo archivo


def on_scenario_change(scenario_num):
    if state.sonido_activado:
        _play_bg(scenario_num)


def play_sound(name):
    if not state.sonido_activado:
        return
    snd = state.sounds.get(name)
    if snd is None:
        return
    try:
        snd.stop()
        snd.play()
    except Exception:
        pass


def play_walk_sound():
    """Reproduce pasos según el personaje activo."""
    if not state.sonido_activado:
        return
    key = "pasos_opt" if state.personaje_activo == "optimus" else "pasos"
    snd = state.sounds.get(key)
    if snd is None:
        return
    try:
        ch = pygame.mixer.Channel(1)
        if not ch.get_busy():
            ch.set_volume(0.7)
            ch.play(snd)
    except Exception:
        pass


def stop_walk_sound():
    try:
        pygame.mixer.Channel(1).stop()
    except Exception:
        pass


# ── Música exclusiva del Laberinto ────────────────────────────────────
_MAZE_MUSIC_FILE = "zelda_lullaby.mp3"
_maze_music_channel = None   # Canal pygame dedicado
_maze_music_sound   = None   # Objeto Sound cargado
_maze_music_on      = True   # Toggle ON/OFF dentro del laberinto

def _load_maze_music():
    """Carga la música del laberinto si aún no está cargada."""
    global _maze_music_sound
    if _maze_music_sound is not None:
        return
    path = os.path.join(_SOUNDS_DIR, _MAZE_MUSIC_FILE)
    if not os.path.exists(path):
        print(f"[Audio] Música laberinto no encontrada: {path}")
        return
    try:
        _maze_music_sound = pygame.mixer.Sound(path)
        _maze_music_sound.set_volume(0.45)
        print("[Audio] Música laberinto cargada OK")
    except Exception as e:
        print(f"[Audio] Error cargando música laberinto: {e}")

def play_maze_music():
    """Inicia la música del laberinto en su canal dedicado (loop)."""
    global _maze_music_channel, _maze_music_on
    _load_maze_music()
    if _maze_music_sound is None:
        return
    _maze_music_on = True
    try:
        # Canal 15: reservado exclusivamente para el laberinto
        _maze_music_channel = pygame.mixer.Channel(15)
        _maze_music_channel.set_volume(0.45)
        _maze_music_channel.play(_maze_music_sound, loops=-1)
    except Exception as e:
        print(f"[Audio] Error reproduciendo música laberinto: {e}")

def stop_maze_music():
    """Detiene completamente la música del laberinto."""
    global _maze_music_channel
    try:
        # Detener siempre el canal 15 directamente (no depender solo de la variable)
        pygame.mixer.Channel(15).stop()
    except Exception:
        pass
    try:
        if _maze_music_channel is not None:
            _maze_music_channel.stop()
            _maze_music_channel = None
    except Exception:
        pass

def toggle_maze_music():
    """Alterna encendido/apagado de la música del laberinto."""
    global _maze_music_on, _maze_music_channel
    _maze_music_on = not _maze_music_on
    try:
        if _maze_music_on:
            _load_maze_music()
            if _maze_music_sound is not None:
                _maze_music_channel = pygame.mixer.Channel(15)
                _maze_music_channel.set_volume(0.45)
                _maze_music_channel.play(_maze_music_sound, loops=-1)
        else:
            if _maze_music_channel is not None:
                _maze_music_channel.stop()
    except Exception as e:
        print(f"[Audio] Error toggle música laberinto: {e}")

def is_maze_music_on():
    return _maze_music_on

def toggle_music():
    try:
        if state.sonido_activado:
            pygame.mixer.music.unpause()
            _play_bg(state.escenario_actual)
        else:
            pygame.mixer.music.pause()
            stop_walk_sound()
    except Exception:
        pass
