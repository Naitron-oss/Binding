from pygame import *
from random import randint
from math import *
from const import GRATIO
from UIHeart import *
from Tear import *
from Fire import *
from Coin import *
from Key import *
from Pickup import *
from Heart import *
from Bomb import *
from Item import *
from Pill import *
from Trapdoor import *
from Banner import *

class Character:
	"""The main class for Isaac"""

	hurtDistance = .6

	def __init__(self, variant, xy, keys, textures, sounds, fonts):
		self.variant = variant
		self.x, self.y = xy
		self.textures = textures["character"][variant]

		self.tearTextures = textures["tears"]
		self.tearSounds = sounds["tear"]
		self.heartTextures = textures["hearts"]

		self.sounds = sounds["hurt"]

		self.dead = False
		self.isFlying = False
		self.pill = None
		self.lastHurt = -1

		self.tears = []
		self.hearts = [UIHeart(0, 2, textures["hearts"]) for i in range(3)]

		self.heads = [self.textures.subsurface(Rect((i*64)*2, 0, 64, 64)) for i in range(3)]
		self.heads.append(transform.flip(self.heads[1], True, False))

		self.tearHeads = [self.textures.subsurface(Rect(64+(i*64)*2, 0, 64, 64)) for i in range(3)]
		self.tearHeads.append(transform.flip(self.tearHeads[1], True, False))

		self.feet = [
			[self.textures.subsurface(Rect((i*64), 64, 64, 64)) for i in range(8)],
			[self.textures.subsurface(Rect((i*64), 64*2, 64, 64)) for i in range(8)],
			[],
			[]
		]

		self.bodyRect = Rect(self.x-16, self.y-16, 32, 32)

		self.pickups = [Pickup(i, textures["pickups"], fonts["pickups"]) for i in range(3)] # Keys, Bombs, Coins

		self.pickups[0].score += 5
		self.pickups[0].updateDigits()

		for frame in self.feet[0]:
			self.feet[2].append(frame)

		for frame in self.feet[1]:
			self.feet[3].append(transform.flip(frame, True, False))

		self.head = self.heads[0]
		self.body = self.feet[0][0]


		self.specialFrames = [self.textures.subsurface(i*128, 272+128, 128, 128) for i in range(1, 3)]
		self.specialFrame = 0

		self.lastPickup = 0

		# Animation setup
		self.interval = .06
		self.lastAnimate = 0
		self.walking = False
		self.eyesOpen = True
		self.walkIndex = 0
		self.lastTear = 0
		
		# Velocity
		self.xVel = 0
		self.yVel = 0

		# Direction
		self.up = False
		self.down = False
		self.left = False
		self.right = False
		self.lastKey = 0
		self.lastTearKey = 0

		self.lastKeys = []
		self.lastTearKeys = []

		# Keys
		self.moveKeys = keys[0]
		self.tearKeys = keys[1]

		# Stats
		self.speed = 2
		self.shotRate = 1
		self.damage = 2
		self.range = 2
		self.shotSpeed = 1
		self.luck = 1

		self.items = []

	def heal(self, ammount, variant):
		if not self.dead:
			starting = -1
			heartCount = len(self.hearts)
			for i in range(heartCount):
				if self.hearts[i].variant == variant:
					starting = i
					break

			if starting == -1:
				return 2

			leftover = self.hearts[starting].add(ammount)
			for i in range(starting, heartCount):	
				if leftover <= 0:
					break
				else:
					heart = self.hearts[i]
					leftover = heart.add(leftover)

					if leftover != 0 and variant != 0 and (i == heartCount-1 or self.hearts[i+1].variant != variant): 
							return leftover

			return True

	def clearTears(self):
		self.tears = []

	def hurt(self, ammount, enemyX, enemyY, time):

		if time-self.lastHurt < 1:
			return

		self.sounds[randint(0,1)].play() # Play random hurt sound

		leftover = self.hearts[-1].damage(1)
		for i in range(len(self.hearts)-1, -1, -1):
			if type(leftover) == bool and leftover:
				del self.hearts[i]
				break
			else:
				if leftover <= 0:
					break
				else:
					if i == 0 and self.hearts[i].health == 1:
						self.dead = True
					leftover = self.hearts[i].damage(leftover)

		# Isaac push back
		if enemyX != None and enemyY != None:
			dx, dy = ((enemyX-self.x)*-1, (enemyY-self.y)*-1)
			angle = atan2(dy, dx)

			pConst = 2

			self.xVel += pConst*cos(angle)
			self.yVel += pConst*sin(angle)

		self.lastHurt = time

		self.specialFrame = 2

		if self.hearts[0].health == 0:
			self.die()

	def usePill(self):
		if self.pill != None:
			self.pill.use(self) # Pass in the character to check for PHD
			st = self.pill.stats # The pills statss
			types = ["Speed", "Tears", "Damage", "Range", "Shot Speed", "Luck"]
			if sum(st) == -1:
				self.game.banners.append(Banner(types[st.index(-1)] + " Down", self.game.textures))
			else:
				self.game.banners.append(Banner(types[st.index(1)] + " Up", self.game.textures))
			self.speed += st[0]
			self.shotRate += st[1]
			self.damage += st[2]
			self.range += st[3]
			self.shotSpeed += st[4]
			self.luck += st[5]
			
			self.pill = None

	def die(self):
		self.dead = True

	def updateVel(self):

		if self.up:
			self.yVel += -0.15

		if self.down:
			self.yVel += 0.15

		if self.left:
			self.xVel += -0.15

		if self.right:
			self.xVel += 0.15

		if (not self.left) and (not self.right) or (self.left and self.right):
			self.xVel *= 0.85

		if (not self.up) and (not self.down) or (self.up and self.down):
			self.yVel *= 0.85

		if abs(self.xVel) > 1:
			self.xVel = 1 if self.xVel > 0 else -1

		if abs(self.yVel) > 1:
			self.yVel = 1 if self.yVel > 0 else -1

		if self.xVel == 0 and self.yVel == 0:
			self.head = self.heads[0]

	def moving(self, key, value, joystick):
		if joystick:
			jValue = value

			value = abs(jValue) > .7

			if key == 0:
				# X change
				if jValue >= 0:
					# Right
					index = 1
				else:
					# Left
					index = 3

			elif key == 1:
				# Y change

				if jValue >= 0:
					# Up
					index = 0
				else:
					index = 2

			elif key == 2:
				# X change
				if jValue >= 0:
					# Right
					index = 1
				else:
					# Left
					index = 3

				try:
					if value:
						self.lastTearKey = index
						self.lastTearKeys.append(index)
					else:
						self.lastTearKeys.remove(index)
				except:
					pass
				return
			elif key == 3:
				# Y change

				if jValue >= 0:
					# Up
					index = 0
				else:
					index = 2
				try:
					if value:
						self.lastTearKey = index
						self.lastTearKeys.append(index)
					else:
						self.lastTearKeys.remove(index)
				except:
					pass
				return


		else:
			try:
				index = self.moveKeys.index(key)
			except:
				try:
					index = self.tearKeys.index(key)
					if value:
						self.lastTearKey = index
						self.lastTearKeys.append(index)
					else:
						self.lastTearKeys.remove(index)
				except:
					pass
				return

		if index == 0:
			self.down = value
		elif index == 1:
			self.right = value
		elif index == 2:
			self.up = value
		elif index == 3:
			self.left = value

		if value:
			self.lastKey = index
			self.lastKeys.append(index)
		else:
			try:
				self.lastKeys.remove(index)
			except:
				pass

		if len(self.lastKeys) > 0:
			self.head = self.heads[self.lastKeys[-1]]
		else:
			self.head = self.heads[0]

		if len(self.lastTearKeys) > 0:
			self.head = self.heads[self.lastTearKeys[-1]]

	def step(self, time):
		xVel = round(abs(self.xVel), 1)
		yVel = round(abs(self.yVel), 1)

		if xVel > 0.1 or yVel > 0.1:

			if all([not self.down, not self.right, not self.up, not self.left]):
				# No keys are down

				self.head = self.heads[0]

			if len(self.lastKeys) > 0:
				self.body = self.feet[self.lastKeys[-1]][int(self.walkIndex)]
			else:
				self.body = self.feet[self.lastKey][int(self.walkIndex)]

			self.walkIndex += 1


			if self.walkIndex >= len(self.feet[0]):
				self.walkIndex = 0
		else:
			self.walkIndex = 0
			self.head = self.heads[0]
			self.body = self.feet[0][0]

		if len(self.lastKeys) > 0 and (xVel > 0.1 or yVel > 0.1):
			self.head = self.heads[self.lastKeys[-1]]
			self.body = self.feet[self.lastKeys[-1]][int(self.walkIndex)]
		else:
			self.head = self.heads[0]

		if len(self.lastTearKeys) > 0:
			self.head = self.heads[self.lastTearKeys[-1]]


	def render(self, surface, time, bounds, obsticals, doors):
		move = [0,0] # Which direction on the map to move

		if time-self.lastAnimate >= self.interval:
			self.lastAnimate = time
			self.step(time)

		if self.specialFrame == 2 and time-self.lastHurt >= 0.22:
			self.specialFrame = 0
		elif self.specialFrame == 1 and time-self.lastPickup >= 0.5:
			self.specialFrame = 0


		if self.lastTearKey in self.lastTearKeys and time-self.lastTear >= (8-self.shotRate)/18:
			self.tears.append(Tear([(0, 1), (1, 0), (0, -1), (-1, 0)][self.lastTearKey], (self.x, self.y-20), (self.xVel*1.5, self.yVel*1.5), self.shotSpeed, self.damage, self.range, True, self.tearTextures, self.tearSounds))
			self.lastTear = time
		elif time-self.lastTear <= 0.1:
			try:
				self.head = self.tearHeads[self.heads.index(self.head)]
			except:
				pass
		else:
			try:
				self.head = self.heads[self.tearHeads.index(self.head)]
			except:
				pass

		sizeModifier = 2.5

		if sum(map(int, [self.left, self.right, self.up, self.down])) > 1:
			sizeModifier /= 1.414213 # So there is no benefit to going diagonal (sqrt(2))

		dx = self.xVel * sizeModifier * self.speed
		dy = self.yVel * sizeModifier * self.speed

		inBoundsX = bounds.collidepoint(self.x+dx, self.y)
		inBoundsY = bounds.collidepoint(self.x, self.y+dy)

		rockColX = False
		rockColY = False

		for ob in obsticals:
			# Collide with ob
			try:
				if ob.destroyed:
					continue
			except:
				pass

			rcx = ob.bounds.collidepoint(self.x+dx, self.y)
			rcy = ob.bounds.collidepoint(self.x, self.y+dy)
			if rcx:
				rockColX = rcx
			if rcy:
				rockColY = rcy
			if rcx or rcy:
				if type(ob) == Fire:
					self.hurt(1, None, None, time)
				elif type(ob) == Coin:
					self.pickups[0].add(ob.worth)
					ob.pickup()
				elif type(ob) == Key:
					if self.pickups[0].use(ob.price):
						self.pickups[2].add(1)
						ob.pickup()
				elif type(ob) == Bomb and not ob.shouldExplode:
					if self.pickups[0].use(ob.price):
						self.pickups[1].add(1)
						ob.pickup()
				elif type(ob) == Heart:
					if self.pickups[0].use(ob.price):
						amm = self.heal(ob.health, ob.variant)
						if amm == 0:
							self.hearts.append(UIHeart(ob.variant, ob.health, self.heartTextures))
						elif type(amm) == int:
							self.hearts.append(UIHeart(ob.variant, amm, self.heartTextures))
						ob.pickup()

						if ob.variant == 1: # Sould heart
							self.specialFrame = 1
							self.lastPickup = time
				elif type(ob) == Pill:
					if self.pickups[0].use(ob.price):
						self.pill = ob
						ob.pickup()
				elif type(ob) == PHD:
					if self.pickups[0].use(ob.price):
						self.items.append(ob)
						ob.pickup()
				elif type(ob) == Trapdoor:
					self.game.floorIndex += 1
					self.game.currentRoom = (0,0)
					self.game.setup()
					self.game.updateFloor()
				elif type(ob) == Item:
					# ADD EM UP HERE
					print("picked up that dank item")

				if not ob.collideable and not rockColX and not rockColY:
					rockColX = rockColY = False

		mx = [0, 1, 0, -1]
		my = [-1, 0, 1, 0]

		for i in range(len(doors)):
			door = doors[i]

			if not door.isOpen:
				continue

			dcx = door.rect.collidepoint(self.x+dx, self.y)
			dcy = door.rect.collidepoint(self.x, self.y+dy)

			if len(doors) == 1 and door.locked:
				door.locked = False


			if door.locked and self.pickups[2].score > 0 and (dcx or dcy):
				door.locked = False
				self.pickups[2].score -= 1
				continue

			if door.locked:
				continue

			if dcx:
				self.x += dx

			if dcy:
				self.y += dy

			side = door.side

			if not dcx or not dcy:
				if sum(map(int, [
						mx[side] < 0 and door.rect.x-(self.x+dx) > 0,
						mx[side] > 0 and door.rect.x+door.rect.w-(self.x+dx) < 0,
						my[side] > 0 and door.rect.y-(self.y+dy) > 0,
						my[side] < 0 and door.rect.y+door.rect.h-(self.y+dy) < 0,
					])) == 1:
					move[0] = mx[side]
					move[1] = my[side]
					break



		self.x += dx if	inBoundsX and (not rockColX or self.isFlying) else 0
		self.y += dy if inBoundsY and (not rockColY or self.isFlying) else 0

		self.bodyRect = Rect(self.x-16, self.y, 32, 16) # Move body rect

		self.updateVel()
		
		if self.specialFrame == 0:
			surface.blit(self.body, (self.x-32, self.y-32))
			surface.blit(self.head, (self.x-32, self.y-32-20))
		else:
			surface.blit(self.specialFrames[self.specialFrame-1], (self.x-64, self.y-72))

		for tear in self.tears[:]:
			if not tear.render(surface, time, bounds, obsticals):
				self.tears.remove(tear)


		for i in range(len(self.hearts)):
			self.hearts[i].render(surface, i)

		for p in self.pickups:
			p.render(surface)

		if self.pill != None:
			surface.blit(self.pill.texture, (WIDTH-80, HEIGHT-60))

		for item in self.items:
			item.renderCorner(surface)

		# draw.rect(surface, (255,0,0), self.bodyRect)

		# for r in self.doorRects:
		# 	draw.rect(surface, (255,0,0), r)

		# surface.set_at((int(self.x+dx), int(self.y+dy)), (0,255,0))

		return move
