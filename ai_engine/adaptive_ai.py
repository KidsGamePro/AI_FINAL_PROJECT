import random

class AdaptiveAIEngine:
    def __init__(self, dataset):
        self.dataset = dataset
        self.score = 0
        self.mistake_tracker = {}
        self.correct_count = 0
        self.incorrect_count = 0
        self.game_mode = None  # "card_game" or "speak_with_ai"

    def generate_question(self):
        """
        Adaptive selection: 40% chance to select a word the user previously made a mistake on,
        provided there are mistakes in the tracker.
        """
        wrong_words = [word for word, count in self.mistake_tracker.items() if count > 0]
        
        correct_item = None
        if wrong_words and random.random() < 0.40:
            chosen_word = random.choice(wrong_words).upper()
            for item in self.dataset:
                if item["correct_word"].upper() == chosen_word:
                    correct_item = item
                    break

        if not correct_item:
            correct_item = random.choice(self.dataset)

        # Shuffle the options to keep it engaging
        options = list(correct_item["options"])
        random.shuffle(options)

        # Return a copy with shuffled options to avoid mutating original dataset
        return {
            "image": correct_item["image"],
            "audio": correct_item["audio"],
            "options": options,
            "correct_word": correct_item["correct_word"],
            "hint": correct_item["hint"]
        }

    def check_answer(self, user_answer, correct_answer):
        user_answer = user_answer.strip().upper()
        correct_answer = correct_answer.strip().upper()

        if user_answer == correct_answer:
            self.score += 15
            self.correct_count += 1
            
            # Remove from mistake tracker if corrected
            if correct_answer in self.mistake_tracker:
                del self.mistake_tracker[correct_answer]
                
            return {
                "status": "correct",
                "meme_type": "happy",
                "hint": None
            }
        else:
            self.incorrect_count += 1
            if correct_answer not in self.mistake_tracker:
                self.mistake_tracker[correct_answer] = 1
            else:
                self.mistake_tracker[correct_answer] += 1

            # Retrieve hint from dataset
            current_hint = "Try again, you can do it! 💪"
            for item in self.dataset:
                if item["correct_word"].upper() == correct_answer:
                    current_hint = item["hint"]
                    break

            # If user makes multiple mistakes on the same word, add starting-letter help
            if self.mistake_tracker[correct_answer] >= 2:
                current_hint = f"Starts with '{correct_answer[0]}'! " + current_hint

            return {
                "status": "wrong",
                "meme_type": "try_again",
                "hint": current_hint
            }

    def reset_progress(self):
        """Reset scores and trackers for a fresh session"""
        self.score = 0
        self.mistake_tracker = {}
        self.correct_count = 0
        self.incorrect_count = 0
