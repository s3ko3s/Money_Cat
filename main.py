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
        while line[0] != "/":
            line = levelFile.readline()
            if line.rstrip() == '[':
                while line[0] != "]":
                    line = levelFile.readline()
                    if line[0] != "]":
                        endLine = line.find("|")
                        level.append(line[0: endLine])
    except:
        print("NO SUCH FILE EXISTING!")
        terminate()