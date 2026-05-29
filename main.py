import pygame
import sys
import random
from gui.start_screen import StartScreen

class EnglishAIEngine:
    def __init__(self):
        self.score = 0
        self.mistake_tracker = {}
        
        
        self.dataset = [
            {
                "image": "assets/images/banana.png",
                "audio": "assets/sounds/banana.mp3",
                "options": ["APPLE", "GRAPE", "BANANA", "APRICOT"],
                "correct_word": "BANANA",
                "hint": "It is a long yellow fruit!"
            },
            {
                "image": "assets/images/apple.png",
                "audio": "assets/sounds/apple.mp3",
                "options": ["APPLE", "ORANGE", "CHERRY", "PEAR"],
                "correct_word": "APPLE",
                "hint": "It can be red or green and keeps the doctor away!"
            },
            {
                "image": "assets/images/lion.png",
                "audio": "assets/sounds/lion.mp3",
                "options": ["TIGER", "CAT", "LION", "DOG"],
                "correct_word": "LION",
                "hint": "He is the King of the Jungle! 👑"
            },
            {
                "image": "assets/images/cat.png",
                "audio": "assets/sounds/cat.mp3",
                "options": ["DOG", "CAT", "RABBIT", "LION"],
                "correct_word": "CAT",
                "hint": "It says 'Meow' and loves to drink milk! 🐱"
            },
            {
                "image": "assets/images/dog.png",
                "audio": "assets/sounds/dog.mp3",
                "options": ["WOLF", "FOX", "CAT", "DOG"],
                "correct_word": "DOG",
                "hint": "Man's best friend! It says 'Woof Woof'! 🐶"
            }
        ]
        
    def generate_question(self):
        return random.choice(self.dataset)
    
    def check_answer(self, clicked, correct):
        if clicked == correct:
            self.score += 15
            return {"meme_type": "happy", "hint": None}
        else:
            current_hint = "Try again, you can do it! 💪"
            for q in self.dataset:
                if q["correct_word"] == correct:
                    current_hint = q["hint"]
            return {"meme_type": "try_again", "hint": current_hint}

def main():
    pygame.init()
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 650
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Kiddy Learner ✨")
    
    ai_instance = EnglishAIEngine() 
    app = StartScreen(screen, ai_instance)
    app.run()

if __name__ == "__main__":
    main()