# ═══════════════════════════════════════════════════════════════════
# Actions/rope_pull_game.py
# Mini-juego Tira de la Cuerda - Duelo de Gramática en Inglés
# ═══════════════════════════════════════════════════════════════════

import random
from Resources.vocabulary import get_random_word
from Actions import audio
from Actions.audio import play_english_word


class RopePullGameState:
    """Estado y lógica del mini-juego Tira de la Cuerda

    - show_instructions: si True el juego espera a que el usuario presione ENTER
      para iniciar (no hay timer automático)
    - timer: segundos por turno (ahora 10)
    - health_1 / health_2: vidas del jugador (empiezan en 10)
    - rope_progress: valor visual 0..1 que representa cuánto se ha movido la cuerda
    """

    def __init__(self):
        self.active = False
        self.char1_id = None
        self.char2_id = None
        self.char1_name = "Player1"
        self.char2_name = "Player2"

        # Expresiones temporales
        self.char1_expression = "normal"
        self.char2_expression = "normal"
        self.expression_timer = 0.0

        # Lógica del juego
        self.current_player = 1  # 1 o 2
        self.word_incomplete = ""
        self.word_correct = ""
        self.word_translation = ""
        self.player_input = ""

        self.timer = 10.0  # 10 segundos por turno (mejora solicitada)
        self.health_1 = 10  # Vidas jugador 1
        self.health_2 = 10  # Vidas jugador 2
        self.winner = None
        self.game_over = False

        # Mostrar instrucciones hasta que el jugador presione ENTER
        self.show_instructions = True

        # Animación / visual
        self.input_cursor_blink = 0.0
        self.message = ""
        self.message_timer = 0.0
        self.rope_shake = 0.0
        self.rope_visual_offset = 0.5  # 0.0 (izq) .. 1.0 (der) centro 0.5
        self.rope_target_offset = 0.5
        self.falling_player = None
        self.fall_progress = 0.0
        self.paused = False

        # Corrección: mostrar palabra correcta al fallar
        self.correction_word = ""       # Palabra correcta a mostrar
        self.correction_timer = 0.0     # Tiempo que se muestra la corrección

        self.game_time = 0.0  # Ciclo día/atardecer/noche

    def reset(self):
        """Inicia / reinicia el mini-juego (no las vidas)."""
        self.current_player = random.choice([1, 2])
        self.player_input = ""
        self.timer = 10.0
        self.message = ""
        self.message_timer = 0.0
        self.rope_shake = 0.0
        self.rope_visual_offset = 0.5
        self.rope_target_offset = 0.5
        self.falling_player = None
        self.fall_progress = 0.0
        self.game_over = False
        self.game_time = 0.0
        self.correction_word = ""
        self.correction_timer = 0.0
        self.char1_expression = "normal"
        self.char2_expression = "normal"
        self.expression_timer = 0.0
        self.word_incomplete, self.word_correct, self.word_translation = get_random_word()

    def start_round(self):
        self.player_input = ""
        self.timer = 10.0
        self.word_incomplete, self.word_correct, self.word_translation = get_random_word()

    def submit_answer(self):
        """Procesa la respuesta actual del jugador.

        Reglas: si acierta -> al oponente se le resta 1 vida; si falla -> al propio jugador
        se le resta 1 vida. También se actualiza la animación de la cuerda y se muestra
        mensaje temporal.
        """
        entered = self.player_input.strip().lower()
        correct = self.word_correct.lower()

        is_correct = entered == correct

        if is_correct:
            # Oponente pierde una vida — reproducir sonido de la palabra
            try: play_english_word(self.word_correct)
            except Exception: pass
            if self.current_player == 1:
                # Jugador 1 acertó => mostrar happy, rival sad
                self.char1_expression = "happy"
                self.char2_expression = "sad"
                self.health_2 = max(0, self.health_2 - 1)
                self.message = f"{self.char1_name} ACERTÓ!"
                self.rope_target_offset = max(0.0, self.rope_visual_offset - 0.12)
            else:
                # Jugador 2 acertó => mostrar happy, rival sad
                self.char2_expression = "happy"
                self.char1_expression = "sad"
                self.health_1 = max(0, self.health_1 - 1)
                self.message = f"{self.char2_name} ACERTÓ!"
                self.rope_target_offset = min(1.0, self.rope_visual_offset + 0.12)
        else:
            # El propio jugador pierde una vida
            # Mostrar corrección y reproducir sonido de la palabra correcta
            self.correction_word = self.word_correct
            self.correction_timer = 2.0  # Mostrar 2 segundos
            try: play_english_word(self.word_correct)
            except Exception: pass
            if self.current_player == 1:
                self.health_1 = max(0, self.health_1 - 1)
                self.message = f"{self.char1_name} FALLÓ!"
                self.rope_target_offset = min(1.0, self.rope_visual_offset + 0.08)
            else:
                self.health_2 = max(0, self.health_2 - 1)
                self.message = f"{self.char2_name} FALLÓ!"
                self.rope_target_offset = max(0.0, self.rope_visual_offset - 0.08)

        # Efecto de sacudida breve (moderado para zoom suave)
        self.rope_shake = 0.35
        self.message_timer = 1.4
        self.expression_timer = 2.0  # Mostrar expresión 2 segundos

        # Chequear caídas de vidas y animación de caída
        if self.health_1 <= 0:
            self.falling_player = 1
        elif self.health_2 <= 0:
            self.falling_player = 2
        # Reproducir sonido de caída si se inicia la animación de caída
        if self.falling_player is not None:
            try:
                audio.play_sound('concha')
            except Exception:
                pass

        # Pasar al siguiente jugador si el juego no terminó inmediatamente
        if not self.game_over and self.falling_player is None:
            self.current_player = 3 - self.current_player
            self.start_round()

    def update(self, dt):
        """Actualiza animaciones y lógica; dt en segundos."""
        if self.paused:
            return

        if self.show_instructions:
            return

        # Pausar turno mientras se muestra la corrección
        if self.correction_timer > 0:
            self.correction_timer -= dt
            if self.correction_timer <= 0:
                self.correction_word = ""
                self.correction_timer = 0.0
            return

        if self.game_over:
            return

        # Timer del turno
        self.timer -= dt
        if self.timer <= 0:
            # Tiempo agotado: el jugador pierde
            self.player_input = ""
            self.message = "¡Tiempo agotado!"
            self.message_timer = 1.2
            # aplicar penalización
            if self.current_player == 1:
                self.health_1 = max(0, self.health_1 - 1)
                self.rope_target_offset = min(1.0, self.rope_visual_offset + 0.08)
            else:
                self.health_2 = max(0, self.health_2 - 1)
                self.rope_target_offset = max(0.0, self.rope_visual_offset - 0.08)

            # revisar caída
            if self.health_1 <= 0:
                self.falling_player = 1
            elif self.health_2 <= 0:
                self.falling_player = 2
            if self.falling_player is not None:
                try:
                    audio.play_sound('concha')
                except Exception:
                    pass
            else:
                self.current_player = 3 - self.current_player
                self.start_round()

        # Animaciones: lerp visual de la cuerda hacia target
        lerp_t = min(1.0, dt * 6.0)
        self.rope_visual_offset = self.rope_visual_offset + (self.rope_target_offset - self.rope_visual_offset) * lerp_t

        # Reducir sacudida
        if self.rope_shake > 0:
            self.rope_shake = max(0.0, self.rope_shake - dt * 1.8)

        # Ciclo día/atardecer/noche
        self.game_time += dt

        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

        if self.expression_timer > 0:
            self.expression_timer = max(0.0, self.expression_timer - dt)
        else:
            self.char1_expression = "normal"
            self.char2_expression = "normal"

        # Caída del jugador
        if self.falling_player is not None:
            self.fall_progress += dt * 0.8
            if self.fall_progress >= 1.0:
                # Animación terminada => declarar ganador
                if self.falling_player == 1:
                    self.winner = 2
                else:
                    self.winner = 1
                self.game_over = True


# Instancia global
game_instance = RopePullGameState()

