import neat.config
import pygame
import os
import random
import neat

AI_PLAYING = True
GENERATION = 0

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'gameImages', 'pipe.png')))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'gameImages', 'base.png')))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'gameImages', 'bg.png')))
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'gameImages', f'bird{i+1}.png'))) for i in range(3)]

pygame.font.init()
SCORE_FONT = pygame.font.SysFont('04b_19', 35)
pygame.display.set_caption('Flappy Bird NEAT')
icon = pygame.image.load(os.path.join('assets', 'icon', f'bird.png'))
pygame.display.set_icon(icon)


class Bird:
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y, ):
        self.x = x
        self.y = y
        self.rotation = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMAGES[0]

    def flap(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        moving = 1.5 * (self.time**2) + self.speed * self.time

        if moving > 16:
            moving = 16
        elif moving < 0:
            moving -= 2

        self.y += moving

        if moving < 0 or self.y < (self.height + 50):
            if self.rotation < self.MAX_ROTATION:
                self.rotation = self.MAX_ROTATION
        else:
            if self.rotation > -90:
                self.rotation -= self.MAX_ROTATION

    def draw(self, screen):
        self.image_count += 1

        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME*2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME*3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME*4:
            self.image = self.IMAGES[1]
        elif self.image_count >= self.ANIMATION_TIME*4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0

        if self.rotation <= -80:
            self.image = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        image_center_pos = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=image_center_pos)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.bottom_pos = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BOTTOM_PIPE = PIPE_IMAGE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bottom_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE,  (self.x, self.top_pos))
        screen.blit(self.BOTTOM_PIPE, (self.x, self.bottom_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

        top_distance = (self.x - bird.x, self.top_pos - round(bird.y))
        bottom_distance = (self.x - bird.x, self.bottom_pos - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_distance)

        if top_point or bottom_point:
            return True
        else:
            return False
            

class Base:
    SPEED = 5
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))


def draw_screen(screen, birds, pipes, base, score):
    screen.blit(BG_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = SCORE_FONT.render(f'Score: {score}', 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    if AI_PLAYING:
        text = SCORE_FONT.render(f'Generation: {GENERATION}', 1, (255, 255, 255))
        screen.blit(text, (10, 10))


    base.draw(screen)
    pygame.display.update()


def main(genomes, config):
    global GENERATION
    GENERATION += 1

    if AI_PLAYING:
        networks = []
        genomes_list = []
        birds = []
        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            networks.append(network)
            genome.fitness = 0
            genomes_list.append(genome)
            birds.append(Bird(230, 350))

    else:
        birds = [Bird(230, 350)]
    
    base = Base(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    running = True

    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if not AI_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.flap()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
            pass
        else:
            running = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            genomes_list[i].fitness = 0.1
            output = networks[i].activate((bird.y, 
                                           abs(bird.y - pipes[pipe_index].height), 
                                           abs(bird.y - pipes[pipe_index].bottom_pos)))
            if output[0] > 0.5:
                bird.flap()
        base.move()

        spawn_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if AI_PLAYING:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        networks.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    spawn_pipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if spawn_pipe:
            score += 1
            pipes.append(Pipe(600))
            for genome in genomes_list:
                genome.fitness += 5
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > base.y or bird.y < 0:
                birds.pop(i)
                if AI_PLAYING:
                    genomes_list.pop(i)
                    networks.pop(i)

        draw_screen(screen, birds, pipes, base, score)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    max_generations = 50
    if AI_PLAYING:
        population.run(main, max_generations)
    else:
        main(None, None)


if __name__ == '__main__':
    config_path = 'config.txt'
    run(config_path)

