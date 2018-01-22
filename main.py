'''
This is a Python 3 + PyGame implementation of javid9x's 2d circle resolution
tutorial part 1.

Programming Balls #1 Circle Vs Circle Collision C++
Link: https://www.youtube.com/watch?v=LPzyNOHY3A4

Credits to javid9x for the maths stuff and algorithms
'''

from game import Game
import pygame as pg
from pygame.math import Vector2
import math
import random


class Ball:
	def __init__(self, pos, radius):
		self.pos = Vector2(pos)
		self.vel = Vector2()
		self.accel = Vector2()
		self.radius = radius
		self.mass = 10 * self.radius
	
	def update(self, time_elapsed):
		self.accel = -self.vel * 0.8
		self.vel += self.accel * time_elapsed
		self.pos += self.vel * time_elapsed

		# clamp velocity
		if self.vel.length() < 0.1:
			self.vel.x, self.vel.y = 0, 0

	def render(self, screen):
		x, y = int(self.pos.x), int(self.pos.y)
		pg.draw.circle(screen, pg.Color('white'), (x, y), self.radius, 1)

		# draw velocity vector
		vx, vy = self.vel.x, self.vel.y
		pg.draw.line(screen, pg.Color('green'), (x, y), (x + vx, y + vy), 1)
	
	def collide_point(self, point):
		distance_vec = self.pos - Vector2(point)
		d = distance_vec.length()
		return d <= self.radius

	def collide_ball(self, ball):
		distance = self.pos - ball.pos
		radius_sum = self.radius + ball.radius
		return (distance.length() ** 2) < (radius_sum ** 2)

	def resolve_static_collision(self, ball):
		distance_vec = self.pos - ball.pos
		radius_sum = self.radius + ball.radius
		distance = distance_vec.length()

		# Calculate interpenetration
		interpen = distance - radius_sum
		
		# Resolve interpenetration
		overlap = interpen / 2
		self.pos -= overlap * distance_vec / distance
		ball.pos += overlap * distance_vec / distance
		'''
		Note: (distance_vec / distance) is actually a normalized vector: d hat
		'''
	
	def resolve_dynamic_collision(self, other):
		b1, b2 = self, other
		distance_vec = self.pos - other.pos
		normal = distance_vec.normalize()
		tangent = Vector2(-normal.y, normal.x)	# rotate normal 90 deg

		# Dot product tangent
		dptan1 = self.vel.dot(tangent)	# proj self.vel to tangent
		dptan2 = other.vel.dot(tangent)	# proj other.vel to tangent

		# Dot product normal
		dpnorm1 = self.vel.dot(normal)
		dpnorm2 = other.vel.dot(normal)
		
		# Conservation of momentum in 1D (wikipedia)
		m1 = (dpnorm1 * (self.mass - other.mass) + 2 * other.mass * dpnorm2) / (self.mass + other.mass)
		m2 = (dpnorm2 * (other.mass - self.mass) + 2 * self.mass * dpnorm1) / (self.mass + other.mass)

		# Update other velocities
		self.vel = tangent * dptan1 + normal * m1
		other.vel = tangent * dptan2 + normal * m2

		'''
		kx = b1.vel.x - b2.vel.x
		ky = b1.vel.y - b2.vel.y
		p = 2 * (normal.x * kx + normal.y * ky) / (b1.mass + b2.mass)
		b1.vel.x = b1.vel.x - p * b2.mass * normal.x
		b1.vel.y = b1.vel.y - p * b2.mass * normal.y
		b2.vel.x = b2.vel.x + p * b1.mass * normal.x
		b2.vel.y = b2.vel.y + p * b1.mass * normal.y
		'''


	def __repr__(self):
		return 'Ball p={me.pos} r={me.radius} m={me.mass} v={me.vel} a={me.accel}'.format(me=self)


class CircleCollisionGame(Game):
	def __init__(self,):
		super().__init__(title='Circle collisions')
		self.balls = list()

		self.RADIUS_RANGE = (20, 50)
		self.NUM_BALLS = 10

		self.selected_ball = None
		self._add_balls(self.NUM_BALLS)

		self._mouse_buttons_held = [False, False, False]

		self._collided_balls = []

	
	def _add_balls(self, quantity):
		for x in range(quantity):
			radius = random.randint(*self.RADIUS_RANGE)
			x = random.randint(0, self.SCREEN_WIDTH)
			y = random.randint(0, self.SCREEN_HEIGHT)
			self.balls.append(Ball((x, y), radius))


	def update(self, time_elapsed):
		for ball in self.balls:
			ball.update(time_elapsed)

		for ball in self.balls:
			for target in self.balls:
				if ball == target:
					continue
				collided = ball.collide_ball(target)
				if collided:
					# Resolve collisions right away so we don't get extra copies on the list
					''''
					This has been cause of my 2 hour misery ; - ;. I was getting extra 
					copies on the list: (ball, target) and (target, ball) because I don't
					resolve them right away. This resulted in the dynamic collision
					resolution loop calculating the resolution two times on the same pair and 
					thus overriding the correct velocity (during collision) by a new value
					(after collision) when they already separted. The second dynamic 
					collision resolution turns the velocities of one of the objects to ZERO).

					Lesson:
					-------
					Don't try to do your own thing while following the tutorial!
					'''
					self._collided_balls.append([ball, target])
					ball.resolve_static_collision(target)

		# Part of 2 hour misery:
		'''
		for ball, target in self._collided_balls:
			ball.resolve_static_collision(target)
		'''

		for ball, target in self._collided_balls:
			ball.resolve_dynamic_collision(target)

		self._wrap_balls()
	
	def _wrap_balls(self):
		for ball in self.balls:
			if ball.pos.x > self.SCREEN_WIDTH:
				ball.pos.x = 0
			elif ball.pos.x < 0:
				ball.pos.x = self.SCREEN_WIDTH
			
			if ball.pos.y > self.SCREEN_HEIGHT:
				ball.pos.y = 0
			elif ball.pos.y < 0:
				ball.pos.y = self.SCREEN_HEIGHT

	def render(self, surface):
		for ball in self.balls:
			ball.render(surface)

		# Draw red line between colliding balls
		for i, (ball, target) in enumerate(self._collided_balls):
			pg.draw.line(surface, pg.Color('red'), ball.pos, target.pos)

		# Finally, clear _collided_balls
		self._collided_balls = []

		self._render_cue(surface)
	
	def _render_cue(self, surface):
		if self.selected_ball and self._mouse_buttons_held[2]:
			pg.draw.line(surface, pg.Color('blue'), self.selected_ball.pos, pg.mouse.get_pos())
	
	def handle_event(self, event):
		if event.type == pg.MOUSEBUTTONDOWN: 
			self._mouse_buttons_held[event.button - 1] = True

			if event.button == 1:
				for ball in self.balls:
					collided = ball.collide_point(event.pos)
					if collided:
						self.selected_ball = ball
						print('selected:', self.selected_ball)
						break

		elif event.type == pg.MOUSEBUTTONUP:
			self._mouse_buttons_held[event.button - 1] = False

			# Apply velocity to selected ball
			if event.button == 3:
				if self.selected_ball:
					self.selected_ball.vel += (self.selected_ball.pos - event.pos)


		elif event.type == pg.MOUSEMOTION:
			# Drag the ball around
			if self._mouse_buttons_held[0]:
				if self.selected_ball is not None:
					if self.selected_ball.collide_point(event.pos):
						self.selected_ball.pos = Vector2(event.pos)

			
def main():
	CircleCollisionGame().start()


if __name__ == '__main__':
	main()
