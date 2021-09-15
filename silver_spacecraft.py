import math
import random
import time
import arcade

class Enemy(arcade.Sprite):
    def __init__(self, w, h):
        super().__init__(':resources:images/space_shooter/playerShip2_orange.png')
        self.speed = 1.5
        self.width = 50
        self.height = 50
        self.center_x = random.randint(0, w)
        self.center_y = h
        self.angle = 180
        self.explosion_sound = arcade.sound.load_sound(':resources:sounds/explosion1.wav')

    def move(self):
        self.center_y -= self.speed



class Bullet(arcade.Sprite):
    def __init__(self, host):
        super().__init__(':resources:images/space_shooter/laserRed01.png')
        self.width = 12
        self.height = 40
        self.speed = 4
        self.center_x = host.center_x
        self.center_y = host.center_y
        self.change_x = 0
        self.angle = host.angle
        self.fire_sound = arcade.sound.load_sound(':resources:sounds/laser1.mp3')
    
    def move(self):
        self.angle_rad = math.radians(self.angle)
        self.center_x -= self.speed * math.sin(self.angle_rad)
        self.center_y += self.speed * math.cos(self.angle_rad)

class SpaceCraft(arcade.Sprite):
    def __init__(self, w, h):
        super().__init__(':resources:images/space_shooter/playerShip1_blue.png')
        self.width = 50
        self.height = 50
        self.speed = 4
        self.speed_for_angle = 3
        self.center_x = w // 2
        self.center_y = 40
        self.change_x = 0
        self.angle = 0
        self.change_angle = 0
        self.bullet_list = []
        self.score = 0
        self.life_list = ['❤'] * 3
        self.lives = '❤' * len(self.life_list)
    
    def move(self):
        self.center_x += self.change_x * self.speed
    
    def rotate(self):
        self.angle += self.change_angle * self.speed_for_angle
    
    def fire(self):
        self.bullet_list.append(Bullet(self))
    
    def scores(self):
        self.score += 1

    def hp(self):
        if len(self.life_list) > 0:
            del self.life_list[-1]
            self.lives = '❤' * len(self.life_list)


class Game(arcade.Window):
    def __init__(self):
        self.w = 800
        self.h = 600
        super().__init__(self.w, self.h, 'Silver SpaceCraft')
        self.background_img = arcade.load_texture(':resources:images/backgrounds/stars.png')
        arcade.set_background_color(arcade.color.BLACK)

        self.me = SpaceCraft(self.w, self.h)
        self.bullet = Bullet(self.me)
        self.enemy = Enemy(self.w, self.h)
        self.enemy_list = []

        self.start_time_for_enemy = time.time()
        self.start_time = time.time()
        self.time_sleep_for_enemy = random.randint(0, 6)
        self.time_sleep = 3

        self.game_over = GameOver(self.w, self.h)
    
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, self.w, self.h, self.background_img)
        arcade.draw_text(f"Lives: {self.me.lives}", 10, 10, arcade.color.RED, 20, 20)
        arcade.draw_text(f"Score: {self.me.score}", self.w -130, 10, arcade.color.WHITE, 20, 20)
        self.me.draw()
        
        for i in range(len(self.me.bullet_list)):
            self.me.bullet_list[i].draw()

        for i in range(len(self.enemy_list)):
            self.enemy_list[i].draw()
        
        if len(self.me.life_list) == 0:
            self.game_over.on_draw()


    def on_update(self, delta_time: float):
        self.end_time_for_enemy = time.time()
        self.end_time = time.time()
        self.me.move()
        self.me.rotate()
        
        for enemy in self.enemy_list:
            enemy.move()

        for bullet in self.me.bullet_list:
            bullet.move()

        if self.end_time_for_enemy - self.start_time_for_enemy > self.time_sleep_for_enemy:
            self.enemy_list.append(Enemy(self.w, self.h))
            self.start_time_for_enemy = time.time()
            self.time_sleep_for_enemy = random.randint(0, 6)

        if self.end_time - self.start_time > self.time_sleep:
            for enemy in self.enemy_list:
                enemy.speed += 0.5
            self.start_time = time.time()
        
        for bullet in self.me.bullet_list:
            if bullet.center_y > self.h or bullet.center_y < 0 or bullet.center_x > self.w or bullet.center_x < 0:
                self.me.bullet_list.remove(bullet)
        
        for bullet in self.me.bullet_list:
            for enemy in self.enemy_list:
                if arcade.check_for_collision(bullet, enemy):
                    self.me.scores()
                    self.me.bullet_list.remove(bullet)
                    arcade.sound.play_sound(self.enemy.explosion_sound, 30)
                    self.enemy_list.remove(enemy)

        for enemy in self.enemy_list:
            if enemy.center_y < 0:
                self.enemy_list.remove(enemy)
                self.me.hp()


    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.me.change_x = -1
        
        elif key == arcade.key.D:
            self.me.change_x = 1

        elif key == arcade.key.LEFT:
            self.me.change_angle = 1

        elif key == arcade.key.RIGHT:
            self.me.change_angle = -1

        elif key == arcade.key.SPACE:
            self.me.fire()
            arcade.sound.play_sound(self.bullet.fire_sound, 50)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.me.change_x = 0
        
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.me.change_angle = 0

        elif key == arcade.key.ESCAPE:
            self.game_over.exit_game()

        # elif key == arcade.key.P:
        #     self.game_over.play_again()

class GameOver(arcade.View):
    def __init__(self, w, h):
        super().__init__()
        self.w = w
        self.h = h
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, self.w - 1, 0, self.h -1)
        self.texture = arcade.load_texture(':resources:images/backgrounds/stars.png')
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, self.w, self.h, self.texture)
        arcade.draw_text('Game Over', self.w // 2.4, self.h // 2, arcade.color.WHITE, 20, 20)
        arcade.draw_text("Press 'ESC' for exit", self.w // 2.4, self.h // 2.3, arcade.color.WHITE, 12, 12)

    def exit_game(self):
        arcade.finish_render()
        arcade.exit()

    # def play_again(self):
    #     arcade.finish_render()
    #     arcade.exit()
    #     self.play = Game()
    #     arcade.run()


game = Game()
arcade.run()