import pygame
import random
import json
import os

# Настройки игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Шрифты
pygame.font.init()
font = pygame.font.Font(None, 36)

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Загрузка звуковых эффектов
win_sound = pygame.mixer.Sound('win.wav')  # Звук выигрыша
lose_sound = pygame.mixer.Sound('lose.wav')  # Звук проигрыша
coin_sound = pygame.mixer.Sound('coin.wav')  # Звук сбора монеты
buy_sound = pygame.mixer.Sound('buy.wav')  # Звук покупки

# Загрузка изображений с проверкой ошибок
def load_image(image_path):
    try:
        return pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Не удалось загрузить изображение '{image_path}': {e}")
        return None

main_menu_bg = load_image('main_menu_bg.png')
game_bg = load_image('game_bg.png')

# Функция для рисования текста на экране
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

# Загрузка прогресса
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as file:
            progress = json.load(file)
            if 'skins' not in progress:
                progress['skins'] = []  # Инициализируем пустой список для скинов
            return progress
    return {"coins": 0, "best_scores": [], "skins": []}

# Сохранение прогресса
def save_progress(data):
    with open("progress.json", "w") as file:
        json.dump(data, file)

# Сброс прогресса
def reset_progress():
    default_progress = {"coins": 0, "best_scores": [], "skins": []}
    save_progress(default_progress)

# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, lives=3):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (50, 50))  # Масштабируем изображение
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = SCREEN_HEIGHT - 100
        self.jump_speed = -15
        self.gravity = 0.5
        self.velocity_y = 0
        self.on_ground = True
        self.lives = lives

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

    def fall(self):
        self.rect.y = SCREEN_HEIGHT - 50  # Опускаем игрока до пола
        self.on_ground = True
        self.velocity_y = 0

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        if self.rect.y >= SCREEN_HEIGHT - 50:
            self.rect.y = SCREEN_HEIGHT - 50
            self.on_ground = True
            self.velocity_y = 0
        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity_y = 0

# Класс для препятствий
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, color=None, shape='square'):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        if shape == 'triangle':
            pygame.draw.polygon(self.image, color, [(25, 0), (50, 50), (0, 50)])
        else:  # square
            self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3  # Устанавливаем скорость препятствий

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -50:
            self.kill()

# Класс для монет
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= 1  # Двигаем монеты с той же скоростью, что и препятствия
        if self.rect.x < -30:
            self.kill()

# Главное меню
def main_menu(progress):
    while True:
        screen.fill(WHITE)  # Очистка экрана перед отрисовкой
        if main_menu_bg is not None:
            screen.blit(main_menu_bg, (0, 0))  # Рисуем фон главного меню
        
        draw_text(screen, "Geometry Dash Clone", font, BLACK, SCREEN_WIDTH // 2 - 150, 50)
        draw_text(screen, "1: Start Game", font, BLACK, SCREEN_WIDTH // 2 - 100, 150)
        draw_text(screen, "2: View Best Scores", font, BLACK, SCREEN_WIDTH // 2 - 100, 200)
        draw_text(screen, "3: Shop", font, BLACK, SCREEN_WIDTH // 2 - 100, 250)
        draw_text(screen, "4: Quit", font, BLACK, SCREEN_WIDTH // 2 - 100, 300)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reset_progress()  # Сбрасываем прогресс перед выходом
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    level_selection(progress)  # Переход к выбору уровня
                if event.key == pygame.K_2:
                    view_best_scores(progress)
                if event.key == pygame.K_3:
                    shop(progress)
                if event.key == pygame.K_4:
                    reset_progress()  # Сбрасываем прогресс перед выходом
                    pygame.quit()
                    exit()

# Выбор уровня
def level_selection(progress):
    while True:
        screen.fill(WHITE)  # Очистка экрана перед отрисовкой
        draw_text(screen, "Select Difficulty Level", font, BLACK, SCREEN_WIDTH // 2 - 150, 50)
        draw_text(screen, "1: Easy", font, BLACK, SCREEN_WIDTH // 2 - 100, 150)
        draw_text(screen, "2: Medium", font, BLACK, SCREEN_WIDTH // 2 - 100, 200)
        draw_text(screen, "3: Hard", font, BLACK, SCREEN_WIDTH // 2 - 100, 250)
        draw_text(screen, "4: Back to Main Menu", font, BLACK, SCREEN_WIDTH // 2 - 150, 300)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reset_progress()  # Сбрасываем прогресс перед выходом
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_skin = select_skin(progress)
                    run_game(player_skin, progress, difficulty="easy")
                if event.key == pygame.K_2:
                    player_skin = select_skin(progress)
                    run_game(player_skin, progress, difficulty="medium")
                if event.key == pygame.K_3:
                    player_skin = select_skin(progress)
                    run_game(player_skin, progress, difficulty="hard")
                if event.key == pygame.K_4:
                    return  # Возврат в главное меню

# Выбор скина
def select_skin(progress):
    skins = [
        "skin_image1.png", "skin_image2.png", "skin_image3.png",
        "skin_image4.png", "skin_image5.png", "skin_image6.png",
        "skin_image7.png", "skin_image8.png"
    ]  # Путь к изображениям скинов
    skin_names = ["Skin 1", "Skin 2", "Skin 3", "Skin 4", "Skin 5", "Бобер", "Шлепа", "Огузок"]
    selected_skin = 0

    # Проверяем, есть ли у игрока уже какие-либо скины
    if progress['skins']:
        if progress['skins'][-1] in skin_names:
            selected_skin = skin_names.index(progress['skins'][-1])  # Выбираем индекс последнего купленного скина
        else:
            selected_skin = 0  # Если скин не найден, выбираем первый

    while True:
        screen.fill(WHITE)  # Очистка экрана
        draw_text(screen, "Select Your Skin", font, BLACK, SCREEN_WIDTH // 2 - 100, 50)
        draw_text(screen, "Use Left/Right Arrow Keys to Choose and Enter to Confirm", font, BLACK, 50, 500)

        # Загружаем и отображаем изображение скина
        try:
            skin_image = pygame.image.load(skins[selected_skin])  # Загружаем изображение скина
            skin_image = pygame.transform.scale(skin_image, (100, 100))  # Масштабируем изображение
            screen.blit(skin_image, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50))
            draw_text(screen, skin_names[selected_skin], font, BLACK, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 70)
        except FileNotFoundError:
            draw_text(screen, "Ошибка загрузки скина", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reset_progress()  # Сбрасываем прогресс перед выходом
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    selected_skin = (selected_skin + 1) % len(skins)
                if event.key == pygame.K_LEFT:
                    selected_skin = (selected_skin - 1) % len(skins)
                if event.key == pygame.K_RETURN:
                    return skins[selected_skin]  # Возвращаем путь к изображению выбранного скина

# Просмотр лучших результатов
def view_best_scores(progress):
    while True:
        screen.fill(WHITE)  # Очистка экрана перед отрисовкой
        draw_text(screen, "Best Scores", font, BLACK, SCREEN_WIDTH // 2 - 100, 50)

        best_scores = sorted(progress['best_scores'], reverse=True)[:5]
        for i, score in enumerate(best_scores):
            draw_text(screen, f"{i + 1}: {score}", font, BLACK, SCREEN_WIDTH // 2 - 100, 100 + i * 40)

        draw_text(screen, "Press ESC to Return", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reset_progress()  # Сбрасываем прогресс перед выходом
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

# Магазин
def shop(progress):
    skin_names = ["Бобер", "Шлепа", "Огузок"]
    skin_prices = [5, 5, 10]

    while True:
        screen.fill(WHITE)  # Очистка экрана перед отрисовкой
        draw_text(screen, "Shop", font, BLACK, SCREEN_WIDTH // 2 - 50, 50)
        draw_text(screen, f"Coins: {progress['coins']}", font, BLACK, SCREEN_WIDTH // 2 - 100, 100)

        # Отображаем все доступные скины для покупки
        for i, (name, price) in enumerate(zip(skin_names, skin_prices)):
            draw_text(screen, f"{i + 1}: Buy {name} ({price} Coins)", font, BLACK, SCREEN_WIDTH // 2 - 200, 150 + i * 50)

        draw_text(screen, "4: Exit Shop", font, BLACK, SCREEN_WIDTH // 2 - 200, 150 + len(skin_names) * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reset_progress()  # Сбрасываем прогресс перед выходом
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and progress['coins'] >= skin_prices[0] and skin_names[0] not in progress['skins']:
                    buy_sound.play()  # Звук покупки
                    progress['coins'] -= skin_prices[0]
                    progress['skins'].append(skin_names[0])
                    save_progress(progress)
                if event.key == pygame.K_2 and progress['coins'] >= skin_prices[1] and skin_names[1] not in progress['skins']:
                    buy_sound.play()  # Звук покупки
                    progress['coins'] -= skin_prices[1]
                    progress['skins'].append(skin_names[1])
                    save_progress(progress)
                if event.key == pygame.K_3 and progress['coins'] >= skin_prices[2] and skin_names[2] not in progress['skins']:
                    buy_sound.play()  # Звук покупки
                    progress['coins'] -= skin_prices[2]
                    progress['skins'].append(skin_names[2])
                    save_progress(progress)
                if event.key == pygame.K_4:
                    return

# Запуск игры
def run_game(player_skin, progress, difficulty):
    player = Player(player_skin)  
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    all_sprites.add(player)

    min_distance = 150
    max_distance = 300
    last_obstacle_x = SCREEN_WIDTH + 50

    score = 0
    coins_collected = 0
    running = True
    paused = False
    victory = False 

    # Настройки сложности
    if difficulty == "easy":
        obstacle_speed = 3
    elif difficulty == "medium":
        obstacle_speed = 5
    elif difficulty == "hard":
        obstacle_speed = 7

    # Переменные для увеличения скорости
    speed_increase_threshold = 1000  # Очки для увеличения сложности
    speed_increase_factor = 0.2  # Увеличение скорости

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RIGHT:
                    player.jump()
                if event.key == pygame.K_DOWN:
                    player.fall()  
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    save_progress(progress)
                    return

        if not paused:
            all_sprites.update()
            obstacles.update()
            coins.update()

            # Генерация монет
            if coins_collected < 5 and random.randint(1, 100) < 2:  
                coin = Coin(SCREEN_WIDTH + 50, SCREEN_HEIGHT - 80)
                all_sprites.add(coin)
                coins.add(coin)
                coins_collected += 1 

            if len(obstacles) == 0 or obstacles.sprites()[-1].rect.x < SCREEN_WIDTH - min_distance:
                obstacle_x = last_obstacle_x + random.randint(min_distance, max_distance)

                # Увеличиваем вероятность появления препятствий
                obstacle_appearance_chance = max(1, min(10, score // 400))  
                
                if random.randint(1, 100) < obstacle_appearance_chance * 2:  
                    obstacle_shape = random.choice(['square', 'triangle'])
                    obstacle_color = random.choice([BLACK, RED, BLUE])
                    obstacle_y = SCREEN_HEIGHT - 50 if random.choice([True, False]) else SCREEN_HEIGHT - 200

                    obstacle = Obstacle(obstacle_x, obstacle_y, obstacle_color, obstacle_shape)
                    obstacle.speed = obstacle_speed  
                    all_sprites.add(obstacle)
                    obstacles.add(obstacle)
                    last_obstacle_x = obstacle_x

            # Увеличиваем скорость игры и препятствий на каждые 1000 очков
            if score >= speed_increase_threshold:
                obstacle_speed += speed_increase_factor  # Увеличиваем скорость препятствий
                speed_increase_threshold += 1000  # Увеличиваем порог для следующего повышения

            score += 1

            if pygame.sprite.spritecollide(player, obstacles, False):
                lose_sound.play()  
                player.lives -= 1
                if player.lives <= 0:
                    progress['best_scores'].append(score)
                    save_progress(progress)
                    draw_text(screen, "Game Over!", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
                    pygame.display.update()
                    pygame.time.wait(2000)
                    return

            collected_coins = pygame.sprite.spritecollide(player, coins, True)
            for coin in collected_coins:
                coin_sound.play()  
                progress['coins'] += 1

            if score >= 4000 and not victory:
                victory = True 
                win_sound.play()  
                draw_text(screen, "Ай молодчинка! Прям чувствовал, что выиграешь!", font, GREEN, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2)
                pygame.display.update()
                pygame.time.wait(2000)  
                return  

            if game_bg is not None:
                screen.blit(game_bg, (0, 0))  
            all_sprites.draw(screen)
            obstacles.draw(screen)
            coins.draw(screen)
            draw_text(screen, f"Score: {score}", font, BLACK, 10, 10)
            draw_text(screen, f"Lives: {player.lives}", font, BLACK, 10, 40)
            draw_text(screen, f"Coins: {progress['coins']}", font, BLACK, 10, 70)

        else:
            draw_text(screen, "Game Paused", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press P to Resume or ESC to Quit", font, BLACK, SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 40)

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

# Инициализация
def main():
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    progress = load_progress()
    main_menu(progress)
    pygame.quit()

if __name__ == "__main__":
    main()
