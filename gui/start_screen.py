import pygame
import sys
import os
from gui.game_play import GameplayScreen
from ai_engine.effects import GlowEffect, AnimatedCounter

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

        # Layout: buttons side by side, stats below
        self.btn_game1_rect = pygame.Rect(80, 260, 380, 100)  # Left button
        self.btn_game2_rect = pygame.Rect(540, 260, 380, 100)  # Right button
        self.btn_stats_rect = pygame.Rect(310, 410, 380, 100)  # Stats button centered below

        self.btn1_pressed = False
        self.btn2_pressed = False
        self.btn3_pressed = False

        self.btn_stats_back_rect = pygame.Rect(560, 540, 260, 80)
        self.btn_stats_refresh_rect = pygame.Rect(180, 540, 260, 80)
        self.btn_stats_back_pressed = False
        self.btn_stats_refresh_pressed = False
        self.stats_refresh_message = ""
        self.stats_refresh_message_timer = 0

        # Glow effects
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
        
        try:
            self.audio = AudioManager() if AudioManager else None
            if self.audio:
                self.audio.play_file("assets/sounds/intro.mp3")
        except Exception:
            self.audio = None

    def return_to_menu(self):
        """Cleanly navigate back to the main menu, resetting state and stopping audio"""
        screen = self.gameplay_screen
        if screen is not None:
            try:
                if getattr(screen, "audio", None):
                    screen.audio.stop_music()
            except Exception as e:
                print("Error stopping audio:", e)

            try:
                audio_stream = getattr(screen, "audio_stream", None)
                if audio_stream is not None:
                    audio_stream.stop()
                    audio_stream.close()
                    screen.audio_stream = None
                if hasattr(screen, "is_listening"):
                    screen.is_listening = False
            except Exception as e:
                print("Error stopping mic recording:", e)

        try:
            self.ai.reset_progress()
        except Exception as e:
            print("Error resetting progress:", e)

        self.state = "START"
        self.gameplay_screen = None

    def draw_stats_screen(self):
        # Update hover and glow effects for stats screen buttons
        mouse_pos = pygame.mouse.get_pos()
        self.glow_back.set_hover(self.btn_stats_back_rect.collidepoint(mouse_pos))
        self.glow_refresh.set_hover(self.btn_stats_refresh_rect.collidepoint(mouse_pos))
        
        self.glow_back.update()
        self.glow_refresh.update()

        # Update anim counters
        self.animated_card_correct.update()
        self.animated_card_incorrect.update()
        self.animated_card_score.update()
        self.animated_speak_correct.update()
        self.animated_speak_incorrect.update()
        self.animated_speak_score.update()

        self.screen.blit(self.bg_surface, (0, 0))

        title_surf = self.font.render("📊 Game Statistics 📊", True, (44, 62, 80))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen_width // 2, 50)))

        stat_font = pygame.font.SysFont("Segoe UI Emoji", 26)
        small_font = pygame.font.SysFont("Segoe UI Emoji", 22)

        # Card Game Stats Card
        card_card = pygame.Rect(60, 110, 400, 300)
        pygame.draw.rect(self.screen, (45, 52, 54), card_card.move(0, 6), border_radius=30)
        pygame.draw.rect(self.screen, (255, 192, 72), card_card, border_radius=30)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, card_card, width=3, border_radius=30)

        card_title = stat_font.render("🎮 Card Game", True, (44, 62, 80))
        self.screen.blit(card_title, card_title.get_rect(center=(card_card.centerx, 150)))

        c_correct = self.animated_card_correct.get_value()
        c_incorrect = self.animated_card_incorrect.get_value()
        c_total = c_correct + c_incorrect
        c_score = self.animated_card_score.get_value()
        c_accuracy = int((c_correct / c_total) * 100) if c_total > 0 else 0

        c_correct_surf = small_font.render(f"✅ Correct: {c_correct}", True, (44, 62, 80))
        self.screen.blit(c_correct_surf, c_correct_surf.get_rect(center=(card_card.centerx, 200)))

        c_incorrect_surf = small_font.render(f"❌ Incorrect: {c_incorrect}", True, (192, 57, 43))
        self.screen.blit(c_incorrect_surf, c_incorrect_surf.get_rect(center=(card_card.centerx, 240)))

        c_score_surf = small_font.render(f"⭐ Total Score: {c_score}", True, (44, 62, 80))
        self.screen.blit(c_score_surf, c_score_surf.get_rect(center=(card_card.centerx, 280)))

        c_accuracy_surf = small_font.render(f"🎯 Accuracy: {c_accuracy}%", True, (243, 156, 18))
        self.screen.blit(c_accuracy_surf, c_accuracy_surf.get_rect(center=(card_card.centerx, 320)))

        # Speak with AI Stats Card
        speak_card = pygame.Rect(540, 110, 400, 300)
        pygame.draw.rect(self.screen, (45, 52, 54), speak_card.move(0, 6), border_radius=30)
        pygame.draw.rect(self.screen, (46, 213, 115), speak_card, border_radius=30)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, speak_card, width=3, border_radius=30)

        speak_title = stat_font.render("🎤 Speak with AI", True, (255, 255, 255))
        self.screen.blit(speak_title, speak_title.get_rect(center=(speak_card.centerx, 150)))

        s_correct = self.animated_speak_correct.get_value()
        s_incorrect = self.animated_speak_incorrect.get_value()
        s_total = s_correct + s_incorrect
        s_score = self.animated_speak_score.get_value()
        s_accuracy = int((s_correct / s_total) * 100) if s_total > 0 else 0

        s_correct_surf = small_font.render(f"✅ Correct: {s_correct}", True, (255, 255, 255))
        self.screen.blit(s_correct_surf, s_correct_surf.get_rect(center=(speak_card.centerx, 200)))

        s_incorrect_surf = small_font.render(f"❌ Incorrect: {s_incorrect}", True, (192, 57, 43))
        self.screen.blit(s_incorrect_surf, s_incorrect_surf.get_rect(center=(speak_card.centerx, 240)))

        s_score_surf = small_font.render(f"⭐ Total Score: {s_score}", True, (255, 255, 255))
        self.screen.blit(s_score_surf, s_score_surf.get_rect(center=(speak_card.centerx, 280)))

        s_accuracy_surf = small_font.render(f"🎯 Accuracy: {s_accuracy}%", True, (243, 156, 18))
        self.screen.blit(s_accuracy_surf, s_accuracy_surf.get_rect(center=(speak_card.centerx, 320)))

        # Refresh button glow and draw
        self.glow_refresh.draw(self.screen, (84, 160, 255))
        b_refresh = self.btn_stats_refresh_rect.copy()
        if self.btn_stats_refresh_pressed:
            b_refresh.y += 4
        else:
            pygame.draw.rect(self.screen, (45, 52, 54), b_refresh.move(0, 4), border_radius=25)
        pygame.draw.rect(self.screen, (84, 160, 255), b_refresh, border_radius=25)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, b_refresh, width=3, border_radius=25)
        refresh_txt = self.font.render("Reset Stats 🔄", True, self.TEXT_WHITE)
        self.screen.blit(refresh_txt, refresh_txt.get_rect(center=b_refresh.center))

        # Back button glow and draw
        self.glow_back.draw(self.screen, (255, 159, 26))
        b_back = self.btn_stats_back_rect.copy()
        if self.btn_stats_back_pressed:
            b_back.y += 4
        else:
            pygame.draw.rect(self.screen, (45, 52, 54), b_back.move(0, 4), border_radius=25)
        pygame.draw.rect(self.screen, (255, 159, 26), b_back, border_radius=25)
        pygame.draw.rect(self.screen, self.TEXT_WHITE, b_back, width=3, border_radius=25)
        back_txt = self.font.render("Menu 🏠", True, self.TEXT_WHITE)
        self.screen.blit(back_txt, back_txt.get_rect(center=b_back.center))

        if self.stats_refresh_message_timer > 0:
            message_surf = small_font.render(self.stats_refresh_message, True, (44, 62, 80))
            self.screen.blit(message_surf, message_surf.get_rect(center=(self.screen_width // 2, 450)))
            self.stats_refresh_message_timer -= 1

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
            # Update hover state
            mouse_pos = pygame.mouse.get_pos()
            self.glow_btn1.set_hover(self.btn_game1_rect.collidepoint(mouse_pos))
            self.glow_btn2.set_hover(self.btn_game2_rect.collidepoint(mouse_pos))
            self.glow_btn3.set_hover(self.btn_stats_rect.collidepoint(mouse_pos))
            
            self.glow_btn1.update()
            self.glow_btn2.update()
            self.glow_btn3.update()

            self.screen.blit(self.bg_surface, (0, 0))

            title_surf = self.title_font.render("✨ AI KIDDY LEARNER ✨", True, self.TEXT_WHITE)
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen_width // 2, 100)))

            # Button 1 (Card Game)
            self.glow_btn1.draw(self.screen, (255, 192, 72))
            b1 = self.btn_game1_rect.copy()
            if self.btn1_pressed:
                b1.y += 4
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b1.move(0, 4), border_radius=30) 
            pygame.draw.rect(self.screen, (255, 192, 72), b1, border_radius=30) 
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b1, width=3, border_radius=30)
            txt1 = self.font.render("Play with Words 🎮", True, self.TEXT_WHITE)
            self.screen.blit(txt1, txt1.get_rect(center=b1.center))

            # Button 2 (Speak with AI)
            self.glow_btn2.draw(self.screen, (46, 213, 115))
            b2 = self.btn_game2_rect.copy()
            if self.btn2_pressed:
                b2.y += 4
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b2.move(0, 4), border_radius=30) 
            pygame.draw.rect(self.screen, (46, 213, 115), b2, border_radius=30) 
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b2, width=3, border_radius=30)
            txt2 = self.font.render("Speak with AI 🎤", True, self.TEXT_WHITE)
            self.screen.blit(txt2, txt2.get_rect(center=b2.center))

            # Button 3 (Stats)
            self.glow_btn3.draw(self.screen, (84, 160, 255))
            b3 = self.btn_stats_rect.copy()
            if self.btn3_pressed:
                b3.y += 4
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), b3.move(0, 4), border_radius=30)
            pygame.draw.rect(self.screen, (84, 160, 255), b3, border_radius=30)
            pygame.draw.rect(self.screen, self.TEXT_WHITE, b3, width=3, border_radius=30)
            txt3 = self.font.render("My Stats 📊", True, self.TEXT_WHITE)
            self.screen.blit(txt3, txt3.get_rect(center=b3.center))

            pygame.display.flip()
        elif self.state == "STATS":
            self.draw_stats_screen()
        elif (self.state == "WORDS" or self.state == "SPEAK") and self.gameplay_screen:
            try:
                self.gameplay_screen.draw()
            except Exception as e:
                print("Error drawing gameplay_screen:", e)
                self.return_to_menu()

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
                            print("Error handling click:", e)
                            self.return_to_menu()

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
                                self.return_to_menu()
                        elif self.btn2_pressed:
                            self.btn2_pressed = False
                            try:
                                self.ai.game_mode = "speak_with_ai"
                                from gui.speak_with_ai import SpeakWithAIScreen
                                self.gameplay_screen = SpeakWithAIScreen(self.screen, self.ai)
                                self.state = "SPEAK"
                            except Exception as e:
                                print("Unable to start SpeakWithAIScreen:", e)
                                self.return_to_menu()
                        elif self.btn3_pressed:
                            self.btn3_pressed = False
                            try:
                                self.ai.load_stats()
                                card_stats = self.ai.stats.get("card_game", {})
                                speak_stats = self.ai.stats.get("speak_with_ai", {})
                                
                                # Reset animated counters to slide from 0
                                self.animated_card_correct.reset(0, card_stats.get("correct", 0))
                                self.animated_card_incorrect.reset(0, card_stats.get("incorrect", 0))
                                self.animated_card_score.reset(0, card_stats.get("total_score", 0))
                                self.animated_speak_correct.reset(0, speak_stats.get("correct", 0))
                                self.animated_speak_incorrect.reset(0, speak_stats.get("incorrect", 0))
                                self.animated_speak_score.reset(0, speak_stats.get("total_score", 0))
                                
                                self.stats_refresh_message = "Stats Loaded"
                                self.stats_refresh_message_timer = 60
                            except Exception as e:
                                self.stats_refresh_message = "Load Failed"
                                self.stats_refresh_message_timer = 60
                            self.state = "STATS"
                    elif self.state == "STATS":
                        if self.btn_stats_refresh_pressed:
                            self.btn_stats_refresh_pressed = False
                            try:
                                # Reset stats in file and memory
                                self.ai.stats = {
                                    "card_game": {"correct": 0, "incorrect": 0, "total_score": 0},
                                    "speak_with_ai": {"correct": 0, "incorrect": 0, "total_score": 0}
                                }
                                self.ai.save_stats()
                                self.animated_card_correct.reset(0, 0)
                                self.animated_card_incorrect.reset(0, 0)
                                self.animated_card_score.reset(0, 0)
                                self.animated_speak_correct.reset(0, 0)
                                self.animated_speak_incorrect.reset(0, 0)
                                self.animated_speak_score.reset(0, 0)
                                self.stats_refresh_message = "All statistics reset!"
                                self.stats_refresh_message_timer = 90
                            except Exception as e:
                                self.stats_refresh_message = "Reset Failed"
                                self.stats_refresh_message_timer = 90
                        elif self.btn_stats_back_pressed:
                            self.btn_stats_back_pressed = False
                            self.state = "START"
                    elif self.state in ["WORDS", "SPEAK"]:
                        try:
                            self.gameplay_screen.handle_release(mouse_pos)
                        except Exception as e:
                            print("Error handling release:", e)
                            self.return_to_menu()
            if running:
                try:
                    self.draw()
                except Exception as e:
                    print("Error drawing StartScreen:", e)
                    self.return_to_menu()
