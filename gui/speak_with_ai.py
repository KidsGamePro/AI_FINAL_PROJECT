import pygame
import sys
import os
import random
import threading
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class SpeakWithAIScreen:
    def __init__(self, screen, ai_engine):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.ai = ai_engine

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.COLOR_BG_TOP = (74, 144, 226)       
        self.COLOR_BG_BOTTOM = (120, 255, 230)   
        self.CARD_BG = (255, 255, 255)
        self.TEXT_WHITE = (255, 255, 255)
        self.TEXT_DARK = (44, 62, 80)

        self.font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.large_font = pygame.font.SysFont("Segoe UI Emoji", 50)
        self.status_font = pygame.font.SysFont("Segoe UI Emoji", 24)

        self.btn_back_rect = pygame.Rect(40, 110, 80, 50)
        self.btn_mic_rect = pygame.Rect(320, 450, 360, 80)     
        self.btn_speaker_rect = pygame.Rect(580, 320, 60, 60) 
        self.btn_restart_rect = pygame.Rect(240, 430, 240, 75)
        self.btn_home_rect = pygame.Rect(520, 430, 240, 75)

        self.pressed_back_btn = False
        self.pressed_mic_btn = False
        self.pressed_speaker_btn = False
        self.pressed_end_btn = None

        self.status_text = "Click START MIC to record your voice! 🎙️"
        self.is_listening = False  
        self.recognized_text = ""

        self.show_meme = False
        self.is_correct_answer = False  
        self.blurred_bg_surface = None  
        self.meme_display_start_time = 0   

        self.model_path = "model"
        if not os.path.exists(self.model_path):
            self.model = None
        else:
            self.model = Model(self.model_path)
            allowed_words = ["banana", "apple", "lion", "cat", "dog", "[unk]"] 
            self.vosk_recognizer = KaldiRecognizer(self.model, 16000, json.dumps(allowed_words))
        
        self.audio_queue = queue.Queue()
        self.audio_stream = None

        self.recording_start_time = 0
        self.MAX_RECORDING_SECONDS = 6  

        self.question_count = 0
        self.MAX_QUESTIONS = 10  
        self.game_over = False

        self.loaded_images = {}
        self.draw_gradient_background()
        self.next_question()

    def draw_gradient_background(self):
        self.bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.COLOR_BG_TOP[0] * (1 - ratio) + self.COLOR_BG_BOTTOM[0] * ratio)
            g = int(self.COLOR_BG_TOP[1] * (1 - ratio) + self.COLOR_BG_BOTTOM[1] * ratio)
            b = int(self.COLOR_BG_TOP[2] * (1 - ratio) + self.COLOR_BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (self.screen_width, y))

    def load_image(self, image_path, size=(230, 230)):
        if image_path in self.loaded_images:
            return self.loaded_images[image_path]
        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, size)
                self.loaded_images[image_path] = img
                return img
            except Exception:
                return None
        return None

    def make_blur_background(self):
        raw_surface = pygame.Surface((self.screen_width, self.screen_height))
        raw_surface.blit(self.bg_surface, (0, 0))
        self.draw_game_elements(raw_surface) 
        
        scale_factor = 10  
        small_surf = pygame.transform.smoothscale(
            raw_surface, 
            (self.screen_width // scale_factor, self.screen_height // scale_factor)
        )
        self.blurred_bg_surface = pygame.transform.smoothscale(small_surf, (self.screen_width, self.screen_height))
        
        dark_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 60)) 
        self.blurred_bg_surface.blit(dark_overlay, (0, 0))

    def play_pre_recorded_audio(self):
        audio_path = self.current_question.get("audio")
        if audio_path and os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
            except Exception:
                pass

    def next_question(self):
        if self.question_count >= self.MAX_QUESTIONS:
            return
        self.question_count += 1
        self.current_question = self.ai.generate_question()
        self.status_text = "Click START MIC to record your voice! 🎙️"
        self.recognized_text = ""
        self.is_listening = False
        self.show_meme = False

    def audio_callback(self, indata, frames, time, status):
        if self.is_listening:
            self.audio_queue.put(bytes(indata))

    def start_recording(self):
        self.audio_queue.queue.clear()
        self.recording_start_time = pygame.time.get_ticks() 
        self.audio_stream = sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype='int16',
            channels=1, callback=self.audio_callback
        )
        self.audio_stream.start()

    def stop_and_analyze(self):
        self.is_listening = False
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None

        complete_data = b""
        while not self.audio_queue.empty():
            complete_data += self.audio_queue.get()

        if self.model and self.vosk_recognizer:
            self.vosk_recognizer.AcceptWaveform(complete_data)
            result_json = json.loads(self.vosk_recognizer.Result())
            text = result_json.get("text", "").strip().upper()
        else:
            text = ""
        
        if text == "[UNK]" or text == "":
            self.recognized_text = ""   
        else:
            self.recognized_text = text

        correct_word = self.current_question["correct_word"].upper()

        is_correct = (correct_word in text) and (text != "")
        if not is_correct and len(text) >= 3 and text != "[UNK]":
            if text[0] == correct_word[0] and text[-1] == correct_word[-1]:
                is_correct = True

        self.make_blur_background() 
        self.show_meme = True
        self.meme_display_start_time = pygame.time.get_ticks() 

        if is_correct:
            self.is_correct_answer = True
            self.status_text = "🎉 EXCELLENT! Correct Pronunciation! 🎉"
            self.ai.score += 20
        else:
            self.is_correct_answer = False
            self.status_text = f"Oops! It should be {correct_word}."

    def draw_game_elements(self, target_surf):
        progress_rect = pygame.Rect(40, 30, 220, 60)
        pygame.draw.rect(target_surf, (116, 185, 255), progress_rect, border_radius=20)
        progress_text = self.font.render(f"📋 {self.question_count}/{self.MAX_QUESTIONS}", True, self.TEXT_WHITE)
        target_surf.blit(progress_text, progress_text.get_rect(center=progress_rect.center))

        pygame.draw.rect(target_surf, (255, 107, 129), self.btn_back_rect, border_radius=15)
        back_text = self.font.render("↩️", True, self.TEXT_WHITE)
        target_surf.blit(back_text, back_text.get_rect(center=self.btn_back_rect.center))

        score_rect = pygame.Rect(740, 30, 220, 60)
        pygame.draw.rect(target_surf, (255, 234, 167), score_rect, border_radius=20)
        score_surface = self.font.render(f"⭐ Score: {self.ai.score}", True, (214, 142, 12))
        target_surf.blit(score_surface, score_surface.get_rect(center=score_rect.center))

        center_card = pygame.Rect(375, 115, 250, 250)
        pygame.draw.rect(target_surf, self.CARD_BG, center_card, border_radius=30)
        img = self.load_image(self.current_question["image"], (210, 210))
        if img: target_surf.blit(img, (395, 135))

        pygame.draw.rect(target_surf, (52, 152, 219), self.btn_speaker_rect, border_radius=50)
        spk_text = self.font.render("🔊", True, self.TEXT_WHITE)
        target_surf.blit(spk_text, spk_text.get_rect(center=self.btn_speaker_rect.center))

        status_surf = self.status_font.render(self.status_text, True, self.TEXT_DARK)
        target_surf.blit(status_surf, status_surf.get_rect(center=(self.screen_width // 2, 410)))

        mic_color = (231, 76, 60) if self.is_listening else (46, 213, 115)
        pygame.draw.rect(target_surf, mic_color, self.btn_mic_rect, border_radius=25)
        
        if self.is_listening:
            elapsed = (pygame.time.get_ticks() - self.recording_start_time) // 1000
            remaining = max(0, self.MAX_RECORDING_SECONDS - elapsed)
            mic_label = f"STOP ({remaining}s) 🛑"
        else:
            mic_label = "START MIC 🎤"
            
        mic_text = self.font.render(mic_label, True, self.TEXT_WHITE)
        target_surf.blit(mic_text, mic_text.get_rect(center=self.btn_mic_rect.center))

    def draw(self):
        if self.is_listening:
            elapsed_time = (pygame.time.get_ticks() - self.recording_start_time) / 1000
            if elapsed_time >= self.MAX_RECORDING_SECONDS:
                self.stop_and_analyze()

        if self.show_meme:
            meme_elapsed = pygame.time.get_ticks() - self.meme_display_start_time
            if meme_elapsed >= 2200:
                self.show_meme = False
                self.blurred_bg_surface = None
                if self.is_correct_answer:
                    if self.question_count >= self.MAX_QUESTIONS:
                        self.game_over = True
                    else:
                        self.next_question()
                else:
                    self.is_listening = False
                    self.status_text = "Click START MIC to try again! 🎙️"

        if self.show_meme and self.blurred_bg_surface:
            self.screen.blit(self.blurred_bg_surface, (0, 0))
            
            meme_card = pygame.Rect(300, 110, 400, 400)
            pygame.draw.rect(self.screen, self.CARD_BG, meme_card, border_radius=30)
            
            theme_color = (46, 213, 115) if self.is_correct_answer else (231, 76, 60)
            pygame.draw.rect(self.screen, theme_color, meme_card, width=4, border_radius=30)

            title_str = "🎉 Brilliant! 🎉" if self.is_correct_answer else "Oops! Try Again! 🤔"
            m_title = self.font.render(title_str, True, theme_color)
            self.screen.blit(m_title, m_title.get_rect(center=(self.screen_width // 2, 150)))

            meme_path = "assets/memes/correct1.png" if self.is_correct_answer else "assets/memes/try_again1.png"
            meme_img = self.load_image(meme_path, (220, 220))
            if meme_img:
                self.screen.blit(meme_img, (390, 190))
            
            if self.recognized_text:
                said_text = f'You said: "{self.recognized_text}"'
            else:
                said_text = "We couldn't catch that. Please try again! 🎙️"
                
            said_surf = self.status_font.render(said_text, True, self.TEXT_DARK)
            self.screen.blit(said_surf, said_surf.get_rect(center=(self.screen_width // 2, 450)))

        elif not self.game_over:
            self.screen.blit(self.bg_surface, (0, 0))
            self.draw_game_elements(self.screen)
            if self.recognized_text and not self.is_listening:
                rec_surf = self.font.render(f'You said: "{self.recognized_text}"', True, (243, 156, 18))
                self.screen.blit(rec_surf, rec_surf.get_rect(center=(self.screen_width // 2, 560)))
        else:
            self.screen.blit(self.bg_surface, (0, 0))
            end_card = pygame.Rect(150, 100, 700, 450)
            pygame.draw.rect(self.screen, self.CARD_BG, end_card, border_radius=40)
            win_title = self.large_font.render("🎉 SPEAKING COMPLETED! 🎉", True, (74, 142, 226))
            self.screen.blit(win_title, win_title.get_rect(center=(self.screen_width // 2, 180)))
            
            final_score_text = self.font.render(f"Amazing! You scored ⭐ {self.ai.score} Points!", True, self.TEXT_DARK)
            self.screen.blit(final_score_text, final_score_text.get_rect(center=(self.screen_width // 2, 280)))

            pygame.draw.rect(self.screen, (0, 184, 148), self.btn_restart_rect, border_radius=25)
            res_txt = self.font.render("Play Again 🔄", True, self.TEXT_WHITE)
            self.screen.blit(res_txt, res_txt.get_rect(center=self.btn_restart_rect.center))

            pygame.draw.rect(self.screen, (255, 159, 26), self.btn_home_rect, border_radius=25)
            home_txt = self.font.render("Menu 🏠", True, self.TEXT_WHITE)
            self.screen.blit(home_txt, home_txt.get_rect(center=self.btn_home_rect.center))

        pygame.display.flip()

    def handle_click(self, mouse_pos):
        if self.show_meme:
            return

        if not self.game_over:
            if self.btn_back_rect.collidepoint(mouse_pos):
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "GO_HOME"}))
                return

            if self.btn_speaker_rect.collidepoint(mouse_pos):
                self.play_pre_recorded_audio()
                return

            if self.btn_mic_rect.collidepoint(mouse_pos):
                if not self.is_listening:
                    self.is_listening = True
                    self.status_text = "Recording... Speak now! 🔴"
                    self.recognized_text = ""
                    self.start_recording()
                else:
                    self.stop_and_analyze()
        else:
            if self.btn_restart_rect.collidepoint(mouse_pos):
                self.ai.score = 0
                self.question_count = 0
                self.game_over = False
                self.next_question()
            elif self.btn_home_rect.collidepoint(mouse_pos):
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "GO_HOME"}))

    def handle_release(self, mouse_pos):
        self.pressed_back_btn = False
        self.pressed_mic_btn = False
        self.pressed_speaker_btn = False
        self.pressed_end_btn = None