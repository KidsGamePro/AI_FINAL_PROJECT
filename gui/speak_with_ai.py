import pygame
import sys
import os
import json
import math
import random
import queue
from ai_engine.effects import StarParticle, ShakeEffect

try:
    from ai_engine.audio_manager import AudioManager
except Exception:
    AudioManager = None

class SpeakWithAIScreen:
    def __init__(self, screen, ai_engine):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.ai = ai_engine

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"pygame mixer init failed: {e}")

        self.COLOR_BG_TOP = (74, 144, 226)       
        self.COLOR_BG_BOTTOM = (120, 255, 230)   
        self.CARD_BG = (255, 255, 255)
        self.TEXT_WHITE = (255, 255, 255)
        self.TEXT_DARK = (44, 62, 80)

        self.font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.large_font = pygame.font.SysFont("Segoe UI Emoji", 50)
        self.hint_font = pygame.font.SysFont("Segoe UI Emoji", 36, bold=True)
        self.status_font = pygame.font.SysFont("Segoe UI Emoji", 26)

        self.btn_back_rect = pygame.Rect(40, 30, 80, 50)
        self.btn_mic_rect = pygame.Rect(320, 520, 360, 90)
        self.btn_speaker_rect = pygame.Rect(655, 310, 70, 70)
        
        # Fixed: moved end-screen buttons to y=430 so they are visible and clickable
        self.btn_restart_rect = pygame.Rect(220, 430, 240, 75)
        self.btn_home_rect = pygame.Rect(520, 430, 240, 75)

        self.hint_bounce_phase = 0.0
        self.hint_bounce_amplitude = 8
        self.hint_bounce_speed = 0.08

        self.auto_audio_played = False
        self.pressed_back_btn = False
        self.pressed_mic_btn = False
        self.pressed_speaker_btn = False
        self.pressed_end_btn = None

        self.status_text = "Click START MIC to record your voice! 🎙️"
        self.is_listening = False  
        self.recognized_text = ""
        self.hint_text = ""  

        self.show_meme = False
        self.is_correct_answer = False  
        self.blurred_bg_surface = None  
        self.meme_display_start_time = 0   

        self.speech_enabled = False
        self.model = None
        self.vosk_recognizer = None
        self._sd = None

        # Speech recognition setup (Vosk + SoundDevice)
        try:
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer
            self._sd = sd

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(project_root, "model")
            
            if os.path.exists(model_path):
                self.model = Model(model_path)
                allowed_words = ["banana", "apple", "lion", "cat", "dog", "[unk]"]
                self.vosk_recognizer = KaldiRecognizer(self.model, 16000, json.dumps(allowed_words))
                self.speech_enabled = True
            else:
                print(f"Speech recognition model directory not found at: {model_path}")
        except Exception as e:
            print("Speech features disabled (packages or model init error):", e)
        
        self.audio_queue = queue.Queue()
        self.audio_stream = None

        self.recording_start_time = 0
        self.MAX_RECORDING_SECONDS = 5  

        self.question_count = 0
        self.MAX_QUESTIONS = 10  
        self.game_over = False
        
        self.shake_effect = ShakeEffect(intensity=8, duration=15)
        self.particles = []
        self.loaded_images = {}
        
        self.draw_gradient_background()
        
        try:
            self.audio = AudioManager() if AudioManager else None
        except Exception as e:
            print(f"SpeakWithAIScreen audio init failed: {e}")
            self.audio = None
        
        if self.audio:
            try:
                self.audio.play_music("assets/sounds/background.mp3", volume=0.10)
                self.audio.speak(
                    "Welcome to Speak with AI! Look at the picture and the hint, then press START MIC and say the word clearly. Let's do this!"
                )
            except Exception as e:
                print(f"SpeakWithAIScreen background music failed: {e}")

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

    def make_blur_background(self, target_surf):
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
        dark_overlay.fill((0, 0, 0, 80)) 
        self.blurred_bg_surface.blit(dark_overlay, (0, 0))

    def play_pre_recorded_audio(self):
        audio_path = self.current_question.get("audio")
        if audio_path and os.path.exists(audio_path):
            try:
                if self.audio:
                    self.audio.play_file(audio_path)
            except Exception as e:
                print(f"play_pre_recorded_audio failed: {e}")

    def next_question(self):
        if self.question_count >= self.MAX_QUESTIONS:
            self.game_over = True
            return
        self.question_count += 1
        self.current_question = self.ai.generate_question()
        self.hint_text = self.current_question.get("hint", "")
        self.status_text = "Click START MIC to record your voice! 🎙️"
        self.recognized_text = ""
        self.is_listening = False
        self.show_meme = False
        self.auto_audio_played = False 

        if self.audio:
            try:
                self.audio.play_music("assets/sounds/background.mp3", volume=0.10)
            except Exception as e:
                print(f"SpeakWithAIScreen background music restart failed: {e}")

        # Auto-play pre-recorded audio when question appears
        if not self.auto_audio_played:
            self.play_pre_recorded_audio()
            self.auto_audio_played = True

    def audio_callback(self, indata, frames, time, status):
        if self.is_listening:
            self.audio_queue.put(bytes(indata))

    def start_recording(self):
        if not self.speech_enabled:
            self.status_text = "Vosk/Sounddevice not set up properly."
            return
        
        if self.audio:
            try:
                self.audio.stop_music()
            except Exception as e:
                print(f"Failed to stop background music: {e}")
        
        self.audio_queue.queue.clear()
        self.recording_start_time = pygame.time.get_ticks()
        self.audio_stream = self._sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype='int16',
            channels=1, callback=self.audio_callback
        )
        self.audio_stream.start()

    def stop_and_analyze(self):
        self.is_listening = False
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None

        complete_data = b""
        while not self.audio_queue.empty():
            complete_data += self.audio_queue.get()

        text = ""
        if self.model and self.vosk_recognizer:
            self.vosk_recognizer.AcceptWaveform(complete_data)
            result_json = json.loads(self.vosk_recognizer.Result())
            text = result_json.get("text", "").strip().upper()
        
        if text == "[UNK]" or text == "":
            self.recognized_text = ""   
        else:
            self.recognized_text = text

        correct_word = self.current_question["correct_word"].upper()

        # Heuristic for kids pronunciation
        is_correct = (correct_word in text) and (text != "")
        if not is_correct and len(text) >= 3 and text != "[UNK]":
            if text[0] == correct_word[0] and text[-1] == correct_word[-1]:
                is_correct = True

        # Call adaptive AI logic to track success/failure
        result = self.ai.check_answer(correct_word if is_correct else "WRONG", correct_word)

        if is_correct:
            self.is_correct_answer = True
            self.status_text = "🎉 EXCELLENT! Correct Pronunciation! 🎉"
            
            # Spawn star particles
            for _ in range(25):
                particle = StarParticle(random.randint(300, 700), random.randint(150, 400))
                self.particles.append(particle)
            
            try:
                if self.audio:
                    self.audio.speak("Yes! Great job!")
            except Exception:
                pass

            # Build blurry background and show the result card (for correct answers only)
            self.make_blur_background(self.screen) 
            self.show_meme = True
            self.meme_display_start_time = pygame.time.get_ticks() 
        else:
            self.is_correct_answer = False
            self.status_text = f"Oops! It should be {correct_word}."
            self.shake_effect.trigger()
            try:
                if self.audio:
                    self.audio.speak(f"Try again. The word is {correct_word}")
            except Exception:
                pass
            self.show_meme = False
            self.is_listening = False
        
        if self.audio:
            try:
                self.audio.play_music("assets/sounds/background.mp3", volume=0.10)
            except Exception as e:
                print(f"Failed to resume background music: {e}")

    def draw_game_elements(self, target_surf):
        progress_rect = pygame.Rect(120, 30, 220, 60)
        pygame.draw.rect(target_surf, (116, 185, 255), progress_rect, border_radius=20)
        pygame.draw.rect(target_surf, (9, 132, 227), progress_rect, width=3, border_radius=20)
        progress_text = self.font.render(f"📋 {self.question_count}/{self.MAX_QUESTIONS}", True, self.TEXT_WHITE)
        target_surf.blit(progress_text, progress_text.get_rect(center=progress_rect.center))

        pygame.draw.rect(target_surf, (255, 107, 129), self.btn_back_rect, border_radius=15)
        back_text = self.font.render("↩️", True, self.TEXT_WHITE)
        target_surf.blit(back_text, back_text.get_rect(center=self.btn_back_rect.center))

        score_rect = pygame.Rect(740, 30, 220, 60)
        pygame.draw.rect(target_surf, (255, 234, 167), score_rect, border_radius=20)
        pygame.draw.rect(target_surf, (253, 203, 110), score_rect, width=3, border_radius=20)
        score_surface = self.font.render(f"⭐ Score: {self.ai.score}", True, (214, 142, 12))
        target_surf.blit(score_surface, score_surface.get_rect(center=score_rect.center))

        center_card = pygame.Rect(375, 115, 250, 250)
        pygame.draw.rect(target_surf, (45, 52, 54), center_card.move(0, 8), border_radius=30)
        pygame.draw.rect(target_surf, self.CARD_BG, center_card, border_radius=30)
        pygame.draw.rect(target_surf, (74, 144, 226), center_card, width=4, border_radius=30)
        
        img = self.load_image(self.current_question["image"], (210, 210))
        if img: 
            target_surf.blit(img, (395, 135))

        pygame.draw.rect(target_surf, (52, 152, 219), self.btn_speaker_rect, border_radius=50)
        spk_text = self.font.render("🔊", True, self.TEXT_WHITE)
        target_surf.blit(spk_text, spk_text.get_rect(center=self.btn_speaker_rect.center))

        # Display hint text with bounce effect
        if self.hint_text and not self.is_listening:
            self.hint_bounce_phase += self.hint_bounce_speed
            hint_y = 420 + math.sin(self.hint_bounce_phase) * self.hint_bounce_amplitude
            hint_surf = self.hint_font.render(self.hint_text, True, (231, 76, 60))
            hint_rect = hint_surf.get_rect(center=(self.screen_width // 2, int(hint_y)))
            pygame.draw.rect(target_surf, (255, 255, 255), hint_rect.inflate(30, 16), border_radius=20)
            pygame.draw.rect(target_surf, (231, 76, 60), hint_rect.inflate(30, 16), width=3, border_radius=20)
            target_surf.blit(hint_surf, hint_rect)
            status_y = hint_rect.bottom + 30
        else:
            status_y = 430

        status_surf = self.status_font.render(self.status_text, True, self.TEXT_DARK)
        target_surf.blit(status_surf, status_surf.get_rect(center=(self.screen_width // 2, status_y)))

        mic_color = (231, 76, 60) if self.is_listening else (46, 213, 115)
        pygame.draw.rect(target_surf, (45, 52, 54), self.btn_mic_rect.move(0, 5), border_radius=30)
        pygame.draw.rect(target_surf, mic_color, self.btn_mic_rect, border_radius=30)
        pygame.draw.rect(target_surf, self.TEXT_WHITE, self.btn_mic_rect, width=3, border_radius=30)
        
        if self.is_listening:
            elapsed = (pygame.time.get_ticks() - self.recording_start_time) // 1000
            remaining = max(0, self.MAX_RECORDING_SECONDS - elapsed)
            mic_label = f"STOP ({remaining}s) 🛑"
        else:
            mic_label = "START MIC 🎤"
            
        mic_text = self.font.render(mic_label, True, self.TEXT_WHITE)
        target_surf.blit(mic_text, mic_text.get_rect(center=self.btn_mic_rect.center))

    def draw(self):
        scene_surf = pygame.Surface((self.screen_width, self.screen_height))

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
                    self.next_question()
                else:
                    self.is_listening = False
                    self.status_text = "Click START MIC to try again! 🎙️"

        if self.show_meme and self.blurred_bg_surface:
            scene_surf.blit(self.blurred_bg_surface, (0, 0))
            
            meme_card = pygame.Rect(300, 90, 400, 420)
            pygame.draw.rect(scene_surf, (45, 52, 54), meme_card.move(0, 8), border_radius=30)
            pygame.draw.rect(scene_surf, self.CARD_BG, meme_card, border_radius=30)
            
            theme_color = (46, 213, 115) if self.is_correct_answer else (231, 76, 60)
            pygame.draw.rect(scene_surf, theme_color, meme_card, width=4, border_radius=30)

            title_str = "🎉 Brilliant! 🎉" if self.is_correct_answer else "Oops! Try Again! 🤔"
            m_title = self.font.render(title_str, True, theme_color)
            scene_surf.blit(m_title, m_title.get_rect(center=(self.screen_width // 2, 130)))

            # Fixed: correct meme path pointing to the existing assets
            meme_path = "assets/images/memes/happy.png" if self.is_correct_answer else "assets/images/memes/try_again.png"
            meme_img = self.load_image(meme_path, (220, 220))
            if meme_img:
                scene_surf.blit(meme_img, (390, 170))
            
            if self.recognized_text:
                said_text = f'You said: "{self.recognized_text}"'
            else:
                said_text = "We couldn't catch that. Try again! 🎙️"
                
            said_surf = self.status_font.render(said_text, True, self.TEXT_DARK)
            scene_surf.blit(said_surf, said_surf.get_rect(center=(self.screen_width // 2, 430)))

        elif not self.game_over:
            scene_surf.blit(self.bg_surface, (0, 0))
            self.draw_game_elements(scene_surf)
            if self.recognized_text and not self.is_listening:
                rec_surf = self.font.render(f'You said: "{self.recognized_text}"', True, (243, 156, 18))
                scene_surf.blit(rec_surf, rec_surf.get_rect(center=(self.screen_width // 2, 500)))
        else:
            # End screen
            scene_surf.blit(self.bg_surface, (0, 0))
            end_card = pygame.Rect(150, 100, 700, 450)
            pygame.draw.rect(scene_surf, (45, 52, 54), end_card.move(0, 10), border_radius=40)
            pygame.draw.rect(scene_surf, self.CARD_BG, end_card, border_radius=40)
            pygame.draw.rect(scene_surf, (74, 144, 226), end_card, width=6, border_radius=40)
            
            win_title = self.large_font.render("🎉 SPEAKING COMPLETED! 🎉", True, (74, 142, 226))
            scene_surf.blit(win_title, win_title.get_rect(center=(self.screen_width // 2, 180)))
            
            final_score_text = self.font.render(f"Amazing! You scored ⭐ {self.ai.score} Points!", True, self.TEXT_DARK)
            scene_surf.blit(final_score_text, final_score_text.get_rect(center=(self.screen_width // 2, 280)))

            # Restart button
            pygame.draw.rect(scene_surf, (45, 52, 54), self.btn_restart_rect.move(0, 5), border_radius=25)
            pygame.draw.rect(scene_surf, (0, 184, 148), self.btn_restart_rect, border_radius=25)
            pygame.draw.rect(scene_surf, self.TEXT_WHITE, self.btn_restart_rect, width=3, border_radius=25)
            res_txt = self.font.render("Play Again 🔄", True, self.TEXT_WHITE)
            scene_surf.blit(res_txt, res_txt.get_rect(center=self.btn_restart_rect.center))

            # Home button
            pygame.draw.rect(scene_surf, (45, 52, 54), self.btn_home_rect.move(0, 5), border_radius=25)
            pygame.draw.rect(scene_surf, (255, 159, 26), self.btn_home_rect, border_radius=25)
            pygame.draw.rect(scene_surf, self.TEXT_WHITE, self.btn_home_rect, width=3, border_radius=25)
            home_txt = self.font.render("Menu 🏠", True, self.TEXT_WHITE)
            scene_surf.blit(home_txt, home_txt.get_rect(center=self.btn_home_rect.center))

        # Update and draw star particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()
            p.draw(scene_surf)

        # Draw screen buffers with screen shake offset
        self.shake_effect.update()
        self.screen.blit(scene_surf, (self.shake_effect.offset_x, self.shake_effect.offset_y))
        pygame.display.flip()

    def handle_click(self, mouse_pos):
        if self.show_meme:
            return

        if not self.game_over:
            if self.btn_back_rect.collidepoint(mouse_pos):
                if self.ai.game_mode:
                    self.ai.update_stats(self.ai.game_mode, self.ai.correct_count, self.ai.incorrect_count, self.ai.score)
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
                if self.ai.game_mode:
                    self.ai.update_stats(self.ai.game_mode, self.ai.correct_count, self.ai.incorrect_count, self.ai.score)
                self.ai.reset_progress()
                self.question_count = 0
                self.game_over = False
                self.next_question()
            elif self.btn_home_rect.collidepoint(mouse_pos):
                if self.ai.game_mode:
                    self.ai.update_stats(self.ai.game_mode, self.ai.correct_count, self.ai.incorrect_count, self.ai.score)
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "GO_HOME"}))

    def handle_release(self, mouse_pos):
        self.pressed_back_btn = False
        self.pressed_mic_btn = False
        self.pressed_speaker_btn = False
        self.pressed_end_btn = None
