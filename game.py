import pygame
import sys
import json
import random
import os

print(os.listdir())

# Initialize Pygame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JumpDash")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (160, 160, 160)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (214, 163, 85)

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_HIGHSCORES = 3
STATE_SETTINGS = 4
STATE_PAUSED = 5

# Game variables
current_state = STATE_MENU
score = 0
game_speed = 5
player_gravity = 0.5
jump_force = -15
obstacle_timer = 0

# Load scores and settings
try:
    with open('scores.json') as f:
        data = json.load(f)
        high_scores = data['high_scores']
        settings = data['settings']
except:
    high_scores = [0, 0, 0, 0, 0]
    settings = {'difficulty': 'medium', 'sound': True}

# Load music and sounds
# Load music and sounds
music_path = r"C:\Users\DELL\Desktop\code with ryan\finalassign\background_music.mp3"
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
else:
    print("Warning: 'background_music.mp3' not found. Background music will not play.")

#print("Warning: 'background_music.mp3' not found. Background music will not play.")

# Load sound effects
# Sound file paths
sound_dir = r"C:\Users\DELL\Desktop\code with ryan\finalassign"


jump_path = os.path.join(sound_dir, "jump.wav")
die_path = os.path.join(sound_dir, "die.wav")
point_path = os.path.join(sound_dir, "point.wav")

# Load sounds if they exist
jump_sound = pygame.mixer.Sound(jump_path) if os.path.exists(jump_path) else None
die_sound = pygame.mixer.Sound(die_path) if os.path.exists(die_path) else None
point_sound = pygame.mixer.Sound(point_path) if os.path.exists(point_path) else None

# Print warnings if any sound file is missing
if not jump_sound:
    print("Warning: 'jump.wav' not found. Jump sound will not play.")
if not die_sound:
    print("Warning: 'die.wav' not found. Die sound will not play.")
if not point_sound:
    print("Warning: 'point.wav' not found. Point sound will not play.")


class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = DARK_GRAY if is_hovered else GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        font = pygame.font.SysFont("arial", 30, bold=True)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class Background:
    def __init__(self):
        self.ground_y = HEIGHT - 50
        self.clouds = [[random.randint(0, WIDTH), random.randint(50, 200)] for _ in range(5)]
        self.bg_x = 0

    def update(self, speed):
        self.bg_x = (self.bg_x - speed) % WIDTH
        for cloud in self.clouds:
            cloud[0] = (cloud[0] - speed//2) % (WIDTH + 200)
            if cloud[0] < -100:
                cloud[0] = WIDTH + 100
                cloud[1] = random.randint(50, 200)

    def draw(self):
        screen.fill(SKY_BLUE)
        # Draw the background and ground
        pygame.draw.rect(screen, GROUND_COLOR, (0, self.ground_y, WIDTH, 50))
        for x, y in self.clouds:
            pygame.draw.ellipse(screen, (255, 255, 255, 200), (x, y, 100, 40))

            pygame.draw.ellipse(screen, (255, 255, 255, 200), (x + 20, y - 20, 60, 30))
        

        # Draw the background image
class Player:
    def __init__(self):
        # Load and scale frames
        sprite_path = os.path.join(os.path.dirname(__file__), "assets", "player_spritesheet.png")

        self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        self.frames = self.load_frames(self.sprite_sheet, 4, 1)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        # Set rect based on first frame and align with ground
        self.rect = self.frames[0].get_rect()
        self.rect.topleft = (100, HEIGHT - 50 - self.rect.height)

        self.y_vel = 0
        self.on_ground = True

    
    def load_frames(self, sheet, cols, rows):
        frame_width = sheet.get_width() // cols
        frame_height = sheet.get_height() // rows
        frames = [
        sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        for i in range(cols)]
    # Resize frames to better match your game's scale
        scaled_frames = [pygame.transform.scale(frame, (60, 80)) for frame in frames]
        return scaled_frames

    def draw(self):
        screen.blit(self.frames[int(self.current_frame)], (self.rect.x, self.rect.y +23))


    def jump(self):
        if self.on_ground:
            self.y_vel = jump_force
            self.on_ground = False
            if settings['sound'] and jump_sound:
                jump_sound.play()

    def update(self):
        self.y_vel += player_gravity
        self.rect.y += self.y_vel

        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.on_ground = True
            self.y_vel = 0

        # Update animation regardless of ground state but slower in air
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

class Obstacle:
    def __init__(self):
        self.type = random.choice([
            {"width": 30, "height": 60, "color": (100, 100, 100)},
            {"width": 50, "height": 30, "color": (150, 50, 50)}
        ])
        self.rect = pygame.Rect(
            WIDTH,
            HEIGHT - 50 - self.type["height"],
            self.type["width"],
            self.type["height"]
        )

    def update(self):
        self.rect.x -= game_speed
        return self.rect.right > 0

background = Background()
player = Player()
obstacles = []

def reset_game():
    global score, game_speed, obstacle_timer
    player.rect.y = HEIGHT - 150
    player.y_vel = 0
    obstacles.clear()
    score = 0
    game_speed = 5
    obstacle_timer = 0

def update_high_scores():
    global high_scores
    high_scores.append(score)
    high_scores = sorted(list(set(high_scores)), reverse=True)[:5]
    with open('scores.json', 'w') as f:
        json.dump({"high_scores": high_scores, "settings": settings}, f)

def draw_menu():
    title_font = pygame.font.SysFont("comicsansms", 72, bold=True)
    title = title_font.render("JumpDash", True, (50, 50, 50))
    shadow = title_font.render("JumpDash", True, (180, 180, 180))
    screen.blit(shadow, (WIDTH/2 - title.get_width()/2 + 4, HEIGHT/4 + 4))
    screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/4))
    buttons = [
        Button("Start Game", WIDTH/2 - 100, HEIGHT/2, 200, 50, STATE_PLAYING),
        Button("High Scores", WIDTH/2 - 100, HEIGHT/2 + 70, 200, 50, STATE_HIGHSCORES),
        Button("Settings", WIDTH/2 - 100, HEIGHT/2 + 140, 200, 50, STATE_SETTINGS)
    ]
    for button in buttons:
        button.draw()
    return buttons

def draw_highscores():
    font = pygame.font.SysFont("arial", 60, bold=True)
    title = font.render("High Scores", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    y_offset = 140
    for i, hs in enumerate(high_scores):
        score_text = f"{i+1}. {hs}"
        text = pygame.font.SysFont("arial", 40).render(score_text, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 50
    back_button = Button("Back", WIDTH // 2 - 100, HEIGHT - 100, 200, 50, STATE_MENU)
    back_button.draw()
    return [back_button]

def draw_settings():
    font = pygame.font.SysFont("arial", 60, bold=True)
    title = font.render("Settings", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    sound_text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
    difficulty_text = f"Difficulty: {settings['difficulty'].capitalize()}"
    sound_button = Button(sound_text, WIDTH // 2 - 120, 200, 240, 50, 'toggle_sound')
    difficulty_button = Button(difficulty_text, WIDTH // 2 - 120, 280, 240, 50, 'toggle_difficulty')
    back_button = Button("Back", WIDTH // 2 - 100, HEIGHT - 100, 200, 50, STATE_MENU)
    for btn in [sound_button, difficulty_button, back_button]:
        btn.draw()
    return [sound_button, difficulty_button, back_button]

def draw_game():
    background.draw()
    player.draw()
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle.type["color"], obstacle.rect)
    font = pygame.font.SysFont("arial", 36, bold=True)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

def draw_game_over():
    font = pygame.font.SysFont("arial", 72, bold=True)
    text = font.render("Game Over!", True, RED)
    screen.blit(text, text.get_rect(center=(WIDTH/2, HEIGHT/3)))
    font = pygame.font.SysFont("arial", 36)
    score_text = font.render(f"Final Score: {score}", True, BLACK)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH/2, HEIGHT/2)))
    buttons = [
        Button("Play Again", WIDTH/2 - 100, HEIGHT - 180, 200, 50, STATE_PLAYING),
        Button("Main Menu", WIDTH/2 - 100, HEIGHT - 110, 200, 50, STATE_MENU)
    ]
    for button in buttons:
        button.draw()
    return buttons

def draw_paused():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    font = pygame.font.SysFont("arial", 60, bold=True)
    text = font.render("Paused", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    buttons = []
    if current_state == STATE_MENU:
        buttons = draw_menu()
    elif current_state == STATE_PLAYING:
        draw_game()
    elif current_state == STATE_GAME_OVER:
        buttons = draw_game_over()
    elif current_state == STATE_HIGHSCORES:
        buttons = draw_highscores()
    elif current_state == STATE_SETTINGS:
        buttons = draw_settings()
    elif current_state == STATE_PAUSED:
        draw_game()
        draw_paused()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_state == STATE_PLAYING:
                player.jump()
            if event.key == pygame.K_p:
                if current_state == STATE_PLAYING:
                    current_state = STATE_PAUSED
                elif current_state == STATE_PAUSED:
                    current_state = STATE_PLAYING

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button.rect.collidepoint(event.pos):
                    if button.action == STATE_PLAYING:
                        reset_game()
                    if button.action == 'toggle_sound':
                        settings['sound'] = not settings['sound']
                        if settings['sound']:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    elif button.action == 'toggle_difficulty':
                        difficulties = ['easy', 'medium', 'hard']
                        current = difficulties.index(settings['difficulty'])
                        settings['difficulty'] = difficulties[(current + 1) % len(difficulties)]
                    elif isinstance(button.action, int):
                        current_state = button.action

    if current_state == STATE_PLAYING:
        background.update(game_speed)
        player.update()
        obstacle_timer += 1
        if obstacle_timer > 60 - (game_speed * 2):
            obstacles.append(Obstacle())
            obstacle_timer = 0
        obstacles = [obs for obs in obstacles if obs.update()]
        for obs in obstacles:
            if player.rect.colliderect(obs.rect):
                if settings['sound'] and die_sound:
                    die_sound.play()
                update_high_scores()
                current_state = STATE_GAME_OVER
        score += 1
        if score % 500 == 0:
            game_speed = min(game_speed + 0.5, 10)

        if score % 100 == 0 and settings['sound'] and point_sound:
            point_sound.play()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()