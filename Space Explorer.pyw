# Space Explorer

from livewires import games, color
import os.path

games.init(640, 480, 50)#, "Space Explorer")

class SAdjuster(games.Sprite):
    def adjust(self, dx):
        self.x -= dx

class AAdjuster(games.Animation):
    def adjust(self, dx):
        self.x -= dx

class Moon(SAdjuster):
    all = []
    def __init__(self, left):
        super(Moon, self).__init__(games.load_image("images/moon.bmp"),
                                   left=left, bottom=480)
        self.terrain = True
        self.go_through = False
        self.hole = False

        Moon.all.append(self)

    def destroy(self):
        Moon.all.remove(self)
        super(Moon, self).destroy()

class Hill(SAdjuster):
    def __init__(self, num, x, bottom, go_through):
        # num is width-height-design
        super(Hill, self).__init__(games.load_image("images/hill"+num+".bmp"),
                                   x=x, bottom=bottom)
        self.terrain = True
        self.go_through = go_through
        self.hole = False

class Hole(SAdjuster):
    def __init__(self, num, x, bottom):
        super(Hole, self).__init__(games.load_image("images/hole"+str(num)+".bmp"),
                                    x=x, bottom=bottom)
        self.terrain = False
        self.go_through = False
        self.hole = True

    def update(self):
        for sprite in self.overlapping_sprites:
            if sprite.left > self.left + 2 and sprite.right < self.right - 2:
                sprite.y += 1


class Man(games.Sprite):
    SPEED = 1
    def __init__(self, game, bottom):
        self.game = game
        self.man_image_right = games.load_image("images/space_man(right).bmp")
        self.man_image_left = games.load_image("images/space_man(left).bmp")
        super(Man, self).__init__(image = self.man_image_right,
                                  x = 20,
                                  bottom = bottom)
        self.timer = 0
        self.jump = 0
        self.can_jump = True
        self.can_fall = False
        self.can_walk_right = True
        self.can_walk_left = True

    def move(self, dx):
        if (dx > 0 and (self.x != games.screen.width/2 or Moon.all[-1].right == 640)) or (dx < 0 and (self.x != games.screen.width/2 or Moon.all[0].left == 0)):
            self.x += dx
        else:
            for sprite in games.screen.all_objects:
                if sprite != self and sprite not in self.game.info_sprites:
                    sprite.adjust(dx)

    def update(self):
        # make man move right
        if games.keyboard.is_pressed(games.K_RIGHT):
            # make sure image is man_image_right
            if self.image == self.man_image_left:
                self.image = self.man_image_right
            self.move(Man.SPEED)

        # make man move left
        if games.keyboard.is_pressed(games.K_LEFT):
            # make sure image is man_image_left
            if self.image == self.man_image_right:
                self.image = self.man_image_left
            self.move(-Man.SPEED)

        # make sure man does not walk through certain sprites
        for sprite in self.overlapping_sprites:
            if sprite.go_through:
                self.can_walk_right = True
                self.can_walk_left = True
            if not sprite.go_through and self.bottom == sprite.top + 1:
                self.can_walk_right = True
                self.can_walk_left = True
            if not sprite.go_through and self.bottom != sprite.top + 1:
                if self.right == sprite.left + 1:
                    self.can_walk_right = False
                    self.move(-Man.SPEED)
                if self.left == sprite.right - 1:
                    self.can_walk_left = False
                    self.move(Man.SPEED)
                break

        # make sure man does not go beyond screen bounderies
        if self.left < 0:
            self.left = 0
        if self.right > games.screen.width:
            self.right = games.screen.width

        # decrease timer
        if self.timer > 0:
            self.timer -= 1

        # shoot laser
        if games.keyboard.is_pressed(games.K_SPACE) and self.timer == 0:
            if self.image == self.man_image_right:
                laser = Laser(self.game, "red", x = self.x + 17, y = self.y - 4,
                              direction = 1)
                games.screen.add(laser)
            if self.image == self.man_image_left:
                laser = Laser(self.game, "red", x = self.x - 16, y = self.y - 4,
                              direction = -1)
                games.screen.add(laser)
            # reset timer
            self.timer = 25

        # make man jump
        if games.keyboard.is_pressed(games.K_DOWN) and self.can_jump:
            self.jump = 50
            self.can_jump = False

        if self.jump > 0:
            self.y -= 2
            self.jump -= 1

        # make man fall
        for j in range(2):
            if self.jump == 0:
                if self.overlapping_sprites:
                    for sprite in self.overlapping_sprites:
                        if sprite.terrain:
                            if self.bottom != sprite.top + 1:
                                self.can_fall = True
                            else:
                                self.can_fall = False
                                break
                        else:
                            self.can_fall = True
                else:
                    self.can_fall = True
            if self.can_fall:
                self.y += 1
                self.can_fall = False

        # see if man can jump
        for sprite in self.overlapping_sprites:
            if sprite.terrain and self.bottom == sprite.top + 1:
                self.can_jump = True
            if sprite.hole and self.left > sprite.left + 2 and self.right < sprite.right - 2:
                self.can_jump = False
                break

        # make man die if he falls below the screen
        if self.top > games.screen.height:
            self.die()

    def die(self):
        self.game.lives -= 1
        self.destroy()
        for sprite in games.screen.all_objects:
            sprite.stop()
        if self.game.lives < 0:
            message = games.Message("Game Over!", 90, color.blue,
                                    x=games.screen.width/2, y=games.screen.height/2,
                                    lifetime=250, after_death=games.screen.quit,
                                    is_collideable=False)
            games.screen.add(message)
        else:
            message = games.Message("You Died!", 90, color.blue,
                                    x=games.screen.width/2, y=games.screen.height/2,
                                    lifetime=250, after_death=self.game.restart_level,
                                    is_collideable=False)
            games.screen.add(message)

class Robot(SAdjuster):
    all = []
    def __init__(self, game, x, bottom, br, bl):
        self.game = game
        self.right_image = games.load_image("images/robot(right).bmp")
        self.left_image = games.load_image("images/robot(left).bmp")
        self.right_dead = games.load_image("images/robot_dead(right).bmp")
        self.left_dead = games.load_image("images/robot_dead(left).bmp")
        super(Robot, self).__init__(image=self.left_image, x=x, bottom=bottom)
        self.terrain = False
        self.br = br
        self.bl = bl
        self.dead = False
        self.right_boundry = self.x + self.br
        self.left_boundry = self.x - self.bl
        self.going_right = False
        self.shooting_right = False
        self.is_shooting = False
        self.timer = 0
        self.go_through = True
        self.can_fall = False
        self.hole = False

        Robot.all.append(self)

    def update(self):
        if not self.dead:
            if not self.is_shooting:
              # determine which way to move
              if self.right == self.right_boundry:
                self.going_right = False
              if self.left == self.left_boundry:
                self.going_right = True

              # move sprite
              if self.going_right == True:
                if self.image == self.left_image:
                  self.image = self.right_image
                self.x += 1
              else:
                if self.image == self.right_image:
                  self.image = self.left_image
                self.x -= 1

            # decrease timer
            if self.timer > 0:
              self.timer -= 1

            # allows robot to shoot
            if self.top < self.game.man.y < self.bottom and self.x - 380 <= self.game.man.x <= self.x:
              if self.image == self.right_image:
                  self.image = self.left_image
              self.shooting_right = False
              self.is_shooting = True

              can_shoot = True
              for robot in Robot.all:
                  if not robot.dead and self.top < robot.y < self.bottom and self.game.man.right < robot.left < self.left:
                      can_shoot = False
                      break

              if self.timer == 0 and can_shoot:
                laser = Laser(self.game, "green", x=self.x-18, y=self.y-5,
                              direction=-1)
                games.screen.add(laser)
                # reset timer
                self.timer = 25

            elif self.top < self.game.man.y < self.bottom and self.x + 380 >= self.game.man.x > self.x:
              if self.image == self.left_image:
                  self.image = self.right_image
              self.shooting_right = True
              self.is_shooting = True

              can_shoot = True
              for robot in Robot.all:
                  if not robot.dead and self.top < robot.y < self.bottom and self.right < robot.right < self.game.man.left:
                      can_shoot = False
                      break

              if self.timer == 0 and can_shoot:
                laser = Laser(self.game, "green", x=self.x+19, y=self.y-5,
                              direction=1)
                games.screen.add(laser)
                # reset timer
                self.timer = 25

            else:
              self.is_shooting = False

            # make robot fall
            for j in range(2):
              if not self.get_overlapping_sprites():
                self.can_fall = True
              if self.get_overlapping_sprites():
                for sprite in self.overlapping_sprites:
                  if sprite.terrain == True and self.bottom != sprite.top + 1:
                    self.can_fall = True
                  elif sprite.terrain == False:
                    self.can_fall = True
                  else:
                    self.can_fall = False
                    break
              if self.can_fall:
                  self.y += 1

        else:
            if self.is_shooting:
                if self.shooting_right:
                    self.set_image(self.right_dead)
                else:
                    self.set_image(self.left_dead)

            else:
                if self.going_right:
                    self.set_image(self.right_dead)
                else:
                    self.set_image(self.left_dead)

            if self.angle != 40:
                self.angle += 2
            self.y += 2

        if self.top > games.screen.height:
            self.destroy()

    def adjust(self, dx):
        super(Robot, self).adjust(dx)
        self.right_boundry -= dx
        self.left_boundry -= dx

    def die(self):
        self.dead = True

    def destroy(self):
        Robot.all.remove(self)
        super(Robot, self).destroy()

class Bomb_dropper(SAdjuster):
    def __init__(self, game, x, top, bl, br):
        self.game = game
        self.image_left1 = games.load_image("images/bomb_dropper(left)1.bmp")
        self.image_left2 = games.load_image("images/bomb_dropper(left)2.bmp")
        self.image_right1 = games.load_image("images/bomb_dropper(right)1.bmp")
        self.image_right2 = games.load_image("images/bomb_dropper(right)2.bmp")
        super(Bomb_dropper, self).__init__(self.image_left1, x=x, top=top)
        self.terrain = False
        self.go_through = True
        self.hole = False
        self.right_boundry = self.x + br
        self.left_boundry = self.x - bl
        self.going_right = False
        self.timer = 75

    def update(self):
        # determine which way to move
        if self.right == self.right_boundry:
            self.going_right = False
        if self.left == self.left_boundry:
            self.going_right = True

        # move sprite
        if self.going_right == True:
            if self.image == self.image_left1:
                self.image = self.image_right1
            elif self.image == self.image_left2:
                self.image = self.image_right2
            self.x += 1
        else:
            if self.get_image() == self.image_right1:
                self.set_image(self.image_left1)
            elif self.get_image() == self.image_right2:
                self.set_image(self.image_left2)
            self.x -= 1

        # allow robot to drop bombs
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.timer = 75

        if self.timer < 25:
            top = self.top
            if self.going_right:
                self.set_image(self.image_right2)
            else:
                self.set_image(self.image_left2)
            self.top = top
            if self.timer == 12:
                bomb = Bomb1(self, x = self.x, y = self.y + 28)
                games.screen.add(bomb)

        else:
            top = self.top
            if self.going_right:
                self.set_image(self.image_right1)
            else:
                self.set_image(self.image_left1)
            self.top = top

    def adjust(self, dx):
        super(Bomb_dropper, self).adjust(dx)
        self.right_boundry -= dx
        self.left_boundry -= dx

class Laser(SAdjuster):
    SPEED = 5
    def __init__(self, game, color, x, y, direction):
        self.game = game
        super(Laser, self).__init__(games.load_image("images/"+color+"_laser.bmp", False),
                                    x=x, y=y, dx=Laser.SPEED*direction)
        self.terrain = False
        self.go_through = True
        self.hole = False

    def update(self):
        for sprite in self.overlapping_sprites:
            if (sprite in Robot.all and sprite.dead == False) or sprite == self.game.man:
                if sprite in Robot.all:
                    sparks = Sparks(sprite.x, self.y)
                    games.screen.add(sparks)
                sprite.die()
                self.destroy()
            elif not sprite.go_through:
                self.destroy()

        if self.left > games.screen.width + 45 or self.right < -45:
            self.destroy()

class Sparks(AAdjuster):
    images = games.load_animation([os.path.join("images", "sparks1.bmp"),
                                   os.path.join("images", "sparks2.bmp"),
                                   os.path.join("images", "sparks3.bmp"),
                                   "images/sparks4.bmp",
                                   "images/sparks5.bmp",
                                   "images/sparks6.bmp",
                                   "images/sparks7.bmp"])
    def __init__(self, x, y):
        super(Sparks, self).__init__(Sparks.images, x=x, y=y, repeat_interval=2,
                                     n_repeats=1, is_collideable=False)

class Explosion(AAdjuster):
    """ Explosion animation. """
    images = ["explosion10.bmp",
              "explosion11.bmp",
              "explosion12.bmp",
              "explosion13.bmp",
              "explosion14.bmp",
              "explosion15.bmp",
              "explosion16.bmp",
              "explosion17.bmp",
              "explosion18.bmp",
              "explosion19.bmp"]

    def __init__(self, game, x, y):
        self.game = game
        super(Explosion, self).__init__(Explosion.images, x=x, y=y,
                                        repeat_interval=4, n_repeats=1)
        self.terrain = False
        self.go_through = True
        self.hole = False

    def update(self):
        if self.overlaps(self.game.man):
            self.game.man.die()

class Bomb1(SAdjuster):
    def __init__(self, ship, x, y):
        self.ship = ship
        self.bomb_image = games.load_image("images/bomb.bmp")
        super(Bomb1, self).__init__(image=self.bomb_image, x=x, y=y)
        self.terrain = False
        self.go_through = True
        self.hole = False

    def update(self):
        super(Bomb1, self).update()
        if not self.overlapping_sprites:
            self.y += 2
        elif self.overlaps(self.ship):
            self.y += 2
        elif self.overlapping_sprites:
            explosion = Explosion(self.ship.game, x=self.x, y=self.y)
            games.screen.add(explosion)
            self.destroy()

class VElevator(SAdjuster):
    def __init__(self, color, x, y, bt, bb):
        super(VElevator, self).__init__(games.load_image("images/"+color+"_elevator.bmp"),
                                        x=x, y=y)
        self.terrain = True
        self.go_through = True
        self.moving = False
        self.moving_up = True
        self.hole = False
        self.boundry_top = bt
        self.boundry_bottom = bb

    def update(self):
        if self.moving:
            if self.bottom == self.boundry_bottom:
                self.moving_up = True
            if self.top == self.boundry_top:
                self.moving_up = False

            if self.moving_up:
                for sprite in self.overlapping_sprites:
                    if sprite.bottom == self.top + 1:
                        sprite.y -= 1
                self.y -= 1
            else:
                self.y += 1

class HElevator(SAdjuster):
    def __init__(self, color, x, y, br, bl, moving_right=False):
        super(HElevator, self).__init__(games.load_image("images/"+color+"_elevator.bmp"),
                                        x=x, y=y)
        self.terrain = True
        self.go_through = True
        self.moving = False
        self.moving_right = moving_right
        self.hole = False
        self.br = self.right + br
        self.bl = self.left - bl

    def update(self):
        if self.moving:
            if self.right >= self.br:
                self.moving_right = False
            if self.left <= self.bl:
                self.moving_right = True

            if self.moving_right:
                self.x += 1
                for sprite in self.overlapping_sprites:
                    if sprite.bottom == self.top + 1:
                        sprite.move(1)
            else:
                self.x -= 1
                for sprite in self.overlapping_sprites:
                    if sprite.bottom == self.top + 1:
                        sprite.move(-1)

    def adjust(self, dx):
        super(HElevator, self).adjust(dx)
        self.br -= dx
        self.bl -= dx

class Button(SAdjuster):
    def __init__(self, game, elevator, color, x, bottom):
        self.game = game
        self.elevator = elevator

        self.button_image = games.load_image("images/"+color+"_button.bmp")
        self.button_image_pressed = games.load_image("images/"+color+"_button(pressed).bmp")

        self.image_bottom = bottom
        super(Button, self).__init__(
            image = self.button_image,
            x = x, bottom = self.image_bottom)
        self.terrain = True
        self.go_through = True
        self.hole = False

    def update(self):
        for sprite in self.overlapping_sprites:
            if sprite == self.game.man and self.game.man.bottom == self.top + 1 and self.game.man.jump == 0:
                self.image = self.button_image_pressed
                self.bottom = self.image_bottom
                self.elevator.moving = True

class Platform(SAdjuster):
    TIMER = 40
    def __init__(self, game, left, top):
        self.game = game
        super(Platform, self).__init__(games.load_image("images/platform.bmp"),
                                       left=left, top=top)
        self.orig_left = left
        self.orig_top = top
        self.terrain = True
        self.go_through = True
        self.hole = False
        self.timer = Platform.TIMER
        self.timing = False

    def update(self):
        if self.overlaps(self.game.man) and self.game.man.bottom == self.top + 1 and self.game.man.jump == 0:
            self.timing = True
        if self.timing and self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.dy = 2
        if self.top > games.screen.height:
            self.dy = 0
            self.timer = Platform.TIMER
            self.timing = False
            if self.right < 0 or self.left > games.screen.width:
                self.left = self.orig_left
                self.top = self.orig_top

    def adjust(self, dx):
        super(Platform, self).adjust(dx)
        self.orig_left -= dx

class End_piece(SAdjuster):
    def __init__(self, game, x, bottom):
        self.game = game
        super(End_piece, self).__init__(games.load_image("images/oval.bmp"),
                                        x=x, bottom=bottom)
        self.terrain = False
        self.go_through = True
        self.hole = False

    def update(self):
        for sprite in self.overlapping_sprites:
            if sprite == self.game.man:
                self.game.next()
                self.destroy()

class Game(object):
    def __init__(self):
        self.level = 0
        self.levels = [self.level1, self.level2, self.level3, self.level4]
        self.lives = 1
        self.info_sprites = []
        self.next()

    def next(self):
        for sprite in games.screen.all_objects:
            sprite.stop()
        if self.level >= 2:
            self.lives += 1
        self.level += 1
        if self.level > len(self.levels):
            text = "You Won!"
            func = games.screen.quit
        else:
            text = "Level " + str(self.level-1) + " Complete!"
            func = self.levels[self.level-1]
        if self.level == 1:
            func()
        else:
            message = games.Message(text, 90, color.blue, x=games.screen.width/2,
                                    y=games.screen.height/2, lifetime=250,
                                    after_death=func)
            games.screen.add(message)

    def restart_level(self):
        self.levels[self.level-1]()

    def display_info(self):
        self.info_sprites = []
        text = games.Text("Lives: "+str(self.lives), 30, color.red, left=10,
                          top=10, is_collideable=False)
        games.screen.add(text)
        self.info_sprites.append(text)

    def level1(self):
        # patrol distance below: 400
        games.screen.clear()
        self.display_info()
        left = 0
        for i in range(2):
            moon = Moon(left)
            games.screen.add(moon)
            left = moon.right
        hill = Hill("1-1-2", 150, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 700, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 1250, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-1", 1450, Moon.all[0].top+1, True)
        games.screen.add(hill)
        hill = Hill("1-1-1", 1650, Moon.all[0].top+1, True)
        games.screen.add(hill)
        hill = Hill("1-1-2", 1850, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-3-2", 2400, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("5-1-2", 2794, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-2-3", 2497, Moon.all[0].top+4, False)
        games.screen.add(hill)

        elevator = VElevator("red", 2300, 451, 320, 460)
        games.screen.add(elevator)
        button = Button(self, elevator, "red", 1550, Moon.all[0].top+1)
        games.screen.add(button)

        robot = Robot(self, 400, Moon.all[0].top+1, 250, 200)
        games.screen.add(robot)
        robot = Robot(self, 975, Moon.all[0].top+1, 225, 225)
        games.screen.add(robot)
        robot = Robot(self, 1550, Moon.all[0].top+1, 250, 250)
        games.screen.add(robot)
        robot = Robot(self, 2794, Moon.all[0].top-49, 250, 247)
        games.screen.add(robot)
        robot = Robot(self, 3294, Moon.all[0].top+1, 250, 250)
        games.screen.add(robot)

        self.man = Man(self, Moon.all[0].top+1)
        games.screen.add(self.man)

        end_piece = End_piece(self, Moon.all[-1].right-50, Moon.all[-1].top-10)
        games.screen.add(end_piece)

    def level2(self):
        # patrol distance below: 400
        games.screen.clear()
        self.display_info()
        left = 0
        for i in range(2):
            moon = Moon(left)
            games.screen.add(moon)
            left = moon.right
        hill = Hill("1-1-2", 150, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(1, 227, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 700, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(1, 777, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-1", 975, Moon.all[0].top+1, True)
        games.screen.add(hill)
        hill = Hill("1-1-2", 1250, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(2, 1750, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 2147, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(1, 2224, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(1, 2324, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 2700, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(1, 2777, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(1, 2867, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 3257, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(4, 3344, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(4, 3444, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", Moon.all[-1].right-47, Moon.all[0].top+4, False)
        games.screen.add(hill)

        elevator = HElevator("red", 2050, 446, 0, 600)
        games.screen.add(elevator)
        button = Button(self, elevator, "red", 975, Moon.all[0].top-49)
        games.screen.add(button)

        robot = Robot(self, 400, Moon.all[0].top+1, 250, 155)
        games.screen.add(robot)
        robot = Robot(self, 950, Moon.all[0].top+1, 250, 155)
        games.screen.add(robot)
        robot = Robot(self, 2587, Moon.all[0].top+1, 60, 233)
        games.screen.add(robot)
        robot = Robot(self, 3097, Moon.all[0].top+1, 110, 200)
        games.screen.add(robot)
        robot = Robot(self, 3664, Moon.all[0].top+1, 120, 180)
        games.screen.add(robot)

        self.man = Man(self, Moon.all[0].top+1)
        games.screen.add(self.man)

        end_piece = End_piece(self, Moon.all[-1].right-50, Moon.all[-1].top-60)
        games.screen.add(end_piece)

    def level3(self):
        # patrol distance below: 350
        # patrol distance above: 400
        games.screen.clear()
        self.display_info()
        left = 0
        for i in range(2):
            moon = Moon(left)
            games.screen.add(moon)
            left = moon.right
        hill = Hill("4-1-2", 300, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("2-4-1", 675, Moon.all[0].top+1, True)
        games.screen.add(hill)
        hill = Hill("3-1-2", 1000, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("2-1-2", 1000, hill.top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 1000, hill.top+4, False)
        games.screen.add(hill)
        hill = Hill("1-3-2", 1550, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 1744, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-2-3", 1647, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(4, 1831, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(4, 1921, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(4, 2011, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(5, 2344, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 2591, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 3041, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hole = Hole(5, 3288, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("1-1-2", 3535, Moon.all[0].top+4, False)
        games.screen.add(hill)

        elevator = HElevator("red", 1450, 317, 0, 350)
        games.screen.add(elevator)
        button = Button(self, elevator, "red", 1450, Moon.all[0].top+1)
        games.screen.add(button)
        elevator = HElevator("blue", 2494, 446, 0, 300)
        games.screen.add(elevator)
        button = Button(self, elevator, "blue", 2100, Moon.all[0].top+1)
        games.screen.add(button)
        elevator = HElevator("yellow", 3141, 446, 297, 0, True)
        games.screen.add(elevator)
        button = Button(self, elevator, "yellow", 675, Moon.all[0].top-199)
        games.screen.add(button)
        elevator = HElevator("green", 1000, 267, 0, 175)
        games.screen.add(elevator)
        button = Button(self, elevator, "green", 3041, Moon.all[0].top-49)
        games.screen.add(button)

        robot = Robot(self, 300, Moon.all[0].top-49, 200, 200)
        games.screen.add(robot)
        robot = Robot(self, 675, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 1325, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 2816, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 3760, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)

        self.man = Man(self, Moon.all[0].top+1)
        games.screen.add(self.man)

        end_piece = End_piece(self, Moon.all[-1].right-50, Moon.all[-1].top-10)
        games.screen.add(end_piece)

    def level4(self):
        # patrol distance below: 300
        # patrol distance above: 350
        # patrol distance with 2: 350
        games.screen.clear()
        self.display_info()
        left = 0
        for i in range(2):
            moon = Moon(left)
            games.screen.add(moon)
            left = moon.right
        hill = Hill("1-1-2", 47, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("4-3-1", 900, Moon.all[0].top+1, True)
        games.screen.add(hill)
        left = hill.right + 75
        for i in range(3):
            platform = Platform(self, left, hill.top)
            games.screen.add(platform)
            left = platform.right + 75
            hole = Hole(4, platform.x, Moon.all[0].bottom)
            games.screen.add(hole)
            platform.elevate()
        hill = Hill("3-3-1", 900, hill.top+1, True)
        games.screen.add(hill)
        hill = Hill("4-3-1", 1750, Moon.all[0].top+1, True)
        games.screen.add(hill)
        hill = Hill("3-1-1", 1750, hill.top+1, True)
        games.screen.add(hill)
        hill = Hill("2-1-1", 1750, hill.top+1, True)
        games.screen.add(hill)
        hill = Hill("1-1-1", 1750, hill.top+1, True)
        games.screen.add(hill)
        hole = Hole(5, 2200, Moon.all[0].bottom)
        games.screen.add(hole)
        hole = Hole(5, 2650, Moon.all[0].bottom)
        games.screen.add(hole)
        hill = Hill("5-1-2", 3097, Moon.all[0].top+4, False)
        games.screen.add(hill)
        hill = Hill("1-1-2", 2997, Moon.all[0].top-46, False)
        games.screen.add(hill)

        elevator = VElevator("red", 650, 451, 359, 460)
        games.screen.add(elevator)
        button = Button(self, elevator, "red", 1750, Moon.all[0].top+1)
        games.screen.add(button)
        elevator = HElevator("blue", 1100, 117, 550, 0, True)
        games.screen.add(elevator)
        button = Button(self, elevator, "blue", 1925, Moon.all[0].top-149)
        games.screen.add(button)
        elevator = HElevator("yellow", 2350, 446, 0, 300)
        games.screen.add(elevator)
        button = Button(self, elevator, "yellow", 1975, Moon.all[0].top+1)
        games.screen.add(button)
        elevator = HElevator("green", 2500, 446, 300, 0, True)
        games.screen.add(elevator)
        button = Button(self, elevator, "green", 775, Moon.all[0].top-299)
        games.screen.add(button)

        robot = Robot(self, 272, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 322, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 900, Moon.all[0].top-149, 150, 200)
        games.screen.add(robot)
        robot = Robot(self, 900, Moon.all[0].top-299, 150, 150)
        games.screen.add(robot)
        robot = Robot(self, 3197, Moon.all[0].top-49, 150, 150)
        games.screen.add(robot)
        robot = Robot(self, 3522, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)
        robot = Robot(self, 3572, Moon.all[0].top+1, 175, 175)
        games.screen.add(robot)

        self.man = Man(self, Moon.all[0].top-49)
        games.screen.add(self.man)

        end_piece = End_piece(self, Moon.all[-1].right-50, Moon.all[-1].top-10)
        games.screen.add(end_piece)

def main():
    game = Game()
    games.screen.mainloop()

main()
