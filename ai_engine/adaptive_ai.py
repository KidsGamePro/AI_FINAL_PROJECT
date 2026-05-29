import random

class AdaptiveAIEngine:
    def __init__(self, dataset):
        """
        AI Tizimini ishga tushirish.
        dataset: O'yin ichidagi rasm va so'zlar ro'yxati (lug'at)
        """
        self.dataset = dataset
        self.score = 0
        # Bolaning xatolarini kuzatib borish uchun lug'at (AI asosi)
        self.mistake_tracker = {} 

    def generate_question(self):
        """
        Yangi savol va 4 ta javob variantini tayyorlaydi.
        """
        # Dataset ichidan tasodifiy bitta obyektni tanlaymiz (Masalan: Kuchuk)
        correct_item = random.choice(self.dataset)
        image_path = correct_item["image"]
        correct_answer = correct_item["word"]

        # Noto'g'ri javoblarni tanlash (variantlar orasida to'g'ri javob takrorlanmasligi uchun)
        wrong_pool = [item["word"] for item in self.dataset if item["word"] != correct_answer]
        wrong_answers = random.sample(wrong_pool, 3)

        # To'g'ri va noto'g'ri javoblarni birlashtirib, aralashtiramiz
        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        return {
            "image": image_path,
            "correct_word": correct_answer,
            "options": options
        }

    def check_answer(self, user_answer, correct_answer):
        """
        Bolaning javobini tekshiradi va AI mantiqini ishga tushiradi.
        """
        if user_answer == correct_answer:
            self.score += 10 # To'g'ri bo'lsa 10 ochko
            # Agar bola bu so'zda oldin xato qilgan bo'lsa, trekkerdan o'chiramiz
            if correct_answer in self.mistake_tracker:
                del self.mistake_tracker[correct_answer]
            return {
                "status": "correct",
                "score": self.score,
                "meme_type": "happy" # GUI bunga qarab quvnoq mem ko'rsatadi
            }
        else:
            # Bola xato qildi! AI buni eslab qoladi
            if correct_answer not in self.mistake_tracker:
                self.mistake_tracker[correct_answer] = 1
            else:
                self.mistake_tracker[correct_answer] += 1

            # Adaptive AI (Moslashuvchanlik) qismi:
            # Agar bola bitta so'zda 2 marta yoki undan ko'p xato qilsa, yordam (Hint) beramiz
            hints = None
            if self.mistake_tracker[correct_answer] >= 2:
                hints = f"Hint: This word starts with '{correct_answer[0].upper()}'"

            return {
                "status": "wrong",
                "score": self.score,
                "meme_type": "try_again", # GUI bunga qarab "qayta urinish" memini ko'rsatadi
                "hint": hints
            }

    def get_adaptive_difficulty(self):
        """
        O'yin davomida bolaga qiyin bo'layotgan so'zlarni qaytaradi.
        Keyinchalik shu so'zlarni o'yin ko'proq qaytara boshlaydi.
        """
        return [word for word, count in self.mistake_tracker.items() if count > 0]
