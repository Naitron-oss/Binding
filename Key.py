from pygame import *
from const import *
from Animation import *

class Key:
	"""Pickup Key class"""

	def __init__(self, variant, xy, sounds, textures):
		self.variant = variant
		self.x = xy[0]
		self.y = xy[1]
		self.sounds = sounds
		self.textures = textures

		self.bounds = Rect(GRIDX+GRATIO*self.x,GRIDY+GRATIO*self.y, 32, 64)

		self.texture = self.textures.subsurface(0,0,32,64)

		self.collideable = False
		self.pickedUp = False

	def pickup(self):
		self.pickedUp = True
		self.sounds[1].play()

	def render(self, surface, time, ox=0, oy=0):
		if not self.pickedUp:
			# draw.rect(surface, (255,0,0), self.bounds)
			surface.blit(self.texture, (GRIDX+GRATIO*self.x+ox,GRIDY+GRATIO*self.y+oy))
		return not self.pickedUp