# 编写程序，判断今天是否为周末
"""
a = 5
b = [1,2,3,4]
print(a in b) # False
"""

'''
a = "lydia"
b = "i'm lydia"
print(a in b) # True
'''
"""
a = input(f"请输入今天周几:")
b = ["周六","周天","6","7"]
c = a in b

if c == True:
    msg = "今天是周末"
else:
    msg = "今天不是周末"

print(msg)
"""
pip install pygame

import pygame
import random
import sys
import math

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("枪战游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.health = 100
        self.shoot_delay = 250  # 射击延迟（毫秒）
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.speed_x = 0
        self.speed_y = 0
        
        # 键盘控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -8
        if keys[pygame.K_RIGHT]:
            self.speed_x = 8
        if keys[pygame.K_UP]:
            self.speed_y = -8
        if keys[pygame.K_DOWN]:
            self.speed_y = 8
            
        # 边界检测
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
            
        self.rect.y += self.speed_y
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # 当敌人移出屏幕底部时重新放置到顶部
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 5)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # 当子弹移出屏幕顶部时删除
        if self.rect.bottom < 0:
            self.kill()

# 创建精灵组
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 创建玩家
player = Player()
all_sprites.add(player)

# 创建敌人
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 游戏时钟
clock = pygame.time.Clock()

# 分数
score = 0

# 游戏字体
font_name = pygame.font.match_font('simsun')  # 使用系统中的宋体

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health(surf, x, y, health):
    if health < 0:
        health = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (health / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# 游戏主循环
running = True
while running:
    # 保持30fps
    clock.tick(60)
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新精灵
    all_sprites.update()

    # 碰撞检测：子弹击中敌人
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # 碰撞检测：敌人击中玩家
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 25
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        if player.health <= 0:
            running = False

    # 绘制
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # 绘制分数
    draw_text(screen, f"分数: {score}", 18, WIDTH // 2, 10)
    
    # 绘制生命值
    draw_health(screen, 5, 5, player.health)
    
    # 更新屏幕
    pygame.display.flip()

# 游戏结束画面
screen.fill(BLACK)
draw_text(screen, "游戏结束", 64, WIDTH // 2, HEIGHT // 4)
draw_text(screen, f"最终分数: {score}", 22, WIDTH // 2, HEIGHT // 2)
draw_text(screen, "按任意键退出", 18, WIDTH // 2, HEIGHT * 3 // 4)
pygame.display.flip()

# 等待用户按键退出
waiting = True
while waiting:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = False
        if event.type == pygame.KEYUP:
            waiting = False

pygame.quit()
sys.exit()
