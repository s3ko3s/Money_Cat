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