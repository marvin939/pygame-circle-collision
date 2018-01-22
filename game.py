import pygame as pg
import sys


class Game:
	def __init__(self, screen_size=(640, 480), title='GENERIC GAME', fps=60):
		self.SCREEN_WIDTH = screen_size[0]
		self.SCREEN_HEIGHT = screen_size[1]
		self.SCREEN_SIZE = tuple(screen_size)

		self.BG_COLOR = pg.Color('black')

		self.FPS = fps

		self.TITLE = title
		self.screen = None
		self.clock = pg.time.Clock()

	def _create_screen(self, size, title):
		screen = pg.display.set_mode(self.SCREEN_SIZE)
		pg.display.set_caption(title)
		return screen

	def start(self):
		self._playing = True
		self.screen = self._create_screen(self.SCREEN_SIZE, self.TITLE)

		while self._playing:
			for event in pg.event.get():
				self.handle_event(event)
				self._handle_event(event)

			seconds_passed = self.clock.tick(self.FPS) / 1000
			self.update(seconds_passed)
			self.screen.fill(self.BG_COLOR)
			self.render(self.screen)
			pg.display.update()

		self.quit()
	
	def update(self, time_elapsed):
		return
	
	def render(self, surface):
		return

	def handle_event(self, event):
		return
	
	def _handle_event(self, event):
		if event.type == pg.QUIT:
			self._playing = False
	
	def quit(self):
		pg.quit()
		sys.exit()


if __name__ == '__main__':
	Game().start()
