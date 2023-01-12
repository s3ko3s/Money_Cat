import pygame
from pygame import *
from player import Player
from blocks import Platform, BlockDie, BlockDieUp, Coin
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import sqlite3

pygame.init()
WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "Black"
PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#FF6262"
MAX_SCORE = 30
Minute = 0
Hour = 0
screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("Money-Cat")
font_name = pygame.font.match_font('arial')
LEVEL = '1'
level = []
entities = pygame.sprite.Group()  # все спрайты
platforms = []  # все спрайты-платформы


# экран заставки
def start_screen():
    global LEVEL, MAX_SCORE
    intro_text = ["                   MONEY-CAT ", "", "", "", "",
                  "  Управление:",
                  "  W или SPACE - прыжок",
                  "  A, D - ходьба",
                  "  Цель - собрать все монеты на уровне", "",
                  "  Начните уровень, нажав на цифры 1-4", ""]

    fon = pygame.transform.scale(pygame.image.load('Images/fon.jpg'), (WIN_WIDTH, WIN_HEIGHT))
    screen.blit(fon, (0, 0))
    text_coord = 60
    # прорисовка для кажой линии в intro_text
    for line in intro_text:
        if intro_text[0] == line:
            font = pygame.font.Font(None, 60)
        else:
            font = pygame.font.Font(None, 30)
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # выбор уровня, для каждого меняются значения max_score и level
            if event.type == pygame.KEYDOWN and event.key == K_1:
                LEVEL = '1'
                MAX_SCORE = 20
                return
            elif event.type == pygame.KEYDOWN and event.key == K_2:
                LEVEL = '2'
                MAX_SCORE = 30
                return
            elif event.type == pygame.KEYDOWN and event.key == K_3:
                LEVEL = '3'
                MAX_SCORE = 45
                return
            elif event.type == pygame.KEYDOWN and event.key == K_4:
                LEVEL = '4'
                MAX_SCORE = 60
                return
        pygame.display.flip()


# экран паузы
def pause_screen():
    pause_text = ["                      PAUSED", "", "", "", "",
                  "  Управление:",
                  "  W или SPACE - прыжок",
                  "  A, D - ходьба", "",
                  "  НАЖМИТЕ ENTER, ЧТОБЫ ПРОДОЛЖИТЬ."]
    fon = pygame.transform.scale(pygame.image.load('Images/fon.jpg'), (WIN_WIDTH, WIN_HEIGHT))
    screen.blit(fon, (0, 0))
    text_coord = 60
    for line in pause_text:
        if pause_text[0] == line:
            font = pygame.font.Font(None, 60)
        else:
            font = pygame.font.Font(None, 30)
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()


# пауза
def pause():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pause_screen()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            paused = False

        pygame.display.update()


# камера перемещения
class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)



# конфигурация камеры
def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


# Если выйграл - открывать эту форму
class VictoryForm(QMainWindow):
    def __init__(self, time, score, attempts):
        super().__init__()
        self.setFixedSize(500, 500)
        uic.loadUi('victory.ui', self)
        self.time_str = str(time)
        self.score_str = str(score)
        self.attempts_str = str(attempts)
        self.level = str(level)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('VICTORY!')
        self.score.setText(self.score_str)
        self.time.setText(self.time_str)
        self.attempts.setText(self.attempts_str)
        self.pushButton.clicked.connect(self.saveResult)
        self.pushButton_2.clicked.connect(self.cancel)


     # кнопка сохранения результата в БД
    def saveResult(self):
        con = sqlite3.connect("results.sqlite")
        sql = f"""INSERT INTO players (player_name,
                                        level,
                                        time,
                                        attempts)
                            VALUES ('{self.lineEdit.text()}',
                                    '{LEVEL}',
                                    '{self.time_str}',  
                                    '{self.attempts_str}')"""
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
        self.close()

    # кнопка отмены
    def cancel(self):
        terminate()


# функция, чтобы писать текст
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color("WHITE"))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# прорисовка уровня
def loadLevel():
    global LEVEL
    # проверка на наличие файла
    try:
        levelFile = open(f"Levels/level{LEVEL}.txt")
        line = " "
        while line[0] != "/":  # пока не нашли символ завершения файла
            line = levelFile.readline()  # считываем построчно
            if line.rstrip() == '[':  # если нашли символ начала уровня
                while line[0] != "]":  # то, пока не нашли символ конца уровня
                    line = levelFile.readline()  # считываем построчно уровень
                    if line[0] != "]":  # и если нет символа конца уровня
                        endLine = line.find("|")  # то ищем символ конца строки
                        level.append(line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"
    except:
        print("NO SUCH FILE EXISTING!")
        terminate()


# основная функция
def main():
    global MAX_SCORE
    hero = Player(55, 70)  # создаем героя
    entities.add(hero)
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))  # задний фон
    bg.fill(Color(BACKGROUND_COLOR))
    left = right = False
    up = False
    # загружаем файл с уровнем
    loadLevel()
    # прорисовка уровня
    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)

            x += PLATFORM_WIDTH
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "=":
                bd = BlockDieUp(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "+":
                coin = Coin(x, y)
                entities.add(coin)
                platforms.append(coin)
        y += PLATFORM_HEIGHT  # Ñ‚Ð¾ Ð¶Ðµ Ñ�Ð°Ð¼Ð¾Ðµ Ð¸ Ñ� Ð²Ñ‹Ñ�Ð¾Ñ‚Ð¾Ð¹
        x = 0

    timer = pygame.time.Clock()

    total_level_width = len(level[0]) * PLATFORM_WIDTH
    total_level_height = len(level) * PLATFORM_HEIGHT
    # создание камеры
    camera = Camera(camera_configure, total_level_width, total_level_height)
    victory = False  # проверка на победу
    vic = Victory()
    pl = Play()
    run = True
    while run:  # Основной цикл
        timer.tick(60)
        if hero.score == MAX_SCORE:
            victory = True  # если определенное кол-во очков - победа
        for e in pygame.event.get():
            if e.type == QUIT:
                run = False
            # физика героя
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                left = False
                right = False
                up = False
                hero.update(left, right, up, platforms, entities)
                pause()

            if e.type == KEYDOWN and (e.key == K_SPACE or e.key == K_w):
                up = True

            if e.type == KEYUP and (e.key == K_SPACE or e.key == K_w):
                up = False

            if e.type == KEYDOWN and e.key == K_a:
                left = True
            if e.type == KEYDOWN and e.key == K_d:
                right = True

            if e.type == KEYUP and e.key == K_d:
                right = False
            if e.type == KEYUP and e.key == K_a:
                left = False

        pl.update_timer()
        # если победа - вывести окно сохранения результатов
        if victory:
            app = QApplication(sys.argv)
            ex = VictoryForm(vic.pin_up_timer(), MAX_SCORE, hero.deaths + 1)
            pygame.quit()
            ex.show()
            sys.exit(app.exec_())

        screen.blit(bg, (0, 0))
        hero.update(left, right, up, platforms, entities)  # обновляем героя
        camera.update(hero)  # обновляем камеру героя
        for e in entities:  # прорисовка каждого спрайта в группе enteties
            screen.blit(e.image, camera.apply(e))
        # отображение на экране кол-ва попыток, очки и уровень
        draw_text(screen, f"Level {LEVEL}" + "    " + "Attempts: " + str(hero.deaths + 1) \
                  + '        ' + "Score: " + str(hero.score), 24, WIN_WIDTH / 2, 5)
        pygame.display.update()  # обновляем экран