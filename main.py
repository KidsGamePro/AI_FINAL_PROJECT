try:
    import pygame
except ImportError:
    print("Error: pygame is not installed. Please install pygame and try again.")
    sys.exit(1)

import sys
import random
import json
import os
from gui.start_screen import StartScreen

class EnglishAIEngine:
    def __init__(self):
        self.score = 0
        self.mistake_tracker = {}
        self.correct_count = 0
        self.incorrect_count = 0
        self.game_mode = None  # "WORDS" or "SPEAK"
        
        # Separate stats for each game
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stats_file = os.path.join(self.base_dir, "assets", "game_stats.json")
        self.stats = {
            "card_game": {"correct": 0, "incorrect": 0, "total_score": 0},
            "speak_with_ai": {"correct": 0, "incorrect": 0, "total_score": 0}
        }
        self.load_stats()
        
        
        self.dataset = [  #pip install -U openai-whisper
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
            self.correct_count += 1
            return {"meme_type": "happy", "hint": None}
        else:
            self.incorrect_count += 1
            current_hint = "Try again, you can do it! 💪"
            for q in self.dataset:
                if q["correct_word"] == correct:
                    current_hint = q["hint"]
            return {"meme_type": "try_again", "hint": current_hint}

    def load_stats(self):
        """Load stats from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            else:
                self.save_stats()
        except Exception as e:
            print(f"Error loading stats: {e}")

    def save_stats(self):
        """Save stats to file"""
        try:
            os.makedirs(os.path.dirname(self.stats_file) or ".", exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def update_stats(self, game_mode, correct_ans, incorrect_ans, score_gained):
        """Update stats for the game mode and save"""
        if game_mode in self.stats:
            self.stats[game_mode]["correct"] += correct_ans
            self.stats[game_mode]["incorrect"] += incorrect_ans
            self.stats[game_mode]["total_score"] += score_gained
            self.save_stats()

    def reset_progress(self):
        """Resets score and answer statistics. Called whenever a fresh game/session starts."""
        self.score = 0
        self.mistake_tracker = {}
        self.correct_count = 0
        self.incorrect_count = 0

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