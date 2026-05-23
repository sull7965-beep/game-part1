import pygame
import sys
import random

# --- HEAL ITEM ------
class HealItem:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.size = (25, 25)

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.size[0], self.size[1])

    def draw(self, surface):
        # warna hijau (heal)
        pygame.draw.rect(surface, (0, 255, 0), (*self.position, *self.size))

    
# --- 1. Struktur Tree (Node) ---
class GameNode:
    def __init__(self, x, y, color, width, height, health=100, show_health=True, image=None):
        self.position = pygame.Vector2(x, y)
        self.color = color
        self.size = (width, height)
        self.image = image
        self.angle = 0
        self.children = []
        self.max_health = health
        self.health = health
        self.hit_timer = 0
        self.show_health = show_health
        self.stun_timer = 0

    def draw_health_bar(self, surface, parent_pos):
        abs_pos = parent_pos + self.position
        
        bar_width = self.size[0]
        bar_height = 5

        health_ratio = 0 if self.max_health == 0 else max(0, self.health / self.max_health)
        
        # background merah
        pygame.draw.rect(surface, (255, 0, 0),
             (abs_pos.x, abs_pos.y - 10, bar_width, bar_height))
    
        # Health (hijau)
        pygame.draw.rect(surface, (0, 255, 0),
             (abs_pos.x, abs_pos.y - 10, bar_width * health_ratio, bar_height))

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_rect(self, parent_pos):
        abs_pos = parent_pos + self.position
        # Perbaikan bug ukuran Rect dari kode sebelumnya
        return pygame.Rect(abs_pos.x, abs_pos.y, self.size[0], self.size[1])

    def draw(self, surface, parent_pos):
        abs_pos = parent_pos + self.position

        if self.image:
            obj_surface = pygame.transform.scale(self.image, self.size)
        else:
            obj_surface = pygame.Surface(self.size, pygame.SRCALPHA)
            
            if self.stun_timer > 0:
                obj_surface.fill((100, 100, 255))  # biru saat stun
            else:
                obj_surface.fill(self.color)
        
        rotated_surface = pygame.transform.rotate(obj_surface, self.angle)
        new_rect = rotated_surface.get_rect(center=(abs_pos.x + self.size[0]/2, abs_pos.y + self.size[1]/2))
        
        surface.blit(rotated_surface, new_rect.topleft)

        # TAMBAHAN: gambar health bar
        if self.show_health:
            self.draw_health_bar(surface, parent_pos)
        
        for child in self.children:
            child.draw(surface, abs_pos)

# --- 2. Inisialisasi Game ---
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("musik.ogg")
pygame.mixer.music.set_volume(0.8)   # volume 0.0 - 1.0
pygame.mixer.music.play(-1)   


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SQUARE SURVIVOR")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Arial", 60, bold=True)
font_menu = pygame.font.SysFont("Arial", 36, bold=True)
font_text = pygame.font.SysFont("Arial", 24)
font_gameover = pygame.font.SysFont("Arial", 72, bold=True)

game_state = "MENU"

# --- 3. Pengaturan Objek ---
player = GameNode(400, 300, (0, 255, 0), 50, 50, health=50)
# Default awal pedang berada di sebelah kanan
pedang_image = pygame.image.load("pedang.png").convert_alpha()
pedang_image = pygame.transform.scale(pedang_image, (80, 30))
pedang = GameNode(50, 20, None, 80, 30, show_health=False, image = pedang_image)
player.add_child(pedang)


enemies = []
heal_items = []
def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':    pos = (random.randint(0, WIDTH), -50)
    elif side == 'bottom': pos = (random.randint(0, WIDTH), HEIGHT + 50)
    elif side == 'left':   pos = (-50, random.randint(0, HEIGHT))
    else:                pos = (WIDTH + 50, random.randint(0, HEIGHT))
    
    health = random.choice([50, 75])  #membuat agar health musuh bervariasi atau ada 2 pilihan
    enemies.append(GameNode(pos[0], pos[1], (255, 165, 0), 40, 40, health=health))  

for _ in range(3):
    spawn_enemy()

MAX_HEAL_ITEMS = 3 #heal item munculmax 3

def spawn_heal():   #memunculkan heal item

    if len(heal_items) >= MAX_HEAL_ITEMS:
        return

    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)

    heal_items.append(HealItem(x, y))

running = True
is_game_over = False
score = 0



while running: 
    screen.fill((30, 30, 30))
    mouse_pos = pygame.mouse.get_pos()
    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # ==================== STATUS 1: HALAMAN MENU UTAMA ====================
    if game_state == "MENU":
        title_text = font_title.render("SQUARE SURVIVOR", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        btn_start_rect = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
        start_color = (0, 200, 0) if btn_start_rect.collidepoint(mouse_pos) else (0, 150, 0)
        pygame.draw.rect(screen, start_color, btn_start_rect, border_radius=10)
        
        start_text = font_menu.render("START GAME", True, (255, 255, 255))
        screen.blit(start_text, (btn_start_rect.centerx - start_text.get_width() // 2, btn_start_rect.centery - start_text.get_height() // 2))

        btn_tuto_rect = pygame.Rect(WIDTH // 2 - 150, 330, 300, 50)
        tuto_color = (200, 150, 0) if btn_tuto_rect.collidepoint(mouse_pos) else (150, 100, 0)
        pygame.draw.rect(screen, tuto_color, btn_tuto_rect, border_radius=10)
        
        tuto_text = font_menu.render("TUTORIAL", True, (255, 255, 255))
        screen.blit(tuto_text, (btn_tuto_rect.centerx - tuto_text.get_width() // 2, btn_tuto_rect.centery - tuto_text.get_height() // 2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_start_rect.collidepoint(mouse_pos):
                    game_state = "GAMEPLAY"
                elif btn_tuto_rect.collidepoint(mouse_pos):
                    game_state = "TUTORIAL"

    # ==================== STATUS 2: HALAMAN TUTORIAL ====================
    elif game_state == "TUTORIAL":
        tuto_title = font_title.render("CARA BERMAIN", True, (255, 255, 255))
        screen.blit(tuto_title, (WIDTH // 2 - tuto_title.get_width() // 2, 80))
        
        lines = [
            "1. Gunakan TOMBOL PANAH untuk bergerak (Kotak Hijau).",
            "2. Objek biru ialah pedang.",
            "3. Objek orange adalah musuh"
        ]
        
        for i, line in enumerate(lines):
            line_surface = font_text.render(line, True, (200, 200, 200))
            screen.blit(line_surface, (100, 220 + (i * 40)))
            
        btn_back_rect = pygame.Rect(WIDTH // 2 - 150, 450, 300, 50)
        back_color = (200, 50, 50) if btn_back_rect.collidepoint(mouse_pos) else (150, 30, 30)
        pygame.draw.rect(screen, back_color, btn_back_rect, border_radius=10)
        
        back_text = font_menu.render("KEMBALI", True, (255, 255, 255))
        screen.blit(back_text, (btn_back_rect.centerx - back_text.get_width() // 2, btn_back_rect.centery - back_text.get_height() // 2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back_rect.collidepoint(mouse_pos):
                    game_state = "MENU"

    # ==================== STATUS 3: HALAMAN GAMEPLAY ====================
    elif game_state == "GAMEPLAY":
        if not is_game_over:

            if player.hit_timer > 0:
                player.hit_timer -= 1

            keys = pygame.key.get_pressed()
            move_speed = 5
            
            # --- BARU: LOGIKA GERAKAN DAN UBAH ARAH PEDANG ---
            if keys[pygame.K_LEFT]:
                player.position.x -= move_speed
                pedang.position = pygame.Vector2(-60, 15)
                pedang.angle = 180
            elif keys[pygame.K_RIGHT]:
                player.position.x += move_speed
                pedang.position = pygame.Vector2(50, 15)
                pedang.angle = 0
            elif keys[pygame.K_UP]:
                player.position.y -= move_speed
                pedang.position = pygame.Vector2(15, -60)
                pedang.angle = 90
            elif keys[pygame.K_DOWN]:
                player.position.y += move_speed
                pedang.position = pygame.Vector2(15, 50)
                pedang.angle = -90
            

            # --- BARU: PEMBATASAN LAYAR DINAMIS (Mengikuti Ujung Pedang) ---
            # Cari posisi minimal dan maksimal ujung pedang yang valid
            min_x = max(0, -pedang.position.x)
            max_x = WIDTH - player.size[0] - max(0, pedang.position.x + pedang.size[0] - player.size[0])
            min_y = max(0, -pedang.position.y)
            max_y = HEIGHT - player.size[1] - max(0, pedang.position.y + pedang.size[1] - player.size[1])

            # Mengunci posisi player berdasarkan batasan dinamis di atas
            player.position.x = max(min_x, min(player.position.x, max_x))
            player.position.y = max(min_y, min(player.position.y, max_y))

            # Ambil Rect untuk tabrakan
            player_rect = player.get_rect(pygame.Vector2(0,0))
            sword_rect = pedang.get_rect(player.position)

            # === HEAL ITEM PICKUP ===
            for item in heal_items[:]:
                if player_rect.colliderect(item.get_rect()):
                    player.health = min(player.max_health, player.health + 20)
                    heal_items.remove(item)

            # Logika Musuh
            for enemy in enemies[:]:
                #----STUN SYSTEM----
                if enemy.stun_timer > 0:
                    enemy.stun_timer -= 1
                else:
                    # Gerakan normal hanya kalau tidak stun
                    direction = player.position - enemy.position
                    if direction.length() > 0:
                        enemy.position += direction.normalize() * 2

                enemy.position.x = max(0, min(enemy.position.x, WIDTH - enemy.size[0]))
                enemy.position.y = max(0, min(enemy.position.y, HEIGHT - enemy.size[1]))
                
                enemy_rect = enemy.get_rect(pygame.Vector2(0,0))

                if sword_rect.colliderect(enemy_rect):
                    # Kurangi darah
                    enemy.health -= 25   # biar 2–3 hit baru mati

                   # === KNOCKBACK ===
                    knockback_dir = (enemy.position - player.position)
                    if knockback_dir.length() > 0:
                        knockback_dir = knockback_dir.normalize()
                        enemy.position += knockback_dir * 70
                    
                    #----STUN----
                    enemy.stun_timer = 30 # 1 detik stunn

                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        spawn_enemy()
                        score += 10   # tambah skor tiap kill
                        if random.random() < 0.3:
                            spawn_heal()
                elif player_rect.colliderect(enemy_rect):

                    if player.hit_timer <= 0:
                        player.hit_timer = 30
                        player.health -= 5 

                      # === KNOCKBACK PLAYER ===
                        knockback_dir = (player.position - enemy.position)
                        if knockback_dir.length() > 0:
                            knockback_dir = knockback_dir.normalize()
                            player.position += knockback_dir * 40   # makin besar = makin jauh terpental

                        if player.health <= 0:
                           is_game_over = True
            # Render Objek
            player.draw(screen, pygame.Vector2(0, 0))
            for enemy in enemies:
                enemy.draw(screen, pygame.Vector2(0, 0))
            for item in heal_items:
                item.draw(screen)

            score_text = font_text.render(f"POINT: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
        
        else:
            pygame.mixer.music.stop()
            msg = font_gameover.render("MAMPUSS", True, (255, 0, 0))
            screen.blit(msg, (WIDTH//2 - 180, HEIGHT//2 - 40))
            final_score = font_menu.render(f"POINT: {score}", True, (255, 255, 255))
            screen.blit(final_score, (WIDTH//2 - 80, HEIGHT//2 + 40))
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

