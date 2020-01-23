import random
import pygame
import numpy

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

pygame.init()
game_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Blob Arena")
clock = pygame.time.Clock()


# represents rooms drawn in the game
class Room(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, door=2, depth=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        # door is which side of the room the door will appear on
        self.door = door
        self.top = pygame.Rect(self.x, self.y, self.width, self.depth)
        self.left = pygame.Rect(self.x, self.y, self.depth, self.height)
        self.bottom = pygame.Rect(self.x, (self.y + self.height) - self.depth, self.width, self.depth)
        self.right = pygame.Rect((self.x + self.width) - self.depth, self.y, self.depth, self.height)
        self.area = pygame.Rect(self.x, self.y, self.width, self.height)
        # make door to room on the appropriate side, wall_list is the list of walls selected to form a room
        if self.door == 0:
            self.top_left = pygame.Rect(self.x, self.y, self.width / 4, self.depth)
            self.top_right = pygame.Rect(self.x + 3 * (self.width / 4), self.y, self.width / 4, self.depth)
            self.wall_list = [self.top_left, self.top_right, self.left, self.bottom, self.right]
        elif self.door == 1:
            self.left_top = pygame.Rect(self.x, self.y, self.depth, self.height / 4)
            self.left_bottom = pygame.Rect(self.x, self.y + 3 * (self.height / 4), self.depth, self.height / 4)
            self.wall_list = [self.top, self.left_top, self.left_bottom, self.bottom, self.right]
        elif self.door == 2:
            self.bottom_left = pygame.Rect(self.x, (self.y + self.height) - self.depth, (self.width / 4), self.depth)
            self.bottom_right = pygame.Rect(self.x + 3 * (self.width / 4), (self.y + self.height) - self.depth,
                                            self.width / 4, self.depth)
            self.wall_list = [self.top, self.left, self.bottom_left, self.bottom_right, self.right]
        elif self.door == 3:
            self.right_top = pygame.Rect((self.x + self.width) - self.depth, self.y, self.depth, self.height / 4)
            self.right_bottom = pygame.Rect((self.x + self.width) - self.depth, self.y + 3 * (self.height / 4),
                                            self.depth, self.height / 4)
            self.wall_list = [self.top, self.left, self.bottom, self.right_top, self.right_bottom]


# represents a bullet shown on screen
class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun, x_move, y_move, speed=7.0):
        self.x = float(gun.x)
        self.y = float(gun.y)
        self.x_move = float(x_move)
        self.y_move = float(y_move)
        self.speed = speed
        self.width = 5
        self.height = 5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


class Gun:
    def __init__(self, player, shot_delay=15):
        self.x = float(player.x)
        self.y = float(player.y)
        self.damage = 25
        self.bullets = []
        self.shot_delay = shot_delay
        self.cooldown = 0

    # moves all bullets that were shot by a given player/enemy gun
    def move_bullets(self):
        count = 0
        if len(self.bullets) == 0:
            return
        for bullet in self.bullets:
            if 0 > bullet.x or bullet.x > DISPLAY_WIDTH or 0 > bullet.y or bullet.y > DISPLAY_HEIGHT:
                del self.bullets[count]
            bullet.x += bullet.x_move * bullet.speed
            bullet.y += bullet.y_move * bullet.speed
            bullet.rect.x = int(bullet.x)
            bullet.rect.y = int(bullet.y)
            count += 1


# User is the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.health = 100
        self.speed = 9
        self.x = 10.0
        self.y = 10.0
        self.size = 8
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.gun = Gun(self)

    # allow user to move using wasd unless they will run into a wall or off the screen
    def move(self, rooms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and self.y < DISPLAY_HEIGHT - self.size:
            do_move = True
            future_rect = self.rect.move(0, 5)
            for room in rooms:
                for wall in room.wall_list:
                    if future_rect.colliderect(wall) or ((wall.x < future_rect.x < wall.x + wall.width) and (wall.y < future_rect.y < wall.y + wall.height)):
                        do_move = False
            if do_move:
                self.y = self.y + 5
                self.rect = self.rect.move(0, 5)
        if keys[pygame.K_w] and self.y > 0 + self.size:
            do_move = True
            future_rect = self.rect.move(0, -5)
            for room in rooms:
                for wall in room.wall_list:
                    if future_rect.colliderect(wall):
                        do_move = False
            if do_move:
                self.y = self.y - 5
                self.rect = self.rect.move(0, -5)

        if keys[pygame.K_d] and self.x < DISPLAY_WIDTH - self.size:
            do_move = True
            future_rect = self.rect.move(5, 0)
            for room in rooms:
                for wall in room.wall_list:
                    if future_rect.colliderect(wall):
                        do_move = False
            if do_move:
                self.x = self.x + 5
                self.rect = self.rect.move(5, 0)
        if keys[pygame.K_a] and self.x > 0 + self.size:
            do_move = True
            future_rect = self.rect.move(-5, 0)
            for room in rooms:
                for wall in room.wall_list:
                    if future_rect.colliderect(wall):
                        do_move = False
            if do_move:
                self.x = self.x - 5
                self.rect = self.rect.move(-5, 0)

        self.gun.x = self.x
        self.gun.y = self.y

    # allow user to shoot by clicking the mouse, bullet will be fired at the cursor location
    def shoot(self):
        if self.gun.cooldown == 0:
            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                move = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
                distance = numpy.sqrt(move[0] ** 2 + move[1] ** 2)
                norm = (move[0] / distance, move[1] / distance)
                bullet = Bullet(self.gun, norm[0], norm[1])
                self.gun.bullets.append(bullet)
                self.gun.cooldown = self.gun.shot_delay
        else:
            self.gun.cooldown -= 1


# CPU players that attack user
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        self.health = 100
        self.speed = 5
        self.x = random.randrange(0, 800)
        self.y = random.randrange(0, 600)
        self.width = 20
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.gun = Gun(self, 80)
        self.alive = True

    # enemies move randomly
    def move(self):
        x_move = random.randrange(-2, 3)
        y_move = random.randrange(-2, 3)
        self.rect = self.rect.move(x_move, y_move)
        self.x += x_move
        self.y += y_move
        self.gun.x = self.x
        self.gun.y = self.y

    # enemies will shoot at player upon cooldown of their gun
    def shoot(self, player):
        if self.gun.cooldown == 0:
            move = (player.x - self.x, player.y - self.y)
            distance = numpy.sqrt(move[0] ** 2 + move[1] ** 2)
            norm = (move[0] / distance, move[1] / distance)
            bullet = Bullet(self.gun, norm[0], norm[1], 4)
            self.gun.bullets.append(bullet)
            self.gun.cooldown = self.gun.shot_delay
        else:
            self.gun.cooldown -= 1


# re-draw all players, walls and bullets
def update_screen(player, enemies, rooms):
    game_display.fill(WHITE)
    pygame.draw.circle(game_display, BLUE, (int(player.x), int(player.y)), player.size)
    for enemy in enemies:
        pygame.draw.rect(game_display, RED, enemy.rect)
        for bullet in enemy.gun.bullets:
            pygame.draw.rect(game_display, BLACK, bullet.rect)
    for bullet in player.gun.bullets:
        pygame.draw.rect(game_display, GREEN, bullet.rect)
    for room in rooms:
        for rect in room.wall_list:
            pygame.draw.rect(game_display, BLACK, rect)

    pygame.display.update()


def player_actions(player, rooms):
    player.shoot()
    player.move(rooms)
    player.gun.move_bullets()


def enemy_actions(enemies, player):
    for enemy in enemies:
        enemy.shoot(player)
        enemy.move()
        enemy.gun.move_bullets()


# subtract health if bullets collide with player or enemies
def character_bullet_collisions(player, enemies):
    for enemy in enemies:
        enemy_alive = True
        for bullet in player.gun.bullets:
            if bullet.rect.colliderect(enemy.rect):
                enemy.health -= player.gun.damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    del enemy
                enemy_alive = False
                player.gun.bullets.remove(bullet)
                del bullet
                break

        if enemy_alive:
            for bullet in enemy.gun.bullets:
                if bullet.rect.colliderect(player.rect):
                    player.health -= enemy.gun.damage
                    if player.health <= 0:
                        del player
                        pygame.quit()
                        quit()
                    enemy.gun.bullets.remove(bullet)
                    del bullet


# remove bullets if they collide with a wall
def wall_bullet_collisions(player, enemies, rooms):
    for room in rooms:
        for bullet in player.gun.bullets:
            for rect in room.wall_list:
                if bullet.rect.colliderect(rect):
                    player.gun.bullets.remove(bullet)
                    del bullet
                    break
        for enemy in enemies:
            for bullet in enemy.gun.bullets:
                for rect in room.wall_list:
                    if bullet.rect.colliderect(rect):
                        enemy.gun.bullets.remove(bullet)
                        del bullet
                        break


def detect_collisions(player, enemies, rooms):
    character_bullet_collisions(player, enemies)
    wall_bullet_collisions(player, enemies, rooms)


# main game loop
def game_loop(player, enemies, rooms):
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        player_actions(player, rooms)
        enemy_actions(enemies, player)
        detect_collisions(player, enemies, rooms)
        update_screen(player, enemies, rooms)
        clock.tick(60)


# initialize game
def main():
    player = Player()
    enemies = []
    room = Room(200, 300, 160, 160)
    room2 = Room(500, 400, 100, 80)
    rooms = [room, room2]
    for e in range(2):
        e = Enemy()
        enemies.append(e)
    game_loop(player, enemies, rooms)
    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
