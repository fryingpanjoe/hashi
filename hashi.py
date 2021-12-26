import pygame, heapq, random, os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

EDGE_PADDING = 32
EDGE_WIDTH = 4
NODE_RADIUS = 16
NODE_SPACING = 64
NODE_BORDER_WIDTH = 2
BOARD_SIZE = 8

def Kruskal(nodes, weightedEdges):
	C = {}
	#C[(0, 0)] = len(C)
	Q = []
	for (w, e) in weightedEdges:
		heapq.heappush(Q, [w, e])
	nodeCount = len(nodes)
	treeEdges = []
	while len(treeEdges) < nodeCount - 1:
		w, (u, v) = heapq.heappop(Q)
		if v not in C:
			C[v] = len(C)
		if u not in C:
			C[u] = len(C)
		if C[v] != C[u]:
			treeEdges.append((u,v))
			C[u] = C[v]
	return treeEdges

def Prim(nodes, weightedEdges):
	Q = []
	for (w, e) in weightedEdges:
		heapq.heappush(Q, [w, e])
	treeNodes = set()
	treeNodes.add(random.choice(nodes))
	nodeCount = len(nodes)
	treeEdges = []
	while len(treeNodes) < nodeCount:
		P = []
		foundEdge = False
		while not foundEdge:
			w, (u, v) = heapq.heappop(Q)
			if (u not in treeNodes and v in treeNodes) or (u in treeNodes and v not in treeNodes):
				treeNodes.add(u)
				treeNodes.add(v)
				treeEdges.append((u,v))
				foundEdge = True
			else:
				P.append([w, (u, v)])
		for e in P:
			heapq.heappush(Q, e)
	return treeEdges

def NoMinimumSpanningTree(nodes, weightedEdges):
	treeEdges = []
	for (w, e) in weightedEdges:
		treeEdges += [e]
	return treeEdges

def IsHorizontalEdge(e):
	u = e[0]
	v = e[1]
	return u[0] != v[0]

class NumberTextImageCache:
	def __init__(self):
		self.font = pygame.font.Font(None, 36)
		self.surfaces = []
		for i in range(0, 10):
			self.surfaces.append(self.font.render(str(i), True, BLACK))

	def Draw(self, screen, pos, number):
		surface = self.surfaces[number]
		screen.blit(surface, surface.get_rect(center = pos))

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3

class Board:
	def __init__(self):
		self.boardSize = 0
		self.nodes = []
		self.edges = []
		self.nodeEdgeCounts = {}
		self.edgeCounts = {}
		self.possibleEdges = []
		self.userEdges = []
		self.userEdgeCounts = {}
		self.userNodeEdgeCounts = {}
		self.drawPosition = (EDGE_PADDING, EDGE_PADDING)
		self.edgePadding = EDGE_PADDING
		self.nodeRadius = NODE_RADIUS
		self.nodeSpacing = NODE_SPACING
		self.edgeWidth = EDGE_WIDTH
		self.nodeBorderWidth = NODE_BORDER_WIDTH
		self.numberTextCache = NumberTextImageCache()
		self.keyDown = {}
		self.keyPressed = {}
		self.buttonDown = {}
		self.buttonPressed = {}
		self.font = pygame.font.Font(None, 72)
		self.winText = self.font.render('You Won!', True, GREEN)
		self.screenSurface = None

	def SetOptimalScreenMode(self):
		screenWidthHeight = 2 * self.edgePadding + self.nodeSpacing * (self.boardSize - 1)
		screenSize = [screenWidthHeight, screenWidthHeight]
		self.screenSurface = pygame.display.set_mode(screenSize, pygame.DOUBLEBUF)

	def Generate(self, size):
		self.boardSize = size
		while True:
			try:
				self.nodes = []
				for x in range(size):
					for y in range(size):
						if random.random() < 0.8:
							self.nodes.append((x, y))
				weightedEdges = []
				for u in self.nodes:
					if u[0] < size - 1:
						v = (u[0] + 1, u[1])
						if v in self.nodes:
							weightedEdges.append((random.random(), (u, v)))
					if u[1] < size - 1:
						v = (u[0], u[1] + 1)
						if v in self.nodes:
							weightedEdges.append((random.random(), (u, v)))
				#self.edges = NoMinimumSpanningTree(self.nodes, weightedEdges)
				#self.edges = Kruskal(self.nodes, weightedEdges)
				self.edges = Prim(self.nodes, weightedEdges)
				break
			except:
				pass
		for u in self.nodes:
			nodeEdges = [ e for e in self.edges if u in e ]
			if len(nodeEdges) == 2:
				a, b = nodeEdges
				if IsHorizontalEdge(a) == IsHorizontalEdge(b):
					self.nodes.remove(u)
					self.edges.remove(a)
					self.edges.remove(b)
					if u == a[0]:
						c = (b[0], a[1])
					else:
						c = (a[0], b[1])
					self.edges.append(c)
		self.edgeCounts = {}
		for e in self.edges:
			if random.random() < 0.3:
				self.edgeCounts[e] = 2
			else:
				self.edgeCounts[e] = 1
		self.nodeEdgeCounts = {}
		self.possibleEdges = []
		for u in self.nodes:
			edgeCount = 0
			for e in [e for e in self.edges if u in e ]:
				edgeCount += self.edgeCounts[e]
			self.nodeEdgeCounts[u] = edgeCount
			self.userNodeEdgeCounts[u] = 0
			for i in range(u[0] + 1, size):
				v = (i, u[1])
				if v in self.nodes:
					self.possibleEdges.append((u, v))
					break
			for i in range(u[1] + 1, size):
				v = (u[0], i)
				if v in self.nodes:
					self.possibleEdges.append((u, v))
					break

	def GetNodePos(self, u):
		return (self.drawPosition[0] + u[0] * self.nodeSpacing, self.drawPosition[1] + u[1] * self.nodeSpacing)

	def SqDistancePointToEdge(self, p, e):
		(x1, y1) = self.GetNodePos(e[0])
		(x2, y2) = self.GetNodePos(e[1])
		(x3, y3) = p
		dirx = x2 - x1
		diry = y2 - y1
		dirSq = float(dirx * dirx + diry * diry)
		u = ((x3 - x1) * dirx + (y3 - y1) * diry) / dirSq
		u = min(max(0, u), 1)
		px = (x1 + u * dirx)
		py = (y1 + u * diry)
		dx = px - x3
		dy = py - y3
		return dx * dx + dy * dy

	def FindClosestEdge(self, p):
		minDist = 100
		closestEdge = None
		for e in self.possibleEdges:
			d = self.SqDistancePointToEdge(p, e)
			if minDist is None or d < minDist:
				minDist = d
				closestEdge = e
		return closestEdge

	def CanAddUserEdge(self, e):
		u, v = e
		if u in self.userNodeEdgeCounts and self.userNodeEdgeCounts[u] >= self.nodeEdgeCounts[u]:
			return False
		if v in self.userNodeEdgeCounts and self.userNodeEdgeCounts[v] >= self.nodeEdgeCounts[v]:
			return False
		return True

	def CanRemoveUserEdge(self, e):
		return e in self.userEdges

	def AddUserEdge(self, e):
		if e in self.userEdges:
			if self.userEdgeCounts[e] < 2:
				self.userEdgeCounts[e] += 1
				self.userNodeEdgeCounts[e[0]] += 1
				self.userNodeEdgeCounts[e[1]] += 1
		else:
			self.userEdges.append(e)
			self.userEdgeCounts[e] = 1
			self.userNodeEdgeCounts[e[0]] += 1
			self.userNodeEdgeCounts[e[1]] += 1

	def RemoveUserEdge(self, e):
		if e in self.userEdges:
			if self.userEdgeCounts[e] > 0:
				self.userEdgeCounts[e] -= 1
				self.userNodeEdgeCounts[e[0]] -= 1
				self.userNodeEdgeCounts[e[1]] -= 1
			if self.userEdgeCounts[e] == 0:
				self.userEdges.remove(e)
				del self.userEdgeCounts[e]

	def ClearUserEdge(self, e):
		if e in self.userEdges:
			self.userEdges.remove(e)
			self.userNodeEdgeCounts[e[0]] -= self.userEdgeCounts[e]
			self.userNodeEdgeCounts[e[1]] -= self.userEdgeCounts[e]
			del self.userEdgeCounts[e]

	def DrawEdge(self, screen, e, count, color, width):
		p0 = self.GetNodePos(e[0])
		p1 = self.GetNodePos(e[1])
		if count > 1:
			p00 = (p0[0], p0[1] - self.edgeWidth) if IsHorizontalEdge(e) else (p0[0] - self.edgeWidth, p0[1])
			p01 = (p1[0], p1[1] - self.edgeWidth) if IsHorizontalEdge(e) else (p1[0] - self.edgeWidth, p1[1])
			pygame.draw.line(screen, color, p00, p01, width)
			p10 = (p0[0], p0[1] + self.edgeWidth) if IsHorizontalEdge(e) else (p0[0] + self.edgeWidth, p0[1])
			p11 = (p1[0], p1[1] + self.edgeWidth) if IsHorizontalEdge(e) else (p1[0] + self.edgeWidth, p1[1])
			pygame.draw.line(screen, color, p10, p11, width)
		else:
			pygame.draw.line(screen, color, p0, p1, width)

	def DrawPossibleEdges(self, screen):
		for e in self.possibleEdges:
			self.DrawEdge(screen, e, 1, (224, 224, 224), self.edgeWidth * 2)

	def DrawUserEdges(self, screen):
		for e in self.userEdges:
			self.DrawEdge(screen, e, self.userEdgeCounts[e], BLACK, self.edgeWidth)

	def DrawSolutionEdges(self, screen):
		for e in self.edges:
			self.DrawEdge(screen, e, self.edgeCounts[e], GREEN, self.edgeWidth / 2)

	def DrawNodes(self, screen):
		for u in self.nodes:
			pygame.draw.circle(screen, WHITE, self.GetNodePos(u), self.nodeRadius)
			pygame.draw.circle(screen, BLACK, self.GetNodePos(u), self.nodeRadius, self.nodeBorderWidth)
			self.numberTextCache.Draw(screen, self.GetNodePos(u), self.nodeEdgeCounts[u])

	def OnEvent(self, event):
		if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
			self.OnKeyEvent(event)
		elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
			self.OnMouseEvent(event)

	def OnKeyEvent(self, event):
		isDown = event.type == pygame.KEYDOWN
		wasDown = event.key in self.keyDown and self.keyDown[event.key]
		self.keyDown[event.key] = isDown
		self.keyPressed[event.key] = wasDown and not isDown

	def OnMouseEvent(self, event):
		isDown = event.type == pygame.MOUSEBUTTONDOWN
		wasDown = event.button in self.buttonDown and self.buttonDown[event.button]
		self.buttonDown[event.button] = isDown
		self.buttonPressed[event.button] = wasDown and not isDown

	def WasButtonPressed(self, button):
		return button in self.buttonPressed and self.buttonPressed[button]

	def WasKeyPressed(self, key):
		return key in self.keyPressed and self.keyPressed[key]

	def IsKeyDown(self, key):
		return key in self.keyDown and self.keyDown[key]

	def CheckSolution(self):
		for u in self.nodes:
			if u not in self.userNodeEdgeCounts or self.userNodeEdgeCounts[u] != self.nodeEdgeCounts[u]:
				return False
		return True

	def Win(self, screen):
		pos = (screen.get_width() / 2, screen.get_height() / 2)
		screen.blit(self.winText, self.winText.get_rect(center = pos))

	def Update(self):
		self.screenSurface.fill(WHITE)
		#self.DrawPossibleEdges(self.screenSurface)
		highlightEdge = self.FindClosestEdge(pygame.mouse.get_pos())
		if highlightEdge:
			canAdd = self.CanAddUserEdge(highlightEdge)
			canRemove = self.CanRemoveUserEdge(highlightEdge)
			if self.WasButtonPressed(LEFT_MOUSE_BUTTON):
				if canAdd:
					self.AddUserEdge(highlightEdge)
				#else:
				#	self.ClearUserEdge(highlightEdge)
			elif self.WasButtonPressed(RIGHT_MOUSE_BUTTON) and canRemove:
				self.RemoveUserEdge(highlightEdge)
			if canAdd or canRemove:
				self.DrawEdge(self.screenSurface, highlightEdge, 1, RED, self.edgeWidth * 2)
		self.DrawUserEdges(self.screenSurface)
		if self.IsKeyDown(pygame.K_F1):
			self.DrawSolutionEdges(self.screenSurface)
		if self.WasKeyPressed(pygame.K_F5):
			self.Generate(self.boardSize)
		if self.WasKeyPressed(pygame.K_PAGEUP) and self.boardSize < 20:
			self.boardSize += 1
			self.Generate(self.boardSize)
			self.SetOptimalScreenMode()
		if self.WasKeyPressed(pygame.K_PAGEDOWN) and self.boardSize > 4:
			self.boardSize -= 1
			self.Generate(self.boardSize)
			self.SetOptimalScreenMode()
		self.DrawNodes(self.screenSurface)
		if self.CheckSolution():
			self.Win(self.screenSurface)
		self.keyPressed = {}
		self.buttonPressed = {}

pygame.init()
board = Board()
board.Generate(BOARD_SIZE)
board.SetOptimalScreenMode()
pygame.display.set_caption("Hashi")
clock = pygame.time.Clock()
done = False
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		else:
			board.OnEvent(event)
	board.Update()
	clock.tick(120)
	pygame.display.flip()
pygame.quit()
