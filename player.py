from pygame import *
import blocks
import pyganim

# переменные
MOVE_SPEED = 10
WIDTH = 48
HEIGHT = 60
COLOR = "#888888"
JUMP_POWER = 12
GRAVITY = 0.6
JUMP_EXTRA_POWER = 1
ANIMATION_DELAY = 0.1
# файлы для анимации героев
ANIMATION_STAY = [('Idle/Idle1.png'), ('Idle/Idle2.png'), ('Idle/Idle3.png'), ('Idle/Idle4.png'), ('Idle/Idle5.png')]
ANIMATION_LEFT = [('Left/Left1.png'), ('Left/Left2.png'), ('Left/Left3.png'), ('Left/Left4.png'),
                  ('Left/Left5.png'), ('Left/Left6.png'), ('Left/Left7.png'), ('Left/Left8.png')]
ANIMATION_RIGHT = [('Right/Right1.png'), ('Right/Right2.png'), ('Right/Right3.png'), ('Right/Right4.png'),
                   ('Right/Right5.png'), ('Right/Right6.png'), ('Right/Right7.png'), ('Right/Right8.png')]
ANIMATION_JUMP_LEFT = [('Jump/JumpLeft.png', 0.1)]
ANIMATION_JUMP_RIGHT = [('Jump/JumpRight.png', 0.1)]
ANIMATION_JUMP = [('Jump/Jump.png', 0.1)]


class Player(sprite.Sprite):  # спрайт игрока
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0  # скорость перемещения
        self.yvel = 0  # скорость вертикального перемещения
        self.onGround = False
        self.startX = x  # начальная позиция x
        self.startY = y  # начальная позиция y
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.rect = Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.score = 0
        self.deaths = 0

        self.image.set_colorkey(Color(COLOR))  # делаем фон прозрачным
        # Анимация движения
        # вправо
        boltAnim = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()
        # влево
        boltAnim = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()
        # игрок стоит
        boltAnim = []
        for anim in ANIMATION_STAY:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimStay = pyganim.PygAnimation(boltAnim)
        self.boltAnimStay.play()
        # анимации прыжка
        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()

        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.play()

    def update(self, left, right, up, platforms, entities):
        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
            self.image.fill(Color(COLOR))
            self.boltAnimJump.blit(self.image, (0, 0))

        if left: # прыжок влево
            self.xvel = -MOVE_SPEED  # движение влево
            self.image.fill(Color(COLOR))
            if up:  # отдельная анимация
                self.boltAnimJumpLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))

        if right:  # прыжок вправо
            self.xvel = MOVE_SPEED  # движение вправо
            self.image.fill(Color(COLOR))
            if up: # отдельная анимация
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))

        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(Color(COLOR))
                self.boltAnimStay.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms, entities)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms, entities)

    def collide(self, xvel, yvel, platforms, entities):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, blocks.BlockDie):  # если пересакаемый блок - blocks.BlockDie
                    self.die()
                    self.deaths += 1
                    break

                if isinstance(p, blocks.BlockDieUp):  # если пересакаемый блок - blocks.BlockUp
                    self.die()
                    self.deaths += 1
                    break

                if isinstance(p, blocks.Coin):  # если пересакаемый блок - blocks.Coin
                    self.score += 5
                    platforms.remove(p)
                    entities.remove(p)

                if xvel > 0:                      # если движется вправо
                    self.rect.right = p.rect.left  # то не движется вправо

                if xvel < 0:                      # если движется влево
                    self.rect.left = p.rect.right  # то не движется влево

                if yvel > 0:                      # если падает вниз
                    self.rect.bottom = p.rect.top  # то не падает вниз
                    self.onGround = True          # и становится на что-то твердое
                    self.yvel = 0                 # и энергия падения пропадает

                if yvel < 0:                      # если движется вверх
                    self.rect.top = p.rect.bottom  # то не движется вверх
                    self.yvel = 0                 # и энергия прыжка пропадае

    def teleporting(self, goX, goY):
        self.rect.x = goX # координаты назначения перемещения
        self.rect.y = goY # координаты назначения перемещения
        self.xvel = 0
        self.yvel = 0

    def die(self):
        time.wait(500)
        self.teleporting(self.startX, self.startY)  # перемещаемся в начальные координаты
