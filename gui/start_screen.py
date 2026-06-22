import pygame
import sys
import os
from gui.game_play import GameplayScreen
from ai_engine.effects import GlowEffect, AnimatedCounter, PulseEffect
try:
    from ai_engine.audio_manager import AudioManager
except Exception:
    AudioManager = None

class StartScreen:
    def __init__(self, screen, ai_engine):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.ai = ai_engine

        self.COLOR_BG_TOP = (120, 255, 230)      
        self.COLOR_BG_BOTTOM = (255, 110, 196)   
        self.TEXT_WHITE = (255, 255, 255)

        self.title_font = pygame.font.SysFont("Segoe UI Emoji", 55)
        self.font = pygame.font.SysFont("Segoe UI Emoji", 32)

        # Redesigned layout: buttons side by side at top, stats below
        self.btn_game1_rect = pygame.Rect(80, 280, 360, 100)  # Left button
        self.btn_game2_rect = pygame.Rect(560, 280, 360, 100)  # Right button
        self.btn_stats_rect = pygame.Rect(320, 420, 360, 100)  # Stats button centered below

        self.btn1_pressed = False
        self.btn2_pressed = False
        self.btn3_pressed = False

        self.btn_stats_back_rect = pygame.Rect(560, 550, 260, 80)
        self.btn_stats_refresh_rect = pygame.Rect(120, 550, 260, 80)
        self.btn_stats_back_pressed = False
        self.btn_stats_refresh_pressed = False
        self.stats_refresh_message = ""
        self.stats_refresh_message_timer = 0

        # Add glow effects for buttons
        self.glow_btn1 = GlowEffect(self.btn_game1_rect)
        self.glow_btn2 = GlowEffect(self.btn_game2_rect)
        self.glow_btn3 = GlowEffect(self.btn_stats_rect)
        self.glow_back = GlowEffect(self.btn_stats_back_rect)
        self.glow_refresh = GlowEffect(self.btn_stats_refresh_rect)
        
        # Animated counters for stats
        self.animated_card_correct = AnimatedCounter(0, 0)
        self.animated_card_incorrect = AnimatedCounter(0, 0)
        self.animated_card_score = AnimatedCounter(0, 0)
        self.animated_speak_correct = AnimatedCounter(0, 0)
        self.animated_speak_incorrect = AnimatedCounter(0, 0)
        self.animated_speak_score = AnimatedCounter(0, 0)

        self.state = "START"
        self.gameplay_screen = None
        
        self.draw_gradient_background()
        # initialize audio manager and play intro voice
        try:
            self.audio = AudioManager() if AudioManager else None
            if self.audio:
                self.audio.play_file("assets/sounds/intro.mp3")
        except Exception:
            self.audio = None

    def return_to_menu(self):
        """Called any time we navigate back to the main menu (back button, home button,
        or an error in a sub-screen). Makes sure no leftover audio/recording keeps running
        and that score/stats are reset so the next game starts clean."""
        screen = self.gameplay_screen
        if screen is not None:
            # Stop any background music / sound that might still be playing.
            try:
                if getattr(screen, "audio", None):
                    screen.audio.stop_music()
            except Exception as e:
                print("Error stopping audio on return_to_menu:", e)

            # If we were in the middle of recording (Speak with AI), stop the mic stream.
            try:
                audio_stream = getattr(screen, "audio_stream", None)
                if audio_stream is not None:
                    audio_stream.stop()
                    audio_stream.close()
                    screen.audio_stream = None
                if hasattr(screen, "is_listening"):
                    screen.is_listening = False
            except Exception as e:
                print("Error stopping mic recording on return_to_menu:", e)

        # Reset score/progress so a new game always starts from zero.
        try:
            self.ai.reset_progress()
        except Exception as e:
            print("Error resetting progress on return_to_menu:", e)

        self.state = "START"
        self.gameplay_screen = None

    def draw_stats_screen(self):
        try:
            self.ai.load_stats()
        except Exception as e:
            print("Error loading stats in draw_stats_screen:", e)

        self.screen.blit(self.bg_surface, (0, 0))

        title_surf = self.font.render("📊 Game Statistics 📊", True, (44, 62, 80))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen_width // 2, 50)))

        stat_font = pygame.font.SysFont("Segoe UI Emoji", 24)
        small_font = pygame.font.SysFont("Segoe UI Emoji", 22)

        # Card Game Stats
        card_card = pygame.Rect(50, 120, 420, 280)
        pygame.draw.rect(self.screen, (45, 52, 54), card_card.move(0, 5), border_radius=30)
        pygame.draw.rect(self.screen, (255, 192, 72), card_card, border_radius=30)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, card_card, width=3, border_radius=30)

        card_title = stat_font.render("🎮 Card Game", True, (44, 62, 80))
        self.screen.blit(card_title, card_title.get_rect(center=(card_card.centerx, 150)))

        card_stats = self.ai.stats.get("card_game", {})
        card_correct = card_stats.get("correct", 0)
        card_incorrect = card_stats.get("incorrect", 0)
        card_total = card_correct + card_incorrect
        card_score = card_stats.get("total_score", 0)
        card_accuracy = int((card_correct / card_total) * 100) if card_total > 0 else 0

        card_correct_surf = small_font.render(f"✅ Correct: {card_correct}", True, (0, 0, 0))
        self.screen.blit(card_correct_surf, card_correct_surf.get_rect(center=(card_card.centerx, 190)))

        card_incorrect_surf = small_font.render(f"❌ Incorrect: {card_incorrect}", True, (231, 76, 60))
        self.screen.blit(card_incorrect_surf, card_incorrect_surf.get_rect(center=(card_card.centerx, 225)))

        card_score_surf = small_font.render(f"⭐ Score: {card_score}", True, (214, 142, 12))
        self.screen.blit(card_score_surf, card_score_surf.get_rect(center=(card_card.centerx, 260)))

        card_accuracy_surf = small_font.render(f"🎯 Accuracy: {card_accuracy}%", True, (84, 160, 255))
        self.screen.blit(card_accuracy_surf, card_accuracy_surf.get_rect(center=(card_card.centerx, 295)))

        # Speak with AI Stats
        speak_card = pygame.Rect(530, 120, 420, 280)
        pygame.draw.rect(self.screen, (45, 52, 54), speak_card.move(0, 5), border_radius=30)
        pygame.draw.rect(self.screen, (46, 213, 115), speak_card, border_radius=30)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, speak_card, width=3, border_radius=30)

        speak_title = stat_font.render("🎤 Speak with AI", True, (44, 62, 80))
        self.screen.blit(speak_title, speak_title.get_rect(center=(speak_card.centerx, 150)))

        speak_stats = self.ai.stats.get("speak_with_ai", {})
        speak_correct = speak_stats.get("correct", 0)
        speak_incorrect = speak_stats.get("incorrect", 0)
        speak_total = speak_correct + speak_incorrect
        speak_score = speak_stats.get("total_score", 0)
        speak_accuracy = int((speak_correct / speak_total) * 100) if speak_total > 0 else 0

        speak_correct_surf = small_font.render(f"✅ Correct: {speak_correct}", True, (255, 255, 255))
        self.screen.blit(speak_correct_surf, speak_correct_surf.get_rect(center=(speak_card.centerx, 190)))

        speak_incorrect_surf = small_font.render(f"❌ Incorrect: {speak_incorrect}", True, (255, 255, 255))
        self.screen.blit(speak_incorrect_surf, speak_incorrect_surf.get_rect(center=(speak_card.centerx, 225)))

        speak_score_surf = small_font.render(f"⭐ Score: {speak_score}", True, (214, 142, 12))
        self.screen.blit(speak_score_surf, speak_score_surf.get_rect(center=(speak_card.centerx, 260)))

        speak_accuracy_surf = small_font.render(f"🎯 Accuracy: {speak_accuracy}%", True, (84, 160, 255))
        self.screen.blit(speak_accuracy_surf, speak_accuracy_surf.get_rect(center=(speak_card.centerx, 295)))

        b_refresh = self.btn_stats_refresh_rect.copy()
        if self.btn_stats_refresh_pressed:
            b_refresh.y += 5
            pygame.draw.rect(self.screen, (84, 160, 255), b_refresh, border_radius=25)
        else:
            pygame.draw.rect(self.screen, (45, 52, 54), b_refresh.move(0, 5), border_radius=25)
            pygame.draw.rect(self.screen, (84, 160, 255), b_refresh, border_radius=25)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, b_refresh, width=3, border_radius=25)
        refresh_txt = self.font.render("Refresh All Stats 🔄", True, self.TEXT_WHITE)
        self.screen.blit(refresh_txt, refresh_txt.get_rect(center=b_refresh.center))

        if self.stats_refresh_message_timer > 0:
            message_surf = self.font.render(self.stats_refresh_message, True, (255, 255, 255))
            self.screen.blit(message_surf, message_surf.get_rect(center=(self.screen_width // 2, 520)))
            self.stats_refresh_message_timer -= 1

        debug_text = f"Loaded: card {self.ai.stats.get('card_game', {}).get('correct', 0)}/{self.ai.stats.get('card_game', {}).get('incorrect', 0)} " \
                     f"speak {self.ai.stats.get('speak_with_ai', {}).get('correct', 0)}/{self.ai.stats.get('speak_with_ai', {}).get('incorrect', 0)}"
        debug_surf = pygame.font.SysFont('Segoe UI Emoji', 18).render(debug_text, True, (255, 255, 255))
        self.screen.blit(debug_surf, debug_surf.get_rect(center=(self.screen_width // 2, 545)))

        b_back = self.btn_stats_back_rect.copy()
        if self.btn_stats_back_pressed:
            b_back.y += 5
            pygame.draw.rect(self.screen, (255, 159, 26), b_back, border_radius=25)
        else:
            pygame.draw.rect(self.screen, (45, 52, 54), b_back.move(0, 5), border_radius=25)
            pygame.draw.rect(self.screen, (255, 159, 26), b_back, border_radius=25)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, b_back, width=3, border_radius=25)
        back_txt = self.font.render("Back to Menu 🏠", True, self.TEXT_WHITE)
        self.screen.blit(back_txt, back_txt.get_rect(center=b_back.center))

        pygame.display.flip()

    def draw_gradient_background(self):
        self.bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.COLOR_BG_TOP[0] * (1 - ratio) + self.COLOR_BG_BOTTOM[0] * ratio)
            g = int(self.COLOR_BG_TOP[1] * (1 - ratio) + self.COLOR_BG_BOTTOM[1] * ratio)
            b = int(self.COLOR_BG_TOP[2] * (1 - ratio) + self.COLOR_BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (self.screen_width, y))

    def draw(self):
        if self.state == "START":
            self.screen.blit(self.bg_surface, (0, 0))

            title_surf = self.title_font.render("✨ AI KIDDY LEARNER ✨", True, self.TEXT_WHITE)
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen_width // 2, 100)))

            b1 = self.btn_game1_rect.copy()
            if self.btn1_pressed:
                b1.y += 5
                pygame.draw.rect(self.screen, (255, 192, 72), b1, border_radius=30)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b1.move(0, 5), border_radius=30) 
                pygame.draw.rect(self.screen, (255, 192, 72), b1, border_radius=30) 
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b1, width=4, border_radius=30)
            
            txt1 = self.font.render("Play with Words 🎮", True, self.TEXT_WHITE)
            self.screen.blit(txt1, txt1.get_rect(center=b1.center))

            b2 = self.btn_game2_rect.copy()
            if self.btn2_pressed:
                b2.y += 5
                pygame.draw.rect(self.screen, (46, 213, 115), b2, border_radius=30)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b2.move(0, 5), border_radius=30) 
                pygame.draw.rect(self.screen, (46, 213, 115), b2, border_radius=30) 
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b2, width=4, border_radius=30)
            
            txt2 = self.font.render("Speak with AI 🎤", True, self.TEXT_WHITE)
            self.screen.blit(txt2, txt2.get_rect(center=b2.center))

            b3 = self.btn_stats_rect.copy()
            if self.btn3_pressed:
                b3.y += 5
                pygame.draw.rect(self.screen, (84, 160, 255), b3, border_radius=30)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b3.move(0, 5), border_radius=30)
                pygame.draw.rect(self.screen, (84, 160, 255), b3, border_radius=30)
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b3, width=4, border_radius=30)

            stats_font = pygame.font.SysFont("Segoe UI Emoji", 28)
            txt3 = stats_font.render("My Stats 📊", True, self.TEXT_WHITE)
            self.screen.blit(txt3, txt3.get_rect(center=b3.center))

            pygame.display.flip()
        elif self.state == "STATS":
            self.draw_stats_screen()
        elif (self.state == "WORDS" or self.state == "SPEAK") and self.gameplay_screen:
            try:
                self.gameplay_screen.draw()
            except Exception as e:
                print("Error drawing gameplay_screen:", e)
                self.gameplay_screen = None
                self.state = "START"

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.USEREVENT and hasattr(event, "action") and event.action == "GO_HOME":
                    self.return_to_menu()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.state == "START":
                        if self.btn_game1_rect.collidepoint(mouse_pos):
                            self.btn1_pressed = True
                        elif self.btn_game2_rect.collidepoint(mouse_pos):
                            self.btn2_pressed = True
                        elif self.btn_stats_rect.collidepoint(mouse_pos):
                            self.btn3_pressed = True
                    elif self.state == "STATS":
                        if self.btn_stats_refresh_rect.collidepoint(mouse_pos):
                            self.btn_stats_refresh_pressed = True
                        elif self.btn_stats_back_rect.collidepoint(mouse_pos):
                            self.btn_stats_back_pressed = True
                    elif self.state in ["WORDS", "SPEAK"]:
                        try:
                            self.gameplay_screen.handle_click(mouse_pos)
                        except Exception as e:
                            print("Error in gameplay_screen.handle_click:", e)
                            self.gameplay_screen = None
                            self.state = "START"

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = event.pos
                    if self.state == "START":
                        if self.btn1_pressed:
                            self.btn1_pressed = False
                            try:
                                self.ai.game_mode = "card_game"
                                self.gameplay_screen = GameplayScreen(self.screen, self.ai)
                                self.state = "WORDS"
                            except Exception as e:
                                print("Unable to start GameplayScreen:", e)
                                self.gameplay_screen = None
                                self.state = "START"
                        elif self.btn2_pressed:
                            self.btn2_pressed = False
                            try:
                                self.ai.game_mode = "speak_with_ai"
                                from gui.speak_with_ai import SpeakWithAIScreen
                                self.gameplay_screen = SpeakWithAIScreen(self.screen, self.ai)
                                self.state = "SPEAK"
                            except Exception as e:
                                print("Unable to start SpeakWithAIScreen:", e)
                                self.gameplay_screen = None
                                self.state = "START"
                        elif self.btn3_pressed:
                            self.btn3_pressed = False
                            try:
                                self.ai.load_stats()
                                self.stats_refresh_message = "Stats loaded"
                                self.stats_refresh_message_timer = 90
                                print("Stats loaded on open:", self.ai.stats)
                            except Exception as e:
                                self.stats_refresh_message = "Load failed"
                                self.stats_refresh_message_timer = 90
                                print("Error loading stats on open:", e)
                            self.state = "STATS"
                    elif self.state == "STATS":
                        if self.btn_stats_refresh_pressed:
                            self.btn_stats_refresh_pressed = False
                            try:
                                self.ai.load_stats()
                                self.stats_refresh_message = "All stats refreshed!"
                                self.stats_refresh_message_timer = 90
                                print("Stats refreshed from file", self.ai.stats)
                            except Exception as e:
                                self.stats_refresh_message = "Refresh failed"
                                self.stats_refresh_message_timer = 90
                                print("Error refreshing stats:", e)
                        elif self.btn_stats_back_pressed:
                            self.btn_stats_back_pressed = False
                            self.state = "START"
                    elif self.state in ["WORDS", "SPEAK"]:
                        try:
                            self.gameplay_screen.handle_release(mouse_pos)
                        except Exception as e:
                            print("Error in gameplay_screen.handle_release:", e)
                            self.gameplay_screen = None
                            self.state = "START"
            if running:
                try:
                    self.draw()
                except Exception as e:
                    print("Error drawing StartScreen:", e)
                    self.gameplay_screen = None
                    self.state = "START"
                    # continue running to allow recovery from errors
                    continue
