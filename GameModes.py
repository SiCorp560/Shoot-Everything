# GameModes.py holds the base code for running the game
# entire project inspired by Galaga:
# https://en.wikipedia.org/wiki/Galaga

# cmu_112_graphics from here:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
from cmu_112_graphics import *
from GameObjects import *
import random, time

# general GameModes code structure taken directly from 15-112 notes:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class TitleScreen(Mode):
    def appStarted(mode):
        mode.textTimer = 0
        mode.showText = True
        # list comprehension used in creating sparkles, taken from here:
        # https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
        mode.sparkles = [[random.randint(0, mode.width),
                            random.randint(0, mode.height),
                            random.randint(1, 11), True] for i in range(10)]
    
    def keyPressed(mode, event):
        if event.key == "1":
            mode.app.setActiveMode(mode.app.controls)
        elif event.key == "2":
            mode.app.setActiveMode(mode.app.highScores)
        else:
            mode.app.setActiveMode(mode.app.shooterGame)

    def timerFired(mode):
        mode.textTimer += 1
        for sparkle in mode.sparkles:
            if sparkle[2] <= 1:
                sparkle[3] = True
            elif sparkle[2] >= 10:
                sparkle[3] = False
            if sparkle[3]:
                sparkle[2] += 1
            else:
                sparkle[2] -= 1
        if mode.textTimer % 7 == 0:
            mode.showText = not mode.showText
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill="black")
        for sparkle in mode.sparkles:
            canvas.create_oval(sparkle[0] - (sparkle[2]/2),
                                sparkle[1] - (sparkle[2]/2),
                                sparkle[0] + (sparkle[2]/2),
                                sparkle[1] + (sparkle[2]/2), fill="white")
        canvas.create_text(mode.width/2, mode.height/3, text='SHOOT',
                            font="Arial 72 bold", fill="white")
        canvas.create_text(mode.width/2, mode.height/2, text='EVERYTHING',
                            font="Arial 72 bold", fill="white")
        canvas.create_text(10, mode.height - 10, text="Press 1 for help, or 2 for scores",
                            font="Arial 20 bold", fill="white", anchor="sw")
        if mode.showText:
            canvas.create_text(mode.width/2, mode.height*(2/3),
                                text="Press any button to begin!",
                                font="Arial 28 bold", fill="white")

class ShooterGame(Mode):
    def appStarted(mode):
        mode.initializeValues()
    
    def initializeValues(mode):
        # cinematics
        mode.stars = []
        mode.margin = 50
        mode.spriteCounter = 0

        # damage buffer
        mode.damageBuffer = 1
        mode.damageBufferTime = 0

        # current level
        mode.level = 1
        mode.levelBuffer = 2
        mode.levelBufferTime = time.time()

        # current score
        GameObject.score = 0
        mode.scoreCap = 100

        # current number of tokens
        GameObject.tokenScore = 0

        # upgrades
        GameObject.maxPellets = 3
        GameObject.doublePower = False
        GameObject.waveUnlock = False
        GameObject.bombUnlock = False
        GameObject.autoheal = False

        # game status
        mode.pause = False
        mode.gameOver = False

        # use of sprites learned from here:
        # https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#loadImageUsingFile
        ## sprites made by me in Paint 3D
        mode.rocketImage = mode.app.loadImage("Images/rocket.png")
        mode.pelletImage = mode.app.loadImage("Images/pellet.png")
        mode.waveImage = mode.app.loadImage("Images/wave.png")
        mode.bombImage = mode.app.loadImage("Images/bomb.png")
        mode.fallerImage = mode.app.loadImage("Images/faller.png")
        mode.runnerImage = mode.app.loadImage("Images/runner.png")
        mode.bullyImage = mode.app.loadImage("Images/bully.png")
        mode.spikeImage = mode.app.loadImage("Images/spike.png")
        mode.swarmImage = mode.app.loadImage("Images/swarm.png")
        mode.hostImage = mode.app.loadImage("Images/host.png")
        mode.tokenImage = mode.app.loadImage("Images/token.png")
        mode.upgradeImage = mode.app.loadImage("Images/upgrades.png")

        # rocket sprites
        mode.rocketSprites = []
        for i in range(2):
            mode.rocketSprites.append(mode.rocketImage.crop((i * 65, 0,
                                        (i+1) * 65, 65)))
        mode.rocketDamagedSprites = []
        for i in range(2):
            mode.rocketDamagedSprites.append(mode.rocketImage.crop((i * 65, 65,
                                        (i+1) * 65, 130)))
        
        # bullet sprites
        mode.pelletSprites = []
        for i in range(2):
            mode.pelletSprites.append(mode.pelletImage.crop((i * 25, 0,
                                        (i+1) * 25, 25)))
        mode.leftWaveSprites = []
        for i in range(2):
            mode.leftWaveSprites.append(mode.waveImage.crop((i * 70, 0,
                                        (i+1) * 70, 70)))
        mode.rightWaveSprites = []
        for i in range(2):
            mode.rightWaveSprites.append(mode.waveImage.crop((i * 70, 0,
                            (i+1) * 70, 70)).transpose(Image.FLIP_LEFT_RIGHT))
        mode.bombSprites = []
        for i in range(2):
            mode.bombSprites.append(mode.bombImage.crop((i * 25, 0,
                                        (i+1) * 25, 25)))
        
        # enemy sprites
        mode.fallerSprites = []
        for i in range(2):
            mode.fallerSprites.append(mode.fallerImage.crop((i * 40, 0,
                                        (i+1) * 40, 40)))
        mode.runnerSprites = []
        for i in range(2):
            mode.runnerSprites.append(mode.runnerImage.crop((i * 40, 0,
                                        (i+1) * 40, 40)))
        mode.runnerDamagedSprites = []
        for i in range(2):
            mode.runnerDamagedSprites.append(mode.runnerImage.crop((i * 40, 40,
                                        (i+1) * 40, 80)))
        mode.bullySprites = []
        for i in range(2):
            mode.bullySprites.append(mode.bullyImage.crop((i * 40, 0,
                                        (i+1) * 40, 40)))
        mode.hostSprites = []
        for i in range(4):
            mode.hostSprites.append(mode.hostImage.crop((i * 60, 0,
                                        (i+1) * 60, 60)))
        
        # token sprites
        mode.tokenSprites = []
        for i in range(4):
            mode.tokenSprites.append(mode.tokenImage.crop((i * 25, 0,
                                        (i+1) * 25, 25)))
        
        # upgrade sprites
        mode.plusOneSprites = []
        for i in range(2):
            mode.plusOneSprites.append(mode.upgradeImage.crop((i * 85, 0,
                                        (i+1) * 85, 85)))
        mode.timesTwoSprites = []
        for i in range(2):
            mode.timesTwoSprites.append(mode.upgradeImage.crop((i * 85, 85,
                                        (i+1) * 85, 170)))
        mode.waveUpgradeSprites = []
        for i in range(2):
            mode.waveUpgradeSprites.append(mode.upgradeImage.crop((i * 85, 170,
                                        (i+1) * 85, 255)))
        mode.bombUpgradeSprites = []
        for i in range(2):
            mode.bombUpgradeSprites.append(mode.upgradeImage.crop((i * 85, 255,
                                        (i+1) * 85, 340)))
        mode.firstAidSprites = []
        for i in range(2):
            mode.firstAidSprites.append(mode.upgradeImage.crop((i * 85, 340,
                                        (i+1) * 85, 425)))

        # rocket initialized
        mode.rocket = Rocket(mode.width/2, mode.height*(3/4))

    def timerFired(mode):  
        # game over condition
        if mode.rocket.health <= 0:
            mode.gameOver = True
        
        mode.spriteCounter += 1
        
        # idea for moving star background taken from Hack112 "Balloon Bullet Time" project
        mode.stars.append([random.randint(0, mode.width), 0, random.randint(10, 20)])
        i = 0
        while i < len(mode.stars):
            mode.stars[i][1] += mode.stars[i][2]
            if mode.stars[i][1] > mode.height:
                mode.stars.pop(i)
            else:
                i += 1
        
        if not mode.gameOver and not mode.pause:
            # static methods from GameObjects.py called here
            GameObject.move(mode)
            GameObject.remove(mode)
            GameObject.boid()

            # updating level
            if GameObject.score >= mode.scoreCap and mode.level < 10:
                mode.scoreCap *= 2
                mode.level += 1
                mode.levelBufferTime = time.time()
            
            # rocket regeneration
            if mode.rocket.health < 100 and GameObject.autoheal:
                mode.rocket.health += 0.1
            
            # counting each type of enemy
            fallerCount = 0
            runnerCount = 0
            bullyCount = 0
            currentBullies = []
            swarmCount = 0
            hostCount = 0
            currentHosts = []
            for enemy in GameObject.enemies:
                if isinstance(enemy, Faller):
                    fallerCount += 1
                elif isinstance(enemy, Runner):
                    runnerCount += 1
                elif isinstance(enemy, Bully):
                    bullyCount += 1
                    currentBullies.append(enemy)
                elif isinstance(enemy, Swarm):
                    swarmCount += 1
                elif isinstance(enemy, Host):
                    hostCount += 1
                    currentHosts.append(enemy)
                
                # rocket takes damage
                if ((mode.rocket.objectCollision(enemy) and
                    time.time() - mode.damageBufferTime > mode.damageBuffer)):
                    mode.rocket.health -= enemy.power
                    mode.damageBufferTime = time.time()
                for bullet in GameObject.bullets:
                    if ((mode.rocket.objectCollision(bullet)) and
                        (isinstance(bullet, Bomb)) and (bullet.growing)):
                        mode.rocket.health -= 1
                
                # certain enemies stop
                if isinstance(enemy, Host) and enemy.y >= mode.height/6:
                    enemy.stationary = True
                elif isinstance(enemy, Bully) and enemy.y >= mode.height/4:
                    enemy.stationary = True
            
            # enemy generation
            if ((mode.level < 6) and (fallerCount < mode.level) and
                (mode.spriteCounter % 5 == 0)):
                mode.newFaller = Faller(random.randint(0, mode.width), 0)
            if ((mode.level > 3) and (runnerCount < mode.level - 2) and 
                (mode.spriteCounter % 10 == 0)):
                mode.newRunner = Runner(random.randint(0, mode.width), 0)
            if ((mode.level > 4) and (bullyCount < mode.level - 6) and
                (mode.spriteCounter % 15 == 0)):
                mode.newBully = Bully(random.randint(0, mode.width), 0)
            for bully in currentBullies:
                if mode.spriteCounter % 20 == 0:
                    mode.newSpike = Spike(bully.x, bully.y)
            if ((mode.level > 1) and (swarmCount < mode.level * 3) and
                (mode.spriteCounter % 30 == 0)):
                for i in range(3):
                    mode.newSwarm = Swarm(random.randint(0, mode.width), 0)
            if ((mode.level > 5) and (mode.level % 2 == 0) and (hostCount < 1) and
                (mode.spriteCounter % 50 == 0)):
                mode.newHost = Host(random.randint(0, mode.width), 0)
            for host in currentHosts:
                if mode.spriteCounter % 20 == 0:
                    mode.newSwarm = Swarm(host.x, host.y)
            
            # token generation
            if mode.spriteCounter % 100 == 0:
                mode.newToken = Token(random.randint(0, mode.width), 0)

        # cinematic of rocket going "oh noes"
        elif mode.gameOver:
            GameObject.clearAll()
            mode.rocket.x -= 10
            mode.rocket.y += 10

    def keyPressed(mode, event):
        # controls during the actual game
        if not mode.gameOver and not mode.pause:
            if event.key == "Left":
                mode.rocket.x -= 20
                if mode.rocket.outOfBounds(mode):
                    mode.rocket.x += 20
            elif event.key == "Right":
                mode.rocket.x += 20
                if mode.rocket.outOfBounds(mode):
                    mode.rocket.x -= 20
            elif event.key == "z":
                pelletCount = 0
                for bullet in GameObject.bullets:
                    if isinstance(bullet, Pellet):
                        pelletCount += 1
                if pelletCount < GameObject.maxPellets:
                    mode.newPellet = Pellet(mode.rocket.x, mode.rocket.y)
            elif event.key == "x":
                if GameObject.waveUnlock:
                    waveOn = False
                    for bullet in GameObject.bullets:
                        if isinstance(bullet, LeftWave) or isinstance(bullet, RightWave):
                            waveOn = True
                    if not waveOn:
                        mode.newLeftWave = LeftWave(mode.rocket.x, mode.rocket.y)
                        mode.newRightWave = RightWave(mode.rocket.x, mode.rocket.y)
            elif event.key == "c":
                if GameObject.bombUnlock:
                    bombOn = False
                    for bullet in GameObject.bullets:
                        if isinstance(bullet, Bomb):
                            bombOn = True
                    if not bombOn:
                        mode.newBomb = Bomb(mode.rocket.x, mode.rocket.y)
            elif event.key == "p":
                mode.pause = not mode.pause
            
############### DEBUG COMMANDS ###############
            
            elif event.key == "1":
                mode.newFaller = Faller(random.randint(0, mode.width), 0)
            elif event.key == "2":
                mode.newRunner = Runner(random.randint(0, mode.width), 0)
            elif event.key == "3":
                for i in range(5):
                    mode.newSwarm = Swarm(random.randint(0, mode.width), 0)
            elif event.key == "4":
                mode.newHost = Host(random.randint(0, mode.width), 0)
            elif event.key == "5":
                mode.newBully = Bully(random.randint(0, mode.width), 0)
            elif event.key == "8":
                mode.rocket.health = 0
            elif event.key == "9":
                GameObject.tokenScore += 100
            elif event.key == "0" and mode.level < 10:
                mode.scoreCap *= 2
                mode.level += 1
                mode.levelBufferTime = time.time()
            
##############################################
        
        # controls in the pause/upgrade menu
        elif mode.pause:
            if event.key == "p":
                mode.pause = not mode.pause
            elif ((event.key == "1") and (GameObject.maxPellets < 10) and
                (GameObject.tokenScore >= 5)):
                GameObject.maxPellets += 1
                GameObject.tokenScore -= 5
            elif ((event.key == "2") and (not GameObject.doublePower) and
                (GameObject.tokenScore >= 15)):
                GameObject.doublePower = True
                GameObject.tokenScore -= 15
            elif ((event.key == "3") and (not GameObject.waveUnlock) and
                (GameObject.tokenScore >= 10)):
                GameObject.waveUnlock = True
                GameObject.tokenScore -= 10
            elif ((event.key == "4") and (not GameObject.bombUnlock) and
                (GameObject.tokenScore >= 20)):
                GameObject.bombUnlock = True
                GameObject.tokenScore -= 20
            elif ((event.key == "5") and (not GameObject.autoheal) and
                (GameObject.tokenScore >= 20)):
                GameObject.autoheal = True
                GameObject.tokenScore -= 20
            elif event.key == "r":
                GameObject.clearAll()
                mode.initializeValues()
            elif event.key == "m":
                GameObject.clearAll()
                mode.initializeValues()
                mode.app.setActiveMode(mode.app.titleScreen)
        
        # scores updated regardless of restart or menu
        # file IO taken from here:
        # https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
        else:
            if event.key == "r":
                with open("scores.txt", "rt") as f:
                    scoreText = f.read()
                with open("scores.txt", "wt") as f:
                    f.write(f"{scoreText}\n{GameObject.score}")
                mode.initializeValues()
            elif event.key == "m":
                with open("scores.txt", "rt") as f:
                    scoreText = f.read()
                with open("scores.txt", "wt") as f:
                    f.write(f"{scoreText}\n{GameObject.score}")
                mode.initializeValues()
                mode.app.setActiveMode(mode.app.titleScreen)

    def redrawAll(mode, canvas):
        # draws stars and background
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill="black")
        for star in mode.stars:
            canvas.create_oval(star[0], star[1], star[0]+5, star[1]+5,
                                fill="white")
        
        # draws enemies
        # use of images learned from here:
        # https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#loadImageUsingFile
        for enemy in GameObject.enemies:
            if isinstance(enemy, Faller):
                canvas.create_image(enemy.x, enemy.y,
                    image=ImageTk.PhotoImage(mode.fallerSprites[mode.spriteCounter % 2]))
            elif isinstance(enemy, Runner):
                if enemy.health == 2:
                    canvas.create_image(enemy.x, enemy.y,
                        image=ImageTk.PhotoImage(mode.runnerSprites[mode.spriteCounter % 2]))
                else:
                    canvas.create_image(enemy.x, enemy.y,
                        image=ImageTk.PhotoImage(mode.runnerDamagedSprites[mode.spriteCounter % 2]))
            elif isinstance(enemy, Bully):
                canvas.create_image(enemy.x, enemy.y,
                        image=ImageTk.PhotoImage(mode.bullySprites[mode.spriteCounter %2]))
            elif isinstance(enemy, Spike):
                canvas.create_image(enemy.x, enemy.y,
                                    image=ImageTk.PhotoImage(mode.spikeImage))
            elif isinstance(enemy, Swarm):
                rotatedImage = mode.swarmImage.rotate(enemy.angle)
                canvas.create_image(enemy.x, enemy.y,
                                    image=ImageTk.PhotoImage(rotatedImage))
            elif isinstance(enemy, Host):
                canvas.create_image(enemy.x, enemy.y,
                        image=ImageTk.PhotoImage(mode.hostSprites[mode.spriteCounter % 8 % 4]))
        
        # draws bullets
        for bullet in GameObject.bullets:
            if isinstance(bullet, Pellet):
                canvas.create_image(bullet.x, bullet.y,
                    image=ImageTk.PhotoImage(mode.pelletSprites[mode.spriteCounter % 2]))
            elif isinstance(bullet, LeftWave):
                canvas.create_image(bullet.x, bullet.y,
                    image=ImageTk.PhotoImage(mode.leftWaveSprites[mode.spriteCounter % 2]))
            elif isinstance(bullet, RightWave):
                canvas.create_image(bullet.x, bullet.y,
                    image=ImageTk.PhotoImage(mode.rightWaveSprites[mode.spriteCounter % 2]))
            elif isinstance(bullet, Bomb):
                scaledBomb = mode.scaleImage(mode.bombSprites[mode.spriteCounter % 2],
                                                bullet.radius/12.5)
                canvas.create_image(bullet.x, bullet.y,
                                    image=ImageTk.PhotoImage(scaledBomb))
        
        # draws tokens
        for token in GameObject.tokens:
            canvas.create_image(token.x, token.y,
                        image=ImageTk.PhotoImage(mode.tokenSprites[mode.spriteCounter % 8 % 4]))
        
        # draws rocket
        if time.time() - mode.damageBufferTime <= mode.damageBuffer or mode.gameOver:
            canvas.create_image(mode.rocket.x, mode.rocket.y,
                    image=ImageTk.PhotoImage(mode.rocketDamagedSprites[mode.spriteCounter % 2]))
        else:
            canvas.create_image(mode.rocket.x, mode.rocket.y,
                    image=ImageTk.PhotoImage(mode.rocketSprites[mode.spriteCounter % 2]))
        
        # draws health bar
        canvas.create_rectangle(0, mode.height - mode.margin, mode.width,
                                mode.height, fill="red")
        canvas.create_rectangle(0, mode.height - mode.margin,
                                mode.width*(mode.rocket.health/100), mode.height,
                                fill="green")

        # draws score and level
        canvas.create_text(10, 0, text=f"Level {mode.level}",
                            font="Arial 20 bold", fill="white", anchor="nw")
        if mode.level < 10:
            canvas.create_text(10, 20, text=f"Score: {GameObject.score}/{mode.scoreCap}",
                                font="Arial 20 bold", fill="white", anchor="nw")
        else:
            canvas.create_text(10, 20, text=f"Score: {GameObject.score}",
                            font="Arial 20 bold", fill="white", anchor="nw")
        canvas.create_text(10, 40, text=f"Tokens: {GameObject.tokenScore}",
                            font="Arial 20 bold", fill="white", anchor="nw")
        
        # draws game over text
        if mode.gameOver:
            canvas.create_text(mode.width/2, mode.height/2, text="GAME OVER",
                                font="Arial 36 bold", fill="white")
            canvas.create_text(mode.width/2, (3/5)*mode.height,
                                text="Press r to restart, or m to return to menu",
                                font="Arial 20 bold", fill="white")
        
        # draws pause/upgrade icons
        elif mode.pause:
            canvas.create_text(mode.width/2, mode.height/3, text="PAUSED",
                                font="Arial 36 bold", fill="white")
            
            if GameObject.maxPellets < 10:
                icon = 0
            else:
                icon = 1
            canvas.create_image((1/6)*mode.width, mode.height/2,
                            image=ImageTk.PhotoImage(mode.plusOneSprites[icon]))
            canvas.create_text((1/6)*mode.width, (3/5)*mode.height - 20,
                            text=f"Max Pellets: {GameObject.maxPellets}",
                            font="Arial 18 bold", fill="white")
            canvas.create_text((1/6)*mode.width, (3/5)*mode.height,
                            text="5 Tokens", font="Arial 18 bold", fill="white")
            
            if GameObject.doublePower:
                icon = 1
            else:
                icon = 0
            canvas.create_image((2/6)*mode.width, mode.height/2,
                            image=ImageTk.PhotoImage(mode.timesTwoSprites[icon]))
            canvas.create_text((2/6)*mode.width, (3/5)*mode.height - 20,
                            text=f"Double Power", font="Arial 18 bold",
                            fill="white")
            canvas.create_text((2/6)*mode.width, (3/5)*mode.height,
                            text=f"15 Tokens", font="Arial 18 bold",
                            fill="white")
            
            if GameObject.waveUnlock:
                icon = 1
            else:
                icon = 0
            canvas.create_image((3/6)*mode.width, mode.height/2,
                            image=ImageTk.PhotoImage(mode.waveUpgradeSprites[icon]))
            canvas.create_text((3/6)*mode.width, (3/5)*mode.height - 20,
                            text=f"Wave Bullet", font="Arial 18 bold",
                            fill="white")
            canvas.create_text((3/6)*mode.width, (3/5)*mode.height,
                            text=f"10 Tokens", font="Arial 18 bold",
                            fill="white")
            
            if GameObject.bombUnlock:
                icon = 1
            else:
                icon = 0
            canvas.create_image((4/6)*mode.width, mode.height/2,
                            image=ImageTk.PhotoImage(mode.bombUpgradeSprites[icon]))
            canvas.create_text((4/6)*mode.width, (3/5)*mode.height - 20,
                            text=f"Bomb Bullet", font="Arial 18 bold",
                            fill="white")
            canvas.create_text((4/6)*mode.width, (3/5)*mode.height,
                            text=f"20 Tokens", font="Arial 18 bold",
                            fill="white")
            
            if GameObject.autoheal:
                icon = 1
            else:
                icon = 0
            canvas.create_image((5/6)*mode.width, mode.height/2,
                            image=ImageTk.PhotoImage(mode.firstAidSprites[icon]))
            canvas.create_text((5/6)*mode.width, (3/5)*mode.height - 20,
                            text=f"Regeneration", font="Arial 18 bold",
                            fill="white")
            canvas.create_text((5/6)*mode.width, (3/5)*mode.height,
                            text=f"20 Tokens", font="Arial 18 bold",
                            fill="white")
        
        # draws beginning level text
        elif time.time() - mode.levelBufferTime <= mode.levelBuffer:
            canvas.create_text(mode.width/2, mode.height/2,
                                text=f"Level {mode.level}",
                                font="Arial 36 bold", fill="white")

class Controls(Mode):
    def appStarted(mode):
        mode.helpImage = mode.app.loadImage("Images/help.png")
    
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2,
                            image=ImageTk.PhotoImage(mode.helpImage))

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.titleScreen)

class HighScores(Mode):
    def appStarted(mode):
        mode.initializeScores()
        mode.stars = []
    
    def initializeScores(mode):
        with open("scores.txt", "rt") as f:
            scoreText = f.read()
        splitScoreText = sorted(str.splitlines(scoreText))
        mode.scores = []
        for score in splitScoreText:
            mode.scores.append(int(score))
        mode.scores.sort()
    
    def timerFired(mode):
        mode.stars.append([mode.width, random.randint(0, mode.height), random.randint(10, 20)])
        i = 0
        while i < len(mode.stars):
            mode.stars[i][0] -= mode.stars[i][2]
            if mode.stars[i][0] < 0:
                mode.stars.pop(i)
            else:
                i += 1

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.titleScreen)

    def redrawAll(mode, canvas):
        mode.initializeScores()

        # draws stars and background
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill="black")
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill="black")
        for star in mode.stars:
            canvas.create_oval(star[0], star[1], star[0]+5, star[1]+5,
                                fill="white")

        # draws top 10 scores of all time
        canvas.create_text(mode.width/2, mode.height/6, text="High Scores",
                            font="Arial 36 bold", fill="white", anchor="n")
        for i in range(1, 11):
            if len(mode.scores) >= i:
                text = f"{i}. {mode.scores[len(mode.scores)-i]}"
            else:
                text = f"{i}."
            canvas.create_text(mode.width/4, mode.height * ((5+i)/20),
                                text=text, font="Arial 20 bold", fill="white",
                                anchor="w")

class MyModalApp(ModalApp):
    def appStarted(app):
        app.titleScreen = TitleScreen()
        app.shooterGame = ShooterGame()
        app.controls = Controls()
        app.highScores = HighScores()
        app.setActiveMode(app.titleScreen)
        app.timerDelay = 50

app = MyModalApp(width=800, height=800)