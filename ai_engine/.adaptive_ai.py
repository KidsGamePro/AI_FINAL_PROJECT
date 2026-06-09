
import random

class AdaptiveAIEngine:
    def __init__(self, dataset):
        self.dataset = dataset
        self.score = 0
        self.mistake_tracker = {} 

    def generate_question(self):
        # Adaptiv mantiq: Agar xato qilingan so'zlar bo'lsa, ularni qayta so'rash ehtimoli 40%
        # Bu o'yinni bola uchun haqiqiy intellektual moslashuvchan qiladi
        wrong_words = [word for word, count in self.mistake_tracker.items() if count > 0]
        
        correct_item = None
        if wrong_words and random.random() < 0.40:
            # Xato qilingan so'zlar ichidan tasodifiy birini tanlash
            chosen_word = random.choice(wrong_words)
            for item in self.dataset:
                if item["word"] == chosen_word:
                    correct_item = item
                    break

        # Agar xato qilingan so'zlar bo'lmasa yoki 40% lik imkoniyatdan o'tmasa, umumiy bazadan tanlaydi
        if not correct_item:
            correct_item = random.choice(self.dataset)

        image_path = correct_item["image"]
        correct_answer = correct_item["word"]

        # Noto'g'ri javoblar hovuzini yig'ish
        wrong_pool = [item["word"] for item in self.dataset if item["word"] != correct_answer]
        
        # Dataset xavfsizligi: Agar baza juda kichik bo'lsa, crash bo'lishini oldini olish
        sample_size = min(3, len(wrong_pool))
        wrong_answers = random.sample(wrong_pool, sample_size) if wrong_pool else []

        # Variantlarni birlashtirish va aralashtirish
        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        return {
            "image": image_path,
            "correct_word": correct_answer,
            "options": options
        }

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.score += 10  
            
            # Agar oldin xato qilgan bo'lsa va endi to'g'ri topsa, ro'yxatdan o'chiradi yoki kamaytiradi
            if correct_answer in self.mistake_tracker:
                del self.mistake_tracker[correct_answer]
                
            return {
                "status": "correct",
                "score": self.score,
                "meme_type": "happy"  
            }
        else:
            if correct_answer not in self.mistake_tracker:
                self.mistake_tracker[correct_answer] = 1
            else:
                self.mistake_tracker[correct_answer] += 1

            hints = None
            # Bolaga motivatsiya beruvchi dinamik yordamchi shama (Hint)
            if self.mistake_tracker[correct_answer] >= 2:
                hints = f"Hint: This word starts with '{correct_answer[0].upper()}'"

            return {
                "status": "wrong",
                "score": self.score,
                "meme_type": "try_again",  
                "hint": hints
            }

    def get_adaptive_difficulty(self):
        return [word for word, count in self.mistake_tracker.items() if count > 0]
