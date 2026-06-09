import pygame
import sys
import os
import random

class GameplayScreen:
    def __init__(self, screen, ai_engine):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.ai = ai_engine

        self.COLOR_BG_TOP = (255, 110, 196)        
        self.COLOR_BG_BOTTOM = (120, 255, 230)   
        self.CARD_BG = (255, 255, 255)            
        self.TEXT_WHITE = (255, 255, 255)
        self.TEXT_DARK = (44, 62, 80)             
        self.HINT_COLOR = (231, 76, 60)           

        self.btn_colors = [
            (255, 192, 72),    
            (46, 213, 115),    
            (255, 107, 129),  
            (84, 160, 255)     
        ]

        self.COLOR_SUCCESS = (46, 204, 113)      
        self.COLOR_FAIL = (231, 76, 60)          

        self.font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.large_font = pygame.font.SysFont("Segoe UI Emoji", 50)
        self.hint_font = pygame.font.SysFont("Segoe UI Emoji", 26)

        self.buttons = [
            pygame.Rect(140, 410, 320, 85),
            pygame.Rect(540, 410, 320, 85),
            pygame.Rect(140, 515, 320, 85),
            pygame.Rect(540, 515, 320, 85)
        ]
        
        self.btn_back_rect = pygame.Rect(40, 110, 80, 50)
        self.pressed_back_btn = False
        
        self.btn_restart_rect = pygame.Rect(240, 430, 240, 75)
        self.btn_home_rect = pygame.Rect(520, 430, 240, 75)

        self.pressed_button_index = None  
        self.pressed_end_btn = None       

        self.loaded_images = {}
        self.draw_gradient_background()

        self.question_count = 0        
        self.MAX_QUESTIONS = 10        
        self.game_over = False         

        self.show_meme = False
        self.meme_image = None
        self.meme_type = None
        self.meme_scale = 0.0
        self.meme_start_time = 0
        
        self.shake_offset = 0
        self.shake_timer = 0
        self.confettis = []
        self.selected_button_index = None
        
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

    def create_confetti(self):
        self.confettis = []
        colors = [(255, 234, 0), (255, 0, 127), (0, 245, 148), (0, 180, 216), (191, 85, 236)]
        for _ in range(80):
            self.confettis.append({
                "x": random.randint(0, self.screen_width),
                "y": random.randint(-200, 0),
                "speed": random.randint(4, 9),
                "color": random.choice(colors),
                "size": random.randint(6, 12)
            })

    def next_question(self):
        if self.question_count >= self.MAX_QUESTIONS:
            return

        self.question_count += 1
        self.current_question = self.ai.generate_question()
        self.hint_text = None
        self.show_meme = False
        self.meme_type = None
        self.meme_scale = 0.0
        self.selected_button_index = None
        self.pressed_button_index = None
        self.pressed_end_btn = None
        self.pressed_back_btn = False
        self.shake_offset = 0

    def draw(self):
        self.screen.blit(self.bg_surface, (0, 0))

        if not self.game_over:
            progress_rect = pygame.Rect(40, 30, 220, 60)
            pygame.draw.rect(self.screen, (116, 185, 255), progress_rect, border_radius=20)
            pygame.draw.rect(self.screen, (9, 132, 227), progress_rect, width=3, border_radius=20)
            progress_text = self.font.render(f"📋 {self.question_count}/{self.MAX_QUESTIONS}", True, self.TEXT_WHITE)
            self.screen.blit(progress_text, progress_text.get_rect(center=progress_rect.center))

            back_rect = self.btn_back_rect.copy()
            if self.pressed_back_btn:
                back_rect.y += 4
                pygame.draw.rect(self.screen, (231, 76, 60), back_rect, border_radius=15)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), back_rect.move(0, 4), border_radius=15)
                pygame.draw.rect(self.screen, (255, 107, 129), back_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.TEXT_WHITE, back_rect, width=2, border_radius=15)
            back_text = self.font.render("↩️", True, self.TEXT_WHITE)
            self.screen.blit(back_text, back_text.get_rect(center=back_rect.center))

            score_rect = pygame.Rect(740, 30, 220, 60)
            pygame.draw.rect(self.screen, (255, 234, 167), score_rect, border_radius=20)
            pygame.draw.rect(self.screen, (253, 203, 110), score_rect, width=3, border_radius=20)
            score_surface = self.font.render(f"⭐ Score: {self.ai.score}", True, (214, 142, 12))
            self.screen.blit(score_surface, score_surface.get_rect(center=score_rect.center))

            center_card = pygame.Rect(375, 75, 260, 260)
            pygame.draw.rect(self.screen, (45, 52, 54), center_card.move(0, 8), border_radius=40) 
            pygame.draw.rect(self.screen, self.CARD_BG, center_card, border_radius=40)
            pygame.draw.rect(self.screen, (9, 132, 227), center_card, width=5, border_radius=40) 

            image_path = self.current_question["image"]
            current_img = self.load_image(image_path, (210, 210))
            if current_img:
                self.screen.blit(current_img, (400, 100))

            if self.hint_text and not self.show_meme:
                hint_surface = self.hint_surface = self.hint_font.render(self.hint_text, True, self.HINT_COLOR)
                self.screen.blit(hint_surface, hint_surface.get_rect(center=(self.screen_width // 2, 365)))

            if self.shake_timer > 0:
                self.shake_timer -= 1
                self.shake_offset = int(random.choice([-12, 12, -8, 8, 0]))
                if self.shake_timer == 0: self.shake_offset = 0

            for i, rect in enumerate(self.buttons):
                current_rect = rect.copy()
                if self.selected_button_index == i and self.meme_type == "try_again":
                    current_rect.x += self.shake_offset

                current_btn_color = self.btn_colors[i]
                if self.selected_button_index == i:
                    current_btn_color = self.COLOR_SUCCESS if self.meme_type == "happy" else self.COLOR_FAIL

                if self.pressed_button_index == i and not self.show_meme:
                    current_rect.y += 5
                    pygame.draw.rect(self.screen, current_btn_color, current_rect, border_radius=25)
                else:
                    pygame.draw.rect(self.screen, (45, 52, 54), current_rect.move(0, 5), border_radius=25)
                    pygame.draw.rect(self.screen, current_btn_color, current_rect, border_radius=25)
                
                pygame.draw.rect(self.screen, self.TEXT_WHITE, current_rect, width=3, border_radius=25) 
                
                option_text = self.current_question["options"][i]
                text_surface = self.font.render(option_text, True, self.TEXT_WHITE)
                self.screen.blit(text_surface, text_surface.get_rect(center=current_rect.center))

            if self.show_meme and self.meme_type == "happy":
                for confetti in self.confettis:
                    confetti["y"] += confetti["speed"]
                    pygame.draw.circle(self.screen, confetti["color"], (confetti["x"], confetti["y"]), confetti["size"])

            if self.show_meme and self.meme_image:
                if self.meme_scale < 1.0: self.meme_scale += 0.09
                w, h = int(360 * self.meme_scale), int(360 * self.meme_scale)
                if w > 0 and h > 0:
                    scaled_meme = pygame.transform.scale(self.meme_image, (w, h))
                    meme_rect = scaled_meme.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    
                    overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 80))
                    self.screen.blit(overlay, (0, 0))
                    self.screen.blit(scaled_meme, meme_rect)

                if pygame.time.get_ticks() - self.meme_start_time > 1500:
                    self.show_meme = False  
                    if self.question_count >= self.MAX_QUESTIONS:
                        self.game_over = True
                    else:
                        if self.meme_type == "happy":
                            self.next_question()
                        else:
                            self.selected_button_index = None

        else:
            end_card = pygame.Rect(150, 100, 700, 450)
            pygame.draw.rect(self.screen, (45, 52, 54), end_card.move(0, 10), border_radius=40) 
            pygame.draw.rect(self.screen, self.CARD_BG, end_card, border_radius=40)
            pygame.draw.rect(self.screen, (255, 154, 158), end_card, width=6, border_radius=40)

            win_title = self.large_font.render("🎉 GREAT JOB! 🎉", True, (255, 107, 129))
            self.screen.blit(win_title, win_title.get_rect(center=(self.screen_width // 2, 180)))

            final_score_text = self.font.render(f"You collected ⭐ {self.ai.score} Points!", True, self.TEXT_DARK)
            self.screen.blit(final_score_text, final_score_text.get_rect(center=(self.screen_width // 2, 280)))
            
            comment = "Super Superstar! 🌟" if self.ai.score >= 80 else "You are Awesome! ❤️"
            comment_text = self.font.render(comment, True, (46, 213, 115))
            self.screen.blit(comment_text, comment_text.get_rect(center=(self.screen_width // 2, 340)))

            r_rect = self.btn_restart_rect.copy()
            if self.pressed_end_btn == "restart":
                r_rect.y += 5
                pygame.draw.rect(self.screen, (0, 184, 148), r_rect, border_radius=25)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), r_rect.move(0, 5), border_radius=25)
                pygame.draw.rect(self.screen, (0, 184, 148), r_rect, border_radius=25)
            pygame.draw.rect(self.screen, self.TEXT_WHITE, r_rect, width=3, border_radius=25)
            res_txt = self.font.render("Play Again 🔄", True, self.TEXT_WHITE)
            self.screen.blit(res_txt, res_txt.get_rect(center=r_rect.center))

            h_rect = self.btn_home_rect.copy()
            if self.pressed_end_btn == "home":
                h_rect.y += 5
                pygame.draw.rect(self.screen, (255, 159, 26), h_rect, border_radius=25)
            else:
                pygame.draw.rect(self.screen, (45, 52, 54), h_rect.move(0, 5), border_radius=25)
                pygame.draw.rect(self.screen, (255, 159, 26), h_rect, border_radius=25)
            pygame.draw.rect(self.screen, self.TEXT_WHITE, h_rect, width=3, border_radius=25)
            home_txt = self.font.render("Menu 🏠", True, self.TEXT_WHITE)
            self.screen.blit(home_txt, home_txt.get_rect(center=h_rect.center))

        pygame.display.flip()

    def handle_click(self, mouse_pos):
        if not self.game_over:
            if self.show_meme:
                return
                
            if self.btn_back_rect.collidepoint(mouse_pos):
                self.pressed_back_btn = True
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "GO_HOME"}))
                return

            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(mouse_pos):
                    self.pressed_button_index = i
                    self.execute_answer_check(i)
                    break
        else:
            if self.btn_restart_rect.collidepoint(mouse_pos):
                self.ai.score = 0
                self.ai.mistake_tracker = {}
                self.question_count = 0
                self.game_over = False
                self.show_meme = False
                self.pressed_end_btn = None
                self.pressed_button_index = None
                self.selected_button_index = None
                self.next_question()
                
            elif self.btn_home_rect.collidepoint(mouse_pos):
                self.pressed_end_btn = None
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "GO_HOME"}))

    def handle_release(self, mouse_pos):
        self.pressed_button_index = None
        self.pressed_end_btn = None
        self.pressed_back_btn = False

    def execute_answer_check(self, button_index):
        self.selected_button_index = button_index
        clicked_answer = self.current_question["options"][button_index]
        correct_answer = self.current_question["correct_word"]
        result = self.ai.check_answer(clicked_answer, correct_answer)

        self.meme_type = result["meme_type"]
        
        if self.meme_type == "happy":
            self.meme_image = self.load_image("assets/images/memes/happy.png", (360, 360))
            if not self.meme_image:
                self.meme_image = self.load_image("assets/memes/happy.png", (360, 360))
            self.create_confetti()
        else:
            self.meme_image = self.load_image("assets/images/memes/try_again.png", (360, 360))
            if not self.meme_image:
                self.meme_image = self.load_image("assets/memes/try_again.png", (360, 360))
            self.shake_timer = 25
            if result["hint"]:
                self.hint_text = result["hint"]

        self.show_meme = True
        self.meme_scale = 0.0
        self.meme_start_time = pygame.time.get_ticks()


        #done till here