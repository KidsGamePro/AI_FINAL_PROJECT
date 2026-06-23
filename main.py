import sys
import os
import json

try:
    import pygame
except ImportError:
    print("Error: pygame is not installed. Please install pygame and try again.")
    sys.exit(1)

from ai_engine.adaptive_ai import AdaptiveAIEngine
from game_data.vocabulary import WORDS_DATASET
from gui.start_screen import StartScreen


class EnglishAIEngine(AdaptiveAIEngine):
    def __init__(self):
        # Initialize the Adaptive AI Engine with our vocabulary dataset
        super().__init__(WORDS_DATASET)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stats_file = os.path.join(self.base_dir, "assets", "game_stats.json")
        self.stats = {
            "card_game": {"correct": 0, "incorrect": 0, "total_score": 0},
            "speak_with_ai": {"correct": 0, "incorrect": 0, "total_score": 0}
        }
        self.load_stats()

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
