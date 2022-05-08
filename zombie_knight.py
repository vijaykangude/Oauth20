from json import load
import pygame, random

#use 2D vector
vector = pygame.math.Vector2 

#Initialize pygame
pygame.init()

#Sety display surface (tile size is 32x32 so 1280/32 = 40 tiles wide, 736/32 = 23 tiles high)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 716
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zombie Knight")

#Set FPS and clock
FPS = 60
clock = pygame.time.Clock()


#Define classes
class Game():
    """A class to help manage gameplay"""

    def __init__(self, player, zombie_group, platform_group, portal_group, bullet_group, ruby_group):
        """Initialize the game"""
        #Set constant variables
        self.STARTING_ROUND_TIME = 30
        self.STARTING_ZOMBIE_CREATION_TIME = 5

        #Set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        #Set fonts
        self.title_font = pygame.font.Font("fonts/Poultrygeist.ttf", 48)
        self.HUD_font = pygame.font.Font("fonts/Pixel.ttf", 24)

        #Set sounds
        self.lost_ruby_sound = pygame.mixer.Sound("sounds/lost_ruby.wav")
        self.ruby_pickup_sound = pygame.mixer.Sound("sounds/ruby_pickup.wav")
        pygame.mixer.music.load("sounds/level_music.wav")

        #Attach groups and sprites
        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group

    def update(self):
        """Update the game"""
        #Update the round time every second
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0
        
        self.check_collisions()
        self.add_zombie()
        self.check_round_completion()
        self.check_game_over()


    def draw(self):
        """Draw the game HUD"""
        #Set colors
        WHITE = (255, 255, 255)
        GREEN = (25, 200, 25)

        #Set text
        score_text = self.HUD_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(self.player.health), True, WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render("Zombie Knight", True, GREEN)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 25)

        round_text = self.HUD_font.render("Night: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render("Sunrise In: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        #Draw the HUD
        display_surface.blit(score_text, score_rect)
        display_surface.blit(health_text, health_rect)
        display_surface.blit(title_text, title_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(time_text, time_rect)
        

    def add_zombie(self):
        """Add a zombie to the game"""
        #Check to add a zombie every second
        # if self.frame_count % FPS == 0:
            #Only add a zombie if zombie creation time has passed
            # if self.round_time % self.zombie_creation_time == 0:
            #     zombie = Zombie(self.platform_group, self.portal_group, self.round_number, 5 + self.round_number)
            #     self.zombie_group.add(zombie)


    def check_collisions(self):
        """Check collisions that affect gameplay"""
        #See if any bullet in the bullet group hit a zombie in the zombie group
        collision_dict = pygame.sprite.groupcollide(self.bullet_group, self.zombie_group, True, False)
        if collision_dict:
            for zombies in collision_dict.values():
                for zombie in zombies:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True
        
        #See if a player stomped a dead zombie to finish it or collided with a live zombie to take damage
        collision_list = pygame.sprite.spritecollide(self.player, self.zombie_group, False)
        if collision_list:
            for zombie in collision_list:
                #The zombie is dead; stomp it
                if zombie.is_dead == True:
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 25

                    ruby = Ruby(self.platform_group, self.portal_group)
                    self.ruby_group.add(ruby)
                #The zombie isn't dead, so take damage
                else:
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    #Move the player to not continually take damage
                    self.player.position.x -= 256*zombie.direction
                    self.player.rect.bottomleft = self.player.position

        #See if a player collided with a ruby
        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.ruby_pickup_sound.play()
            self.score += 100
            self.player.health += 10
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH

        #See if a living zombie collided with a ruby
        for zombie in self.zombie_group:
            if zombie.is_dead == False:
                if pygame.sprite.spritecollide(zombie, self.ruby_group, True):
                    self.lost_ruby_sound.play()
                    zombie = Zombie(self.platform_group, self.portal_group, self.round_number, 5 + self.round_number)
                    self.zombie_group.add(zombie)

    def check_round_completion(self):
        """Check if the player survive a single night"""
        if self.round_time == 0:
            self.start_new_round()

    def check_game_over(self):
        """Check to see if the player lost the game"""
        pass

    def start_new_round(self):
        """Start a new night"""
        self.round_number += 1

        #Decrease zombie creation time
        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1
        
        #Reset round valus
        self.round_time = self.STARTING_ROUND_TIME

        self.zombie_group.empty()
        self.ruby_group.empty()
        self.ruby_group.empty()

        self.player.reset()
        self.pause_game("You survived the night!", "Press 'Enter' to continue...")



    def pause_game(self, main_text, sub_text):
        """Pause the game"""
        global running

        pygame.mixer.music.pause()

        #Set Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (25, 200, 25)

        #Create main pause text
        main_text = self.title_font.render(main_text, True, GREEN)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

        #Create sub pause text
        sub_text = self.title_font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64)

        #Display the pause text
        display_surface.fill(BLACK)
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        #Pause the game until user hits the enter
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #User wants to continue
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                        pygame.mixer.music.unpause()
                #User wants to quit
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False
                    pygame.mixer.music.stop()


    def reset_gamea(self):
        """Reset the game"""
        pass


class Tile(pygame.sprite.Sprite):
    """A class to represent a 32x32 pixel area in our display"""

    def __init__(self, x, y, image_int, main_group, sub_group=""):
        """Initialize the tile"""
        super().__init__()
        #Load in ther correct image and add it to the correct sub group
        #Dirt
        if image_int == 1:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (1).png"), (32, 32))
        #platform tiles
        elif image_int == 2:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (2).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 3:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (3).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 4:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (4).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 5:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (5).png"), (32, 32))
            sub_group.add(self)
        
        #Add every tile to the main group
        main_group.add(self)

        #Get the rect of the image and position whithin the grid
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Player(pygame.sprite.Sprite):
    """A class the user can control"""

    def __init__(self, x, y, platform_group, portal_geroup, bullet_group):
        """Initialize the player"""
        super().__init__()

        #Set constant variables
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = 0.15
        self.VERTICAL_ACCELERATION = 0.8 #Gravity
        self.VERTICAL_JUMP_SPEED = 18 #Determines how high the player can jump
        self.STARTING_HEALTH = 100

        #Animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []


        #Moving
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (1).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (2).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (3).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (4).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (5).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (6).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (7).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (8).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (9).png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (10).png"), (64, 64)))
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))
        
        #Idling
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (1).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (2).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (3).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (4).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (5).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (6).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (7).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (8).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (9).png"), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (10).png"), (64, 64)))
        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))
        
        #Jumping
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (1).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (2).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (3).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (4).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (5).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (6).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (7).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (8).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (9).png"), (64, 64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (10).png"), (64, 64)))
        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Attacking
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (1).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (2).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (3).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (4).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (5).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (6).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (7).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (8).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (9).png"), (64, 64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (10).png"), (64, 64)))
        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Load image and get rect
        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #Attach sprite groups
        self.platform_group = platform_group
        self.platform_group = portal_geroup
        self.bullet_group = bullet_group

        #Animation booleans
        self.animate_jump = False
        self.animate_fire = False

        #Load sounds
        self.jump_sound = pygame.mixer.Sound("sounds/jump_sound.wav")
        self.slash_sound = pygame.mixer.Sound("sounds/slash_sound.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/player_hit.wav")

        #Kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        #Set initial player values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y


    def update(self):
        """Update the player"""
        pass

    def move(self):
        """Move the player"""
        pass

    def check_collision(self):
        """Check for collision with platforms and portals"""
        pass

    def check_animations(self):
        """Check to see if jump/fire ankimation should run"""
        pass

    def jump(self):
        """Jump upwards if on a platform"""
        pass

    def fire (self):
        """Fire a sword"""
        pass

    def reset(self):
        """Reset the player position"""
        pass

    def animate(self):
        """Animate the player actions"""
        pass


class Bullet(pygame.sprite.Sprite):
    """A projectile launched by the player"""

    def __init__(self):
        """Initialize the bullet"""
        pass

    def update(self):
        """Update the bullet"""
        pass


class Zombie(pygame.sprite.Sprite):
    """An enemy that move across the screen"""

    def __init__(self):
        """Initialize the zombie"""
        pass 
    
    def update(self):
        """Update the zombie"""
        pass

    def move(self):
        """Move the zombie"""
        pass

    def check_collision(self):
        """Check for collision with platforms and portals"""
        pass

    def check_animations(self):
        """Check to see if death/rise ankimation should run"""
        pass

    def animate(self):
        """Animate the zombie actions"""
        pass


class RubyMaker(pygame.sprite.Sprite):
    """A tile that is animated. A ruby will be generated here."""

    def __init__(self, x, y, main_group):
        """Initialize the ruby maker"""
        super().__init__()
        
        #Animation frames
        self.ruby_sprites = []

        #Rotating
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile006.png"), (64, 64)))
        

        #Load image and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #Add to the main group for drawing purposes
        main_group.add(self)


    def update(self):
        """Update the ruby maker"""
        self.animate(self.ruby_sprites, .25)

    def animate(self, sprite_list, speed):
        """Animate the ruby maker"""
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


class Ruby(pygame.sprite.Sprite):
    """A class the player must collect  to earn points and health"""

    def __init__(self):
        """Initialize the ruby"""
        pass

    def update(self):
        """Update the ruby"""
        pass

    def move(self):
        """Move the ruby"""
        pass

    def check_collision(self):
        """Check for collisions with platforms and portals"""
        pass

    def animate(self):
        """Animate the ruby"""
        pass


class Portal(pygame.sprite.Sprite):
    """A class that if collided with will transport you"""
    
    def __init__(self, x, y, color, portal_group):
        """Initialize the portal"""
        super().__init__()

        #Animation frames
        self.portal_sprites = []

        #Portal animation
        if color == "green":
            #Green portal
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile000.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile001.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile002.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile003.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile004.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile005.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile006.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile007.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile008.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile009.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile010.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile011.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile012.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile013.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile014.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile015.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile016.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile017.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile018.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile019.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile020.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile021.png"),(72, 72)))
        else:
            #Purple portal
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile000.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile001.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile002.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile003.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile004.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile005.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile006.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile007.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile008.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile009.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile010.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile011.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile012.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile013.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile014.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile015.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile016.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile017.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile018.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile019.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile020.png"),(72, 72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile021.png"),(72, 72)))

        #Load an image and get a rect
        self.current_sprite = random.randint(0, len(self.portal_sprites)-1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y) 

        #Add to the portal group
        portal_group.add(self)

    def update(self):
        """Update the portal"""
        self.animate(self.portal_sprites, .2)
    
    def animate(self, sprite_list, speed):
        """Animate the portal"""
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]
        



#Create Sprite groups
my_main_tile_group = pygame.sprite.Group()
my_platform_group = pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_bullet_group = pygame.sprite.Group()

my_zombie_group = pygame.sprite.Group()

my_portal_group = pygame.sprite.Group()
my_ruby_group = pygame.sprite.Group()




#Create the tile map
#0 -> no tile, 1 -> dirt, 2-5 -> platforms, 6 -> ruby maker, 7-8 -> platform, 9 -> player
#23 rows and 40 columns
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

#Genrate Tile objects from the tile map
#Loop through the 23 lists (rows) in the map
for i in range(len(tile_map)):
    #Loop through the 40 elements in a given list (cols) 
    for j in range(len(tile_map[i])):
        #Dirt tile 
        if tile_map[i][j] == 1:
            Tile(j*32, i*32, 1, my_main_tile_group)
        elif tile_map[i][j] == 2:
            Tile(j*32, i*32, 2, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 3:
            Tile(j*32, i*32, 3, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 4:
            Tile(j*32, i*32, 4, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 5:
            Tile(j*32, i*32, 5, my_main_tile_group, my_platform_group)
        #Ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j*32, i*32, my_main_tile_group)
        #Portals
        elif tile_map[i][j] == 7:
            Portal(j*32, i*32, "green", my_portal_group)
        elif tile_map[i][j] == 8:
            Portal(j*32, i*32, "purple", my_portal_group)
        #Player
        elif tile_map[i][j] == 9:
            my_player = Player(j*32, i*32, my_platform_group, my_portal_group, my_bullet_group)
            my_player_group.add(my_player)
        
        


#Load in a background image
background_image = pygame.transform.scale(pygame.image.load("images/background.jpg"), (1280, 736))
background_rect = background_image.get_rect()
background_rect.topleft = (0, 0)


#Create a game
my_game = Game(my_player, my_zombie_group, my_platform_group, my_portal_group, my_bullet_group, my_ruby_group)
my_game.pause_game("Zombie Knight", "Press Enter to begin")
pygame.mixer.music.play(-1, 0.0)

#The main game loop
running = True
while running:
    #Check to see if the user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Blit the background
    display_surface.blit(background_image, background_rect)

    #Draw tiles and update RubyMaker
    my_main_tile_group.update()
    my_main_tile_group.draw(display_surface)

    #Update and draw sprite groups
    my_portal_group.update()
    my_portal_group.draw(display_surface)
    
    
    #Update and draw the game
    my_game.update()
    my_game.draw()

    #update the display and tick the clock
    pygame.display.update()
    clock.tick(FPS)


#End the game
pygame.quit()