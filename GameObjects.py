# GameObjects.py is where all entities that appear in the game proper are defined

import math, random

class GameObject(object):
    bullets = set()
    enemies = set()
    tokens = set()
    rocket = None
    id = 0
    score = 0
    tokenScore = 0
    maxPellets = 3
    doublePower = False
    waveUnlock = False
    bombUnlock = False
    autoheal = False

    # idea to use static methods came from TA
    # moves all bullets and enemies
    @staticmethod
    def move(mode):
        for bullet in GameObject.bullets:
            dx, dy = bullet.getDirections(bullet.angle)
            if isinstance(bullet, Bomb):
                if bullet.growing:
                    bullet.radius += 10
                else:
                    bullet.x += dx
                    bullet.y += dy
            else:
                bullet.x += dx
                bullet.y += dy
        
        for enemy in GameObject.enemies:
            dx, dy = enemy.getDirections(enemy.angle)
            if isinstance(enemy, Runner):
                dx, temp = enemy.getDirections(enemy.getAngle(GameObject.rocket) + 180)
                dx *= 2
            if isinstance(enemy, Host):
                if enemy.stationary:
                    pass
                else:
                    enemy.x += dx
                    enemy.y += dy
            elif isinstance(enemy, Bully):
                if enemy.stationary:
                    if enemy.moveRight:
                        enemy.x += enemy.speed
                        if enemy.x > mode.width:
                            enemy.moveRight = False
                    else:
                        enemy.x -= enemy.speed
                        if enemy.x < 0:
                            enemy.moveRight = True
                else:
                    enemy.x += dx
                    enemy.y += dy
            else:
                enemy.x += dx
                enemy.y += dy
        
        for token in GameObject.tokens:
            token.y += 10
    
    # removes any bullets, enemies, and tokens that should be removed
    @staticmethod
    def remove(mode):
        bulletTemp = []
        for bullet in GameObject.bullets:
            for enemy in GameObject.enemies:
                if bullet.objectCollision(enemy):
                    if GameObject.doublePower:
                        enemy.health -= 2*bullet.power
                    else:
                        enemy.health -= bullet.power
                    if isinstance(enemy, Runner):
                        enemy.speed *= 1.5
                    if isinstance(bullet, Bomb) and not bullet.growing:
                        bullet.growing = True
                    elif ((isinstance(bullet, Bomb)) or
                            (isinstance(bullet, LeftWave)) or
                            (isinstance(bullet, RightWave))):
                        pass
                    else:
                        bulletTemp.append(bullet)
            if bullet.outOfBounds(mode):
                bulletTemp.append(bullet)
            if bullet.radius >= 100:
                bulletTemp.append(bullet)
        for item in bulletTemp:
            if item in GameObject.bullets:
                GameObject.bullets.remove(item)
        
        enemyTemp = []
        for enemy in GameObject.enemies:
            if enemy.health <= 0:
                enemyTemp.append(enemy)
                GameObject.score += enemy.score
            if enemy.outOfBounds(mode):
                enemyTemp.append(enemy)
            if isinstance(enemy, Spike):
                if enemy.hit:
                    enemyTemp.append(enemy)
                elif enemy.objectCollision(GameObject.rocket):
                    enemy.hit = True
        for item in enemyTemp:
            if item in GameObject.enemies:
                GameObject.enemies.remove(item)
        
        tokenTemp = []
        for token in GameObject.tokens:
            if token.objectCollision(GameObject.rocket):
                GameObject.tokenScore += 1
                tokenTemp.append(token)
            if token.outOfBounds(mode):
                tokenTemp.append(token)
        for item in tokenTemp:
            if item in GameObject.tokens:
                GameObject.tokens.remove(item)
    
    # idea of Boids taken from here:
    # https://en.wikipedia.org/wiki/Boids
    @staticmethod
    def boid():
        for enemy in GameObject.enemies:
            if isinstance(enemy, Swarm):
                enemy.towardsAngle(enemy.getAngle(GameObject.rocket) + 180, 20)
                nearby = enemy.getNearbySwarm()
                for swarm in nearby:
                    enemy.towardsAngle((swarm.angle - 180) % 360, 5)
                enemy.towardsAngle(enemy.alignment() % 360, 10)
                enemy.towardsAngle(enemy.getAngle(enemy.centerOfMass()), 5)

    # removes all bullets, enemies, and tokens
    @staticmethod
    def clearAll():
        GameObject.bullets = set()
        GameObject.enemies = set()
        GameObject.tokens = set()
    
    def __init__(self, x, y, radius):
        GameObject.id += 1
        self.id = GameObject.id
        self.x, self.y = x, y
        self.radius = radius
    
    def __hash__(self):
        return hash(self.id)
    
    # returns distance between two game objects
    def getDistance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
    
    # returns angle between a game object and
    # either another game object or a point
    def getAngle(self, other):
        if other == None:
            return None
        if isinstance(other, GameObject):
            difX = self.x - other.x
            difY = self.y - other.y
        else:
            x, y = other
            difX = self.x - x
            difY = self.y - y
        if difX == 0:
            if difY >= 0:
                return 90
            else:
                return 270
        elif difY == 0:
            if difX >= 0:
                return 180
            else:
                return 0
        else:
            tempAngle = math.degrees(math.atan(difY/difX))
            if difX > 0:
                if difY > 0:
                    return 180 - tempAngle
                else:
                    return 180 + abs(tempAngle)
            else:
                return tempAngle % 360
    
    # returns change in coordinates based on angle and speed
    def getDirections(self, angle):
        dx = -1 * math.cos(math.radians(angle)) * self.speed
        dy = -1 * math.sin(math.radians(angle)) * self.speed
        return dx, dy

    # object collision determined by lines
    # line collision suggested by TA
    def objectCollision(self, other):
        selfPoints = self.getBounds()
        otherPoints = other.getBounds()
        collisionCheck = False
        for i in range(len(selfPoints)):
            x0, y0 = selfPoints[i]
            x1, y1 = selfPoints[(i+1)%len(selfPoints)]
            for i in range(len(otherPoints)):
                x2, y2 = otherPoints[i]
                x3, y3 = otherPoints[(i+1)%len(otherPoints)]
                if x0 == x1:
                    slope1 = None
                else:
                    slope1 = (y1 - y0) / (x1 - x0)
                if x2 == x3:
                    slope2 = None
                else:
                    slope2 = (y3 - y2) / (x3 - x2)
                if slope1 != slope2:
                    if slope1 == None:
                        constant2 = y2 - (slope2 * x2)
                        x = x0
                        y = (slope2 * x) + constant2
                    elif slope2 == None:
                        constant1 = y0 - (slope1 * x0)
                        x = x2
                        y = (slope1 * x) + constant1
                    else:
                        constant1 = y0 - (slope1 * x0)
                        constant2 = y2 - (slope2 * x2)
                        x = (constant2 - constant1) / (slope1 - slope2)
                        y = (slope1 * x) + constant1
                    if ((((x0 <= x <= x1) or (x1 <= x <= x0)) and
                        ((y0 <= y <= y1) or (y1 <= y <= y0))) and
                        (((x2 <= x <= x3) or (x3 <= x <= x2)) and
                        ((y2 <= y <= y3) or (y3 <= y <= y2)))):
                        collisionCheck = True
        return collisionCheck

# Rocket class
class Rocket(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32.5)
        self.health = 100
        GameObject.rocket = self
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x, self.y - self.radius)
        p2 = (self.x - (5/13)*self.radius, self.y - (11/13)*self.radius)
        p3 = (self.x - (5/13)*self.radius, self.y - (1/13)*self.radius)
        p4 = (self.x - self.radius, self.y + (3/13)*self.radius)
        p5 = (self.x - self.radius, self.y + (9/13)*self.radius)
        p6 = (self.x + self.radius, self.y + (9/13)*self.radius)
        p7 = (self.x + self.radius, self.y + (3/13)*self.radius)
        p8 = (self.x + (5/13)*self.radius, self.y - (11/13)*self.radius)
        p9 = (self.x + (5/13)*self.radius, self.y - (1/13)*self.radius)
        return [p1,p2,p3,p4,p5,p6,p7,p8,p9]

    # checks if rocket is off the screen
    def outOfBounds(self, mode):
        boundsCheck = False
        for point in self.getBounds():
            x, y = point
            if x < 0 or x > mode.width:
                boundsCheck = True
        return boundsCheck

# Bullet class
class Bullet(GameObject): 
    def __init__(self, x, y, radius, angle, speed, power):
        super().__init__(x, y, radius)
        self.speed = speed
        self.angle = angle
        self.power = power
        GameObject.bullets.add(self)
    
    # checks if bullet is off the screen
    def outOfBounds(self, mode):
        boundsCheck = False
        for point in self.getBounds():
            x, y = point
            if x < 0 or x > mode.width or y < 0:
                boundsCheck = True
        return boundsCheck

# Pellet class, Bullet subclass
class Pellet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 12.5, 90, 20, 1)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (3/5)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (3/5)*self.radius)
        p3 = (self.x - self.radius, self.y + (3/5)*self.radius)
        p4 = (self.x - (3/5)*self.radius, self.y + self.radius)
        p5 = (self.x + (3/5)*self.radius, self.y + self.radius)
        p6 = (self.x + self.radius, self.y + (3/5)*self.radius)
        p7 = (self.x + self.radius, self.y - (3/5)*self.radius)
        p8 = (self.x + (3/5)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6,p7,p8]

# LeftWave class, Bullet subclass
class LeftWave(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 0, 20, 50)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (5/7)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (5/7)*self.radius)
        p3 = (self.x - self.radius, self.y + (5/7)*self.radius)
        p4 = (self.x - (5/7)*self.radius, self.y + self.radius)
        p5 = (self.x - (1/7)*self.radius, self.y + self.radius)
        p6 = (self.x - (1/7)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6]

# RightWave class, Bullet subclass
class RightWave(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 180, 20, 50)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x + (5/7)*self.radius, self.y - self.radius)
        p2 = (self.x + self.radius, self.y - (5/7)*self.radius)
        p3 = (self.x + self.radius, self.y + (5/7)*self.radius)
        p4 = (self.x + (5/7)*self.radius, self.y + self.radius)
        p5 = (self.x + (1/7)*self.radius, self.y + self.radius)
        p6 = (self.x + (1/7)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6]

# Bomb class, Bullet subclass
class Bomb(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, 12.5, 90, 10, 1)
        self.growing = False
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (3/5)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (3/5)*self.radius)
        p3 = (self.x - self.radius, self.y + (3/5)*self.radius)
        p4 = (self.x - (3/5)*self.radius, self.y + self.radius)
        p5 = (self.x + (3/5)*self.radius, self.y + self.radius)
        p6 = (self.x + self.radius, self.y + (3/5)*self.radius)
        p7 = (self.x + self.radius, self.y - (3/5)*self.radius)
        p8 = (self.x + (3/5)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6,p7,p8]

# Enemy class
class Enemy(GameObject):
    def __init__(self, x, y, radius, angle, speed, health, power, score):
        super().__init__(x, y, radius)
        self.angle = angle % 360
        self.speed = speed
        self.health = health
        self.power = power
        self.score = score
        GameObject.enemies.add(self)
    
    # checks if enemy is off the screen
    def outOfBounds(self, mode):
        boundsCheck = False
        for point in self.getBounds():
            x, y = point
            if y > mode.height - mode.margin:
                boundsCheck = True
        return boundsCheck

# Faller class, Enemy subclass
class Faller(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 270, random.randint(10, 30), 1, 10, 20)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (1/2)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (1/2)*self.radius)
        p3 = (self.x - self.radius, self.y + (1/4)*self.radius)
        p4 = (self.x + self.radius, self.y + (1/4)*self.radius)
        p5 = (self.x + self.radius, self.y - (1/2)*self.radius)
        p6 = (self.x + (1/2)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6]

# Runner class, Enemy subclass
class Runner(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 270, random.randint(10, 20), 2, 7, 50)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - self.radius, self.y - (1/4)*self.radius)
        p2 = (self.x - self.radius, self.y + self.radius)
        p3 = (self.x + self.radius, self.y + self.radius)
        p4 = (self.x + self.radius, self.y - (1/4)*self.radius)
        return [p1,p2,p3,p4]

# Bully class, Enemy subclass
class Bully(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 270, 15, 2, 1, 100)
        self.stationary = False
        self.moveRight = True
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (1/4)*self.radius)
        p3 = (self.x - (1/2)*self.radius, self.y + (1/4)*self.radius)
        p4 = (self.x + (1/2)*self.radius, self.y + (1/4)*self.radius)
        p5 = (self.x + self.radius, self.y - (1/4)*self.radius)
        p6 = (self.x + self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6]

# Spike class, Enemy subclass
class Spike(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 7.5, 270, 20, 1, 10, 1)
        self.hit = False
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - self.radius, self.y - self.radius)
        p2 = (self.x, self.y + self.radius)
        p3 = (self.x + self.radius, self.y - self.radius)
        return [p1,p2,p3]

# Host class, Enemy subclass
class Host(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 270, 5, 10, 1, 500)
        self.stationary = False
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (1/2)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (1/2)*self.radius)
        p3 = (self.x - self.radius, self.y + (1/2)*self.radius)
        p4 = (self.x - (1/2)*self.radius, self.y + self.radius)
        p5 = (self.x + (1/2)*self.radius, self.y + self.radius)
        p6 = (self.x + self.radius, self.y + (1/2)*self.radius)
        p7 = (self.x + self.radius, self.y - (1/2)*self.radius)
        p8 = (self.x + (1/2)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6,p7,p8]

# Swarm class, Enemy subclass
class Swarm(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 12.5, 270, 10, 1, 5, 5)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x + self.radius * math.cos(math.radians(self.angle)),
                self.y + self.radius * math.sin(math.radians(self.angle)))
        p2 = (self.x + self.radius * math.cos(math.radians(self.angle + 90)),
                self.y + self.radius * math.sin(math.radians(self.angle + 90)))
        p3 = (self.x + self.radius * math.cos(math.radians(self.angle + 180)),
                self.y + self.radius * math.sin(math.radians(self.angle + 180)))
        p4 = (self.x + self.radius * math.cos(math.radians(self.angle + 270)),
                self.y + self.radius * math.sin(math.radians(self.angle + 270)))
        return [p1,p2,p3,p4]
    
    # returns all nearby swarms
    def getNearbySwarm(self):
        distance = self.radius * 3
        result = []
        for enemy in GameObject.enemies:
            if ((isinstance(enemy, Swarm)) and
                (self.getDistance(enemy) < distance) and (enemy is not self)):
                result.append(enemy)
        return result
    
    # calculates the average alignment angle for all nearby swarms
    def alignment(self):
        nearby = self.getNearbySwarm()
        avgAngle = 0
        if nearby == []:
            return self.angle
        else:
            for enemy in nearby:
                avgAngle += enemy.angle
            return avgAngle/len(nearby)
    
    # calculates the center of mass for all nearby swarms
    def centerOfMass(self):
        nearby = self.getNearbySwarm()
        x = 0
        y = 0
        if nearby == []:
            return None
        else:
            for enemy in nearby:
                x += enemy.x
                y += enemy.y
            return (x/len(nearby), y/len(nearby))
    
    # turns swarm towards an angle by a specified amount
    def towardsAngle(self, angle, turn):
        if angle == self.angle or angle == None:
            pass
        else:
            if abs(self.angle - angle) <= 180:
                if self.angle > angle:
                    self.angle = (self.angle - turn) % 360
                else:
                    self.angle = (self.angle + turn) % 360
            else:
                if self.angle > angle:
                    self.angle = (self.angle + turn) % 360
                else:
                    self.angle = (self.angle - turn) % 360

# Token class
class Token(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 12.5)
        GameObject.tokens.add(self)
    
    # object bounds for line collision determined manually
    def getBounds(self):
        p1 = (self.x - (3/5)*self.radius, self.y - self.radius)
        p2 = (self.x - self.radius, self.y - (3/5)*self.radius)
        p3 = (self.x - self.radius, self.y + (3/5)*self.radius)
        p4 = (self.x - (3/5)*self.radius, self.y + self.radius)
        p5 = (self.x + (3/5)*self.radius, self.y + self.radius)
        p6 = (self.x + self.radius, self.y + (3/5)*self.radius)
        p7 = (self.x + self.radius, self.y - (3/5)*self.radius)
        p8 = (self.x + (3/5)*self.radius, self.y - self.radius)
        return [p1,p2,p3,p4,p5,p6,p7,p8]
    
    # checks if bullet is off the screen
    def outOfBounds(self, mode):
        boundsCheck = False
        for point in self.getBounds():
            x, y = point
            if y > mode.height - mode.margin:
                boundsCheck = True
        return boundsCheck