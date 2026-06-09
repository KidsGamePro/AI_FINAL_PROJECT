import pygame
import sys
import os
from gui.game_play import GameplayScreen

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

        self.btn_game1_rect = pygame.Rect(140, 420, 320, 90)  
        self.btn_game2_rect = pygame.Rect(540, 420, 320, 90)  

        self.btn1_pressed = False
        self.btn2_pressed = False

        self.state = "START"
        self.gameplay_screen = None
        
        self.draw_gradient_background()

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
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.screen_width // 2, 180)))

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

            pygame.display.flip()
        elif (self.state == "WORDS" or self.state == "SPEAK") and self.gameplay_screen:
            self.gameplay_screen.draw()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.USEREVENT and hasattr(event, "action") and event.action == "GO_HOME":
                    self.state = "START"
                    self.gameplay_screen = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.state == "START":
                        if self.btn_game1_rect.collidepoint(mouse_pos):
                            self.btn1_pressed = True
                        elif self.btn_game2_rect.collidepoint(mouse_pos):
                            self.btn2_pressed = True
                    elif self.state in ["WORDS", "SPEAK"]:
                        self.gameplay_screen.handle_click(mouse_pos)

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = event.pos
                    if self.state == "START":
                        if self.btn1_pressed:
                            self.btn1_pressed = False
                            self.gameplay_screen = GameplayScreen(self.screen, self.ai)
                            self.state = "WORDS"
                        if self.btn2_pressed:
                            self.btn2_pressed = False
                            try:
                                from gui.speak_with_ai import SpeakWithAIScreen
                                self.gameplay_screen = SpeakWithAIScreen(self.screen, self.ai)
                                self.state = "SPEAK"
                            except Exception as e:
                                print("Unable to start SpeakWithAIScreen:", e)
                                self.gameplay_screen = None
                                self.state = "START"
                    elif self.state in ["WORDS", "SPEAK"]:
                        self.gameplay_screen.handle_release(mouse_pos)
            if running:
                self.draw()