# ═══════════════════════════════════════════════════════════════════
# Resources/vocabulary.py
# Banco de vocabulario en inglés para el mini-juego Tira de la Cuerda
# Formato: (palabra_incompleta, palabra_correcta, traducción_español)
# ═══════════════════════════════════════════════════════════════════

import random

VOCABULARY = [
    # 1. Saludos y Cortesía (Greetings & Politeness) - 13 palabras
    ("helo", "hello", "Hola"),
    ("hi", "hi", "Hola"),
    ("goodbye", "goodbye", "Adiós"),
    ("bye", "bye", "Adiós"),
    ("good mornng", "good morning", "Buenos días"),
    ("good afernoon", "good afternoon", "Buenas tardes"),
    ("good nite", "good night", "Buenas noches"),
    ("plez", "please", "Por favor"),
    ("thank yu", "thank you", "Gracias"),
    ("thanks", "thanks", "Gracias"),
    ("your welcome", "you are welcome", "De nada"),
    ("sorri", "sorry", "Lo siento"),
    ("excus mi", "excuse me", "Disculpa"),
    
    # 2. Información Personal y Familia (Personal Info & Family) - 14 palabras
    ("nam", "name", "Nombre"),
    ("ag", "age", "Edad"),
    ("yes", "yes", "Sí"),
    ("no", "no", "No"),
    ("i", "i", "Yo"),
    ("u", "you", "Tú/Usted"),
    ("he", "he", "Él"),
    ("she", "she", "Ella"),
    ("it", "it", "Eso"),
    ("moter", "mother", "Madre"),
    ("faher", "father", "Padre"),
    ("brther", "brother", "Hermano"),
    ("sistr", "sister", "Hermana"),
    ("frend", "friend", "Amigo"),
    
    # 3. Preguntas Básicas (Question Words) - 6 palabras
    ("wath", "what", "¿Qué?"),
    ("ware", "where", "¿Dónde?"),
    ("who", "who", "¿Quién?"),
    ("hao", "how", "¿Cómo?"),
    ("wen", "when", "¿Cuándo?"),
    ("why", "why", "¿Por qué?"),
    
    # 4. Números (Numbers) - 11 palabras
    ("ero", "zero", "Cero"),
    ("wan", "one", "Uno"),
    ("tu", "two", "Dos"),
    ("thre", "three", "Tres"),
    ("fur", "four", "Cuatro"),
    ("fiv", "five", "Cinco"),
    ("six", "six", "Seis"),
    ("sven", "seven", "Siete"),
    ("eigt", "eight", "Ocho"),
    ("nin", "nine", "Nueve"),
    ("ten", "ten", "Diez"),
    
    # 5. Verbos Esenciales (Essential Verbs) - 7 palabras
    ("bee", "be", "Ser/Estar"),
    ("hav", "have", "Tener"),
    ("goe", "go", "Ir"),
    ("et", "eat", "Comer"),
    ("drnk", "drink", "Beber"),
    ("wnt", "want", "Querer"),
    ("lik", "like", "Gustar"),
    
    # 6. Objetos Cotidianos (Everyday Objects) - 7 palabras
    ("watr", "water", "Agua"),
    ("fod", "food", "Comida"),
    ("hous", "house", "Casa"),
    ("cr", "car", "Auto"),
    ("bak", "book", "Libro"),
    ("fone", "phone", "Teléfono"),
    ("clok", "clock", "Reloj"),
    
    # 7. Colores (Colors) - 6 palabras
    ("red", "red", "Rojo"),
    ("blu", "blue", "Azul"),
    ("yalow", "yellow", "Amarillo"),
    ("gren", "green", "Verde"),
    ("blak", "black", "Negro"),
    ("whit", "white", "Blanco"),
]

def get_random_word():
    """Retorna una palabra aleatoria: (incompleta, correcta, traducción)"""
    return random.choice(VOCABULARY)

def get_random_words(count=5):
    """Retorna lista de palabras aleatorias sin repetir"""
    return random.sample(VOCABULARY, min(count, len(VOCABULARY)))

