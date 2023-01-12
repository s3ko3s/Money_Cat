from pygame import *

# переменные
PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#FF6262"


class Platform(sprite.Sprite):  # класс обычной платформы
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load("Images/block.png")
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class BlockDie(Platform):  # класс шипа снизу
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = image.load("Images/spike.png")


class BlockDieUp(Platform):  # класс шипа сверху
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = image.load("Images/spikeUp.png")


class Coin(sprite.Sprite):  # класс монеты
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = image.load("Images/coin.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.kill()  # удалить монеты из всех групп спрайтов
