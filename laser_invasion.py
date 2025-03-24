'''
Max Robinson
laser_invasion.py
10/11/2024

Description:
A simple game built using Tkinter, where the player
controls a spaceship and shoots at invaders.
The game includes features like scoring, levels,
and a leaderboard.

Dependencies:
- Tkinter

Usage:
Run this script to start the Laser Invasion game.
'''
from tkinter import Tk, Canvas, PhotoImage
from tkinter import Button, Toplevel, Label, Entry, Frame
# Game settings and configuration variables
width, height, window, canvas = 600, 400, None, None
playerWidth, playerHeight = 50, 30
invaderWidth, invaderHeight = 40, 40
bulletWidth, bulletHeight, bulletSpeed = 5, 10, 7
bossCanvas, bossKeyActive, bossImage = None, False, None
settingsWindow = None
frame = None
startButtons, playAgainButton = [], None

# Initializes starting in-game variables

# Player variables
playerX, playerY, playerSprite = width // 2, height - playerHeight, None
# Invader variables
(
    invaderX,
    invaderY,
    invaderSprite,
    numInvaders,
    invaders,
    moveInvaderX,
    moveInvaderY,
    invadersKilled,
) = (175, 50, None, 6, [], 12, 12, 0)
# Bullet variables
bullets = []  # Initialized array for the bullets currently in the window
largeBullet = False  # Toggle between bullet cheat

shootingCooldown = 10
shootingTimer = 0  # Timer that counts frames since the last shot

# Starting variables displayed at top of the window
score, lives, level = 0, 3, 1

# Variables used when game is paused/unpaused
gamePaused, pausedText = False, None

# Initial keyboard bindings
shootKey, leftKey, rightKey = "<space>", "<Left>", "<Right>"

# Initialize Window
window = Tk()
window.title("Laser Invasion")  # Title of the game

# Seamless Space Backgrounds*
#  by [Screaming Brain Studios]
# (https://screamingbrainstudios.itch.io/seamless-space-backgrounds)
backgroundImage = PhotoImage(
    file="nebulabkg.png"
)  # Creates a variable to store the background sprite

# Creates a canvas which is a widget used to draw graphics, text, and images
canvas = Canvas(window, width=width, height=height)
canvas.create_image(
    0, 0, anchor="nw", image=backgroundImage
)  # Places background image on the canvas
canvas.pack()

# Spaceship sprites*
# by [Lowich]
# (https://lowich.itch.io/free-spaceship-sprites)
playerImg = PhotoImage(file="spaceship.png")  # Variable for player sprite
# Enemies*
# by [Stay Retro]
# (https://www.spriters-resource.com/pc_computer/angryvideogamenerdadventuresiiassimilation/sheet/170079/)
invaderImg = PhotoImage(file="invader.png")  # Variable for invader sprite

# Outputs score, level, and lives text on screen
scoreText = canvas.create_text(
    10,
    10,
    anchor="nw",
    text=f"Score: {score}",
    fill="limegreen",
    font=("Arial Bold", 14),
)
livesText = canvas.create_text(
    width - 10,
    10,
    anchor="ne",
    text=f"Lives: {lives}",
    fill="limegreen",
    font=("Arial Bold", 14),
)
levelText = canvas.create_text(
    width // 2,
    20,
    anchor="center",
    text=f"Level: {level}",
    fill="limegreen",
    font=("Arial Bold", 14),
)


# Functions
def createPlayer():
    '''
    Creates and initializes the player sprite on the game canvas.

        This function positions the player sprite at the player's
        x and y coordinates on the canvas.
        The sprite is stored in the playerSprite variable for
        future reference and manipulation during gameplay.

            Returns:
               None
    '''
    global playerSprite
    # Creates player sprite in the correct coordinates
    playerSprite = canvas.create_image(playerX, playerY, image=playerImg)


def createInvader():
    '''
    Creates and positions a set of invaders,
    then adds them to the invader list.

        This function generates invader sprites and positions
        them in a row on the canvas based on the number of invaders.
        It stores the x and y coordinates of each invader
        along with its sprite, and adds them to a list for
        tracking during the game.

            Returns:
                None
    '''
    global invaderSprite
    global invaders
    global numInvaders

    # Creates invader sprites
    for i in range(numInvaders):
        invaderCoord = {
            "x": invaderX + (i * 50),
            "y": invaderY,
        }  # Store positions of each invader
        invaderCoord["sprite"] = canvas.create_image(
            invaderCoord["x"], invaderCoord["y"], image=invaderImg
        )  # Outputs invader sprite in the position from line above
        invaders.append(
            invaderCoord
        )  # Add the coordinates of each invader to the invaders list


def shootBullet():
    '''
    Creates and fires a bullet when the player presses the space key.

        This function generates a blue rectangle representing
        a bullet and places it at the front of the player's
        spaceship. The bullet is added to the bullets list for tracking
        and movement.

            Returns:
                None
    '''
    global bullets, shootingCooldown, shootingTimer
    # Stops all movement when the game is paused
    if (gamePaused):
        return
    if (shootingTimer > 0):
        return
    bullet = {
        "x": playerX,
        "y": playerY - 15,
        "rectangle": None,
    }
    # Bullet starts from the front of spaceship
    # Creates shape and dimensions of the bullet,
    # outputs blue rectangles on the canvas
    bullet["rectangle"] = canvas.create_rectangle(
        bullet["x"] - bulletWidth // 2,
        bullet["y"] - bulletHeight,
        bullet["x"] + bulletWidth // 2,
        bullet["y"],
        fill="blue",
    )
    bullets.append(bullet)  # An array to allow multiple bullets on screen
    shootingTimer = shootingCooldown


def updateShootingTimer():
    '''
    Updates the shooting timer each frame.
    This is called in the game loop to
    reduce the cooldown timer and allow shooting
    again once the cooldown is over.

            Returns:
                None
    '''
    global shootingTimer
    if shootingTimer > 0:
        shootingTimer -= 1


def movingBullets():
    """
    Moves each bullet upwards across the screen
    and removes it when it goes off-screen.

        This function iterates through the list of bullets,
        updating their positions by decreasing
        their y-coordinate. Each bullet representation
        (rectangle) is also moved
        on the canvas according to the bullet's speed.
        When a bullet reaches the top of the screen,
        it is removed from both the canvas and the list of active bullets.

            Returns:
                None
    """
    global bullets
# Loops through all of the bullets that have been fired
    for bullet in bullets[:]:
        bullet["y"] = bullet["y"] - bulletSpeed
        canvas.move(
            bullet["rectangle"], 0, -bulletSpeed
        )
        # Moves the bullet '0' along the X axes
        # and the 'bulletSpeed' along the Y axes

        # Removes bullet if it goes off the screen/ above text
        if bullet["y"] < 40:
            canvas.delete(bullet["rectangle"])
            bullets.remove(bullet)


def invaderMovement():
    """
    Moves the invaders across the screen,
    changing direction when they reach the window edges.

        This function loops through each invader and
        moves them horizontally across the screen.
        If an invader reaches the left or right edge of the window,
        they change direction
        and move down the screen.

            Returns:
                None
    """
    global invaders
    global moveInvaderX
    global moveInvaderY

    # Ensures invaders all start within the window
    leftOfWindow = False
    rightOfWindow = False
    for invader in invaders:  # Loops through each invader
        if invader["x"] <= 15:
            leftOfWindow = True
            break
        elif invader["x"] >= width - 15:
            rightOfWindow = True
            break
    if leftOfWindow:
        moveInvaderX = 12
        for invader in invaders:
            invader[
                "y"
            ] += moveInvaderY
            # If invader hits the left edge of the screen,
            # it moves down the screen

    if rightOfWindow:
        moveInvaderX = -12
        for invader in invaders:
            invader[
                "y"
            ] += moveInvaderY
            # If invader hits the right edge of the screen,
            # it moves down the screen

    for invader in invaders:
        invader["x"] += moveInvaderX  # Moves the invader in the X axis
        canvas.coords(
            invader["sprite"], invader["x"], invader["y"]
        )  # Update the sprite's position


def bulletDetection():
    """
    Detects collisions between bullets and invaders.

        The function loops through each bullet
        and invader to check if the bullet
        hits the hitbox of an invader. If a collision
        is detected, both the bullet and
        the invader are removed from the canvas and the game.

            Returns:
                None
    """
    global invaders, bullets, score, invadersKilled
    for bullet in bullets[:]:
        for invader in invaders[:]:
            if (
                invader["x"] - invaderWidth // 2
                <= bullet["x"]
                <= invader["x"] + invaderWidth // 2
                and invader["y"] - invaderHeight // 2
                <= bullet["y"]
                <= invader["y"] + invaderHeight // 2
            ):
                # Deletes the bullet from the canvas
                canvas.delete(bullet["rectangle"])
                # Deletes the invader from the canvas
                canvas.delete(invader["sprite"])
                # Removes bullet from bullets list
                bullets.remove(bullet)
                # Removes invader from invaders list
                invaders.remove(invader)
                score += 10  # Increase score
                # Tracks number of invaders killed
                invadersKilled += 1
                newScore(invadersKilled)  # Updates score
                break


def playerDetection():
    """
    Detects collisions between the player and invaders.

        If an invader reaches the player's level,
        a collision is considered to have occurred.
        In the event of a collision,
        the invader is removed from the canvas, and the player's
        lives are decremented.

            Returns:
                None
    """
    for invader in invaders[:]:
        # If the invader reaches the level of the player,
        # the invader is deleted
        if invader["y"] > playerY - 26:
            canvas.delete(invader["sprite"])
            invaders.remove(invader)
            newLives()


def newScore(invadersKilled):
    """
    Updates the player's score based on the
    number of invaders killed.

        Each time an invader is killed,
        the score is increased by 10 points.
        The score is then updated and displayed on the canvas.

            Parameters:
                invadersKilled (int): The number of invaders that
                have been killed so far.

            Returns:
                None
    """
    global score
    # Increments score by 10 if invader is destroyed
    score = 10 * invadersKilled
    canvas.itemconfig(
        scoreText, text=f"Score: {score}"
    )  # Update the score text on the canvas


def newLives():
    """
    Decreases the player's lives by 1 when a
    collision occurs with an invader or if an invader reaches
    the player's level. Updates the lives display on the canvas.

        This function is called when the player loses a life due
        to a collision with an invader or other
        in-game event. The number of remaining lives is decremented,
        and the updated number of lives is
        shown on the canvas. If the player runs out of lives,
        the player sprite is hidden, and the leaderboard
        is displayed as the game is now over.

            Returns:
                None
    """
    global lives
    if lives > 0:
        # If invader hits player or reaches the
        # player's level, lives is decremented by 1
        lives -= 1
        canvas.itemconfig(
            livesText, text=f"Lives: {lives}"
        )  # Updates the lives text on the canvas
    else:
        canvas.itemconfig(playerSprite, state="hidden")
        showLeaderboard()


def newLevel():
    """
    Prepares the game for the next level by updating
    the level display and clearing existing bullets.

    This function is called when the player advances to a new level.
    It ensures that the game starts fresh with
    no old bullets moving. The bullets are removed from the game.
    Updates levels text to show
    the user the level they are on.

        Returns:
            None
    """
    global level, bullets
    canvas.itemconfig(
        levelText, text=f"Level: {level}"
    )  # Updates the level text on the canvas
    for bullet in bullets[:]:
        canvas.delete(bullet["rectangle"])
    bullets.clear()


def changeDifficulty():
    """
    Updates the game's difficulty as the
    player progresses through levels.

        This function is called when there are no
        enemies left on the screen. It increases the level,
        adds more enemies, and makes the game
        progressively harder. Each level introduces a new set of
        invaders, and the difficulty increases based on the
        current level. A message is displayed
        when the player advances to the next level.

            Returns:
                None
    """
    global moveInvaderX
    global numInvaders
    global level

    if invaders == []:
        # Level is incremented when all of the enemies have been killed
        level += 1
        newLevel()

        # Makes game increasingly harder based on level
        levelUpText = canvas.create_text(
            width // 2,
            height // 2,
            text="Level Up!",
            fill="yellow",
            font=("Arial Bold", 24),
        )  # Outputs 'Level Up!' when next level is reached

        # Pause before proceeding with the next level
        window.after(2000, lambda: canvas.delete(levelUpText))

        if level >= 4:
            numInvaders = 10
            createInvader()
        elif level == 3:
            numInvaders = 9
            createInvader()
        elif level == 2:
            numInvaders = 8
            createInvader()


def createScreen(window, canvas, width, height, imagePath):
    """
    Creates a new canvas for the boss
    key screen and displays an image as a distraction.

    This function initializes a separate canvas.
    When the boss key is activated,
    this canvas will be displayed, showing an
    image of code that hides the
    main game canvas.

        Parameters:
            window: The main application window.
            canvas: The original game canvas.
            width (int): The width of the new boss key canvas.
            height (int): The height of the new boss key canvas.
            imagePath (str): The file path to the image that will
            be displayed on the boss key screen.

    Returns:
        None
    """
    global bossCanvas, bossImage
    bossCanvas = Canvas(window, width=width, height=height)
    bossImage = PhotoImage(file=imagePath)


def toggleBossKey(event, window, gameCanvas):
    """
        Toggles the activation of the boss key to hide
        the game and display a distraction screen.

    When the boss key is activated, the game screen is
    hidden and replaced with an image of code for distraction.
    Additionally, the game is paused. When the boss key
    is deactivated, the game returns to its previous state,
    restoring the game canvas and any paused elements.

            Parameters:
                event: The event triggered by the user, clicking 'b'.
                window: The main application window.
                gameCanvas: The canvas used to display the game elements.

            Returns:
                None
    """
    global bossCanvas, bossKeyActive, gamePaused, pausedText

    if not bossKeyActive:
        # Activating the boss key
        gameCanvas.pack_forget()
        bossCanvas.pack()
        bossCanvas.create_image(0, 0, anchor="nw", image=bossImage)
        bossKeyActive = True

        # Save the current pause state and force pause
        if not gamePaused:
            gamePaused = True
            if pausedText is None:
                pausedText = canvas.create_text(
                    width // 2,
                    (height // 2) - 50,
                    text="Game Paused",
                    fill="Yellow",
                    font=("Arial Bold", 40),
                )
        settingsButton.pack_forget()

    else:
        # Deactivating the boss key
        bossCanvas.pack_forget()
        gameCanvas.pack()
        bossKeyActive = False

        # Restore the previous pause state
        settingsButton.pack(pady=5)
        if pausedText is not None:
            canvas.delete(pausedText)
            pausedText = None
            gamePaused = False
        update()


def saveGame():
    """
    Saves the current state of the game to a file,
    including the player's progress, score, and game elements.

    This function writes the game data into a file savefile.txt,
    allowing players to resume their progress later.
        The saved game state includes:
            Player's username, position, score,
            lives, level, and number of invaders.
            The number of invaders killed and their
            positions on the screen.
            The positions of the bullets currently in the game.

            Returns:
                None
    """
    global gamePaused, invadersKilled

    try:
        saveFile = open("savefile.txt", "w")
        saveFile.write(f"{playerUsername}\n")
        saveFile.write(f"{playerX},{playerY}\n")
        saveFile.write(f"{score}\n")
        saveFile.write(f"{lives}\n")
        saveFile.write(f"{level}\n")
        saveFile.write(f"{numInvaders}\n")
        saveFile.write(f"{invadersKilled}\n")

        # Save all invader positions
        for invader in invaders:
            saveFile.write(f"{invader['x']},{invader['y']}\n")
        saveFile.write("END\n")  # Mark end of invaders

        # Save all bullet positions
        for bullet in bullets:
            saveFile.write(f"{bullet['x']},{bullet['y']}\n")
        saveFile.write("END\n")  # Mark end of bullets

        saveFile.close()  # Close the file
        print("Game saved successfully!")

        # Delete canvas elements
        for invader in invaders:
            canvas.delete(invader["sprite"])
        for bullet in bullets:
            canvas.delete(bullet["rectangle"])

        gamePaused = True
        canvas.itemconfig(
            playerSprite, state="hidden"
        )  # Hide the spaceship so that it is not deleted.
        showStartScreen()

    except IOError as e:
        print(
            f"Error saving the game: {e}"
        )  # If the game cannot be saved an error occurs


def loadGame():
    """
    Loads the saved game state from a file,
    including the player position, score, lives,
    level, invaders, bullets, and invaders killed.

        This function reads the game data from a
        filesavefile.txt, restores the state of the game by:
            Updating the player's position, score, lives,
            level, and invader information.
            Reloading the invader and bullet sprites on the canvas.
            Rebinding the controls to allow for continued gameplay.

        Returns:
            None
    """
    global playerX, playerY, score, lives, level, numInvaders
    global invaders, bullets, playerUsername, gamePaused, startButtons, frame
    global playerSprite, invadersKilled
    gamePaused = False  # Unpauses the game
    try:
        saveFile = open("savefile.txt", "r")
        lines = saveFile.readlines()  # Read all lines into a list
        saveFile.close()

        if not lines:
            print("Error: Save file is empty!")
            return  # Exit the function if the file is empty

        # Delete canvas elements
        if frame is not None:
            frame.destroy()

        canvas.delete("start_screen")
        canvas.delete("leaderboard")

        for button in startButtons:
            # Removes the button or widget from the window
            button.destroy()
        startButtons = []

        # Load game state values
        playerUsername = lines[0].strip()
        playerX, playerY = map(int, lines[1].strip().split(","))
        score = int(lines[2].strip())
        lives = int(lines[3].strip())
        level = int(lines[4].strip())
        numInvaders = int(lines[5].strip())
        invadersKilled = int(lines[6].strip())

        # Clear existing invaders and bullets from the canvas
        for invader in invaders:
            canvas.delete(invader["sprite"])
        invaders = []

        for bullet in bullets:
            canvas.delete(bullet["rectangle"])
        bullets = []

        # Load invaders
        i = 7  # Start after the invadersKilled line
        while lines[i].strip() != "END":
            x, y = map(int, lines[i].strip().split(","))
            invaderCoord = {
                "x": x,
                "y": y,
                "sprite": canvas.create_image(x, y, image=invaderImg),
            }
            invaders.append(invaderCoord)
            i += 1

        # Load bullets
        i += 1  # Skip "END"
        while lines[i].strip() != "END":
            x, y = map(int, lines[i].strip().split(","))
            bullet = {
                "x": x,
                "y": y,
                "rectangle": canvas.create_rectangle(
                    x - bulletWidth // 2,
                    y - bulletHeight,
                    x + bulletWidth // 2,
                    y,
                    fill="blue",
                ),
            }
            bullets.append(bullet)
            i += 1

        # Update canvas elements to reflect loaded values
        canvas.itemconfig(scoreText, text=f"Score: {score}")
        canvas.itemconfig(livesText, text=f"Lives: {lives}")
        canvas.itemconfig(levelText, text=f"Level: {level}")

        # Text reappears when the game is reloaded
        canvas.itemconfig(scoreText, state="normal")
        canvas.itemconfig(livesText, state="normal")
        canvas.itemconfig(levelText, state="normal")

        # Keyboard bindings
        window.bind(leftKey, playerLeft)
        window.bind(rightKey, playerRight)
        window.bind(shootKey, lambda event: shootBullet())
        window.bind("p", pauseGame)
        window.bind("c", lambda event: cheatLives())
        window.bind("v", lambda event: cheatSpeed())
        window.bind("w", lambda event: cheatBullets())
        window.bind("b", lambda event: toggleBossKey(event, window, canvas))
        window.bind("s", lambda event: saveGame())
        # Press 's' to save and exit the game

        if playerSprite is None:
            playerSprite = canvas.create_image(
                playerX, playerY, image=playerImg
            )  # If sprite doesnt exist then create a new one
        else:
            canvas.coords(
                playerSprite, playerX, playerY
            )  # Update the position of the existing player sprite
            canvas.itemconfig(playerSprite, state="normal")

        print(f"Game loaded successfully! Welcome back, {playerUsername}")
        update()  # Resume the game loop
        createScreen(
            window, canvas, width, height, "boss_screen.png"
        )  # Allows boss key to be pressed

    except IOError as e:
        print(f"Error loading the game: {e}")


def submitUsername():
    """
    Handles the process of submitting the username
    entered by the player, validates the input,
    and starts the game if the username is valid.

    This function retrieves the username from the
    input field, validates it, and if it's not empty,
    it proceeds to hide the username entry widgets
    and start the game. If the username is invalid,
    it displays an error message prompting the player
    to enter a valid username.

        Returns:
            None
    """
    global playerUsername
    # Retrieve the entered username
    playerUsername = usernameEntry.get().strip()
    if not playerUsername:
        usernameLabel.config(text="Enter a valid username:", fg="red")
        return  # Do not proceed if username is empty

    # Hide username entry widgets
    usernameEntry.pack_forget()
    usernameLabel.pack_forget()
    submitButton.pack_forget()

    startGame()


def saveLeaderboard(username, score):
    """
    Saves a player's username and score to the leaderboard file.

    This function appends the given username and score
    to a file called leaderboard.txt. Each entry is written
    as a new line. The function handles potential errors
    when writing to the file
    and prints an error message if something goes wrong.

        Parameters:
            username (str): The player's username to be saved.
            score (int): The player's score to be saved.
    """
    try:
        with open("leaderboard.txt", "a") as lbFile:
            lbFile.write(
                f"{username},{score}\n"
            )  # Adds the username and score to the leaderboard
    except Exception as e:
        print(f"Error saving leaderboard: {e}")


def loadLeaderboard():
    """
    Loads the leaderboard from a file and returns the top 5 scores.

    This function attempts to read the leaderboard from
    a file called leaderboard.txt. Each line in the file
    contains a player's username and their corresponding score.
    The function processes the file
    to extract the scores, sorts them in descending order,
    and returns the top 5 entries.

        Returns:
            list: A list of tuples, where each tuple contains
            a username (str) and a score (int),
            sorted by score in descending order.
            OR:
            list: Empty list if the leaderboard file does not exist
    """
    try:
        with open("leaderboard.txt", "r") as lbFile:
            scores = [
                line.strip().split(",") for line in lbFile.readlines()
            ]  # Read username and score
            scores = [(name, int(score)) for name, score in scores]
            scores.sort(
                key=lambda x: x[1], reverse=True
            )  # Sort by score in descending order
            return scores[:5]  # Return the top 5 entries
    except FileNotFoundError:
        return []


def showLeaderboard():
    """
    Displays the leaderboard on the game canvas.

    This function retrieves the top scores from the
    leaderboard data and displays
    them on the game screen. It ensures that any
    existing leaderboard content is
    cleared before rendering the new leaderboard.

        Returns:
            None
    """
    leaderboard = loadLeaderboard()
    # Clear any existing leaderboard text
    canvas.delete("leaderboard")

    canvas.create_text(
        width // 2,
        height // 5,
        text="Leaderboard",
        fill="yellow",
        font=("Arial Bold", 24),
        tags="leaderboard",
    )

    # Display top 5 scores, with equal distance between them
    for idx, (name, score) in enumerate(leaderboard):
        canvas.create_text(
            width // 2,
            height // 5 + (30 * (idx + 1)),
            text=f"{idx + 1}. {name}: {score}",
            fill="limegreen",
            font=("Arial", 20),
            tags="leaderboard",
        )


def update():
    """
    Continuously updates the game state and
    ensures smooth gameplay.

    This function handles the ongoing mechanics of
    the game, such as updating positions,
    checking for collisions, and handling game
    difficulty adjustments. It is called
    repeatedly using window.after to create a
    loop that keeps the game running smoothly.

        Returns:
            None
    """
    if lives == 0:
        saveLeaderboard(playerUsername, score)
        showLeaderboard()
        showGameOver()
        return
    # If the game is paused then it will no longer update
    if gamePaused:
        return
    # Ensures movement is continuous
    changeDifficulty()
    movingBullets()
    invaderMovement()
    # Constantly checks for collisions
    bulletDetection()
    playerDetection()
    updateShootingTimer()

    window.after(40, update)  # Update called after 40ms to allow movement


def showStartScreen():
    """
    Displays the start screen with options to enter a
    username, start a new game, or load a saved game.

    This function sets up the main menu screen for the game,
    which includes elements like
    the game title, a username input field, buttons to start
    or load a game, and the leaderboard.
    Additionally, it unbinds gameplay-related keys to prevent
    triggering game actions while interacting with the start screen.

        Returns:
            None
    """
    global usernameEntry, usernameLabel, submitButton, frame
    global loadButton, startButtons, playAgainButton
    canvas.delete("game_over")
    if playAgainButton:  # Check if the playAgainButton exists
        playAgainButton.destroy()
    # Display game title
    canvas.create_text(
        width // 2,
        height // 8,
        text="Laser Invasion",
        fill="red",
        font=("Arial Bold", 36),
        tags="start_screen",
    )
    # Hides unwanted text
    canvas.itemconfig(scoreText, state="hidden")
    canvas.itemconfig(livesText, state="hidden")
    canvas.itemconfig(levelText, state="hidden")
    # Creates a frame to structure the username feature
    frame = Frame(window, width=300, height=200, relief="solid", borderwidth=2)
    frame.place(
        relx=0.5, rely=0.75, anchor="center"
    )  # Place the frame in the center of the window

    # Add username label and entry field inside the frame
    usernameLabel = Label(
        frame,
        text="Enter Username:",
        font=("Arial", 14))
    usernameLabel.pack(pady=5)
    usernameEntry = Entry(frame, font=("Arial", 14))
    usernameEntry.pack(pady=5)
    submitButton = Button(
        frame,
        text="Start",
        command=lambda: submitUsername())
    submitButton.pack(pady=10)

    # Creates a load button to call the function loadGame
    loadButton = Button(window, text="Load Game", command=loadGame)
    loadButton.pack(pady=20)
    loadButton.place(relx=0.1, rely=0.85, anchor="center")
    loadButton._tag = "load_button"

    showLeaderboard()
    startButtons.extend(
        [submitButton, usernameEntry, usernameLabel, loadButton]
    )  # Adds all of the buttons on the start page to a list for easy removal

    # Unbinds keys to allow a Player to enter their username,
    # without triggering any cheats/ functions
    window.unbind(leftKey)
    window.unbind(rightKey)
    window.unbind(shootKey)
    window.unbind("p")
    window.unbind("c")
    window.unbind("v")
    window.unbind("w")
    window.unbind("b")
    window.unbind("s")


def startGame():
    '''
    Initializes the game and removes elements from the start screen.

    This function is called when the player chooses
    to begin the game. It clears all
    elements from the start screen, such as buttons,
    labels, and the leaderboard, and
    sets up the game environment by binding keys to actions,
    displaying game status
    elements, and creating the player and invaders. The game
    then begins its main update loop.

        Returns:
            None
    '''
    global startButtons

    # Remove all start screen elements
    for widget in startButtons:
        widget.destroy()  # Removes the button or widget from the window
    startButtons = []

    if frame is not None:
        frame.destroy()

    # Destroy the username entry, label, and submit button
    if "usernameLabel" in globals():
        usernameLabel.destroy()
    if "usernameEntry" in globals():
        usernameEntry.destroy()
    if "submitButton" in globals():
        submitButton.destroy()

    # Delete canvas elements
    canvas.delete("start_screen")
    canvas.delete("leaderboard")

    # Outputs text on the window
    canvas.itemconfig(scoreText, state="normal")
    canvas.itemconfig(livesText, state="normal")
    canvas.itemconfig(levelText, state="normal")

    # Binds the keys once the game has started
    window.bind(leftKey, playerLeft)
    window.bind(rightKey, playerRight)
    window.bind(shootKey, lambda event: shootBullet())
    window.bind("p", pauseGame)
    window.bind("c", lambda event: cheatLives())
    window.bind("v", lambda event: cheatSpeed())
    window.bind("w", lambda event: cheatBullets())
    window.bind("b", lambda event: toggleBossKey(event, window, canvas))
    window.bind("s", lambda event: saveGame())

    # Initialize the game
    createPlayer()
    createInvader()
    createScreen(window, canvas, width, height, "boss_screen.png")
    update()


def showGameOver():
    """
    Displays the game over screen and provides an
    option to restart the game.

    This function is called when the player loses all
    lives or the game ends. It displays
    a Game Over message in the center of the screen and
    creates a Play Again button
    for the player to restart the game.

        Returns:
            None
    """
    global playAgainButton

    canvas.create_text(
        width // 2,
        height // 8,
        text="Game Over",
        fill="red",
        font=("Arial Bold", 36),
        tags="game_over",
    )

    # Create the Play Again button
    playAgainButton = Button(window, text="Play Again", command=resetGame)
    playAgainButton.pack(pady=20)
    playAgainButton.place(relx=0.5, rely=0.8, anchor="center")
    playAgainButton.tag = "playAgainButton"


def resetGame():
    """
    Resets the game to its initial state and displays
    the start screen.

    This function is triggered when the player wants to
    play again after a game over.
    It clears the current game elements, resets the player's
    progress, and initializes the game UI
    and variables to their starting values. Finally,
    it displays the start screen to allow the user to begin
    a new game or load a previous game.

        Returns:
            None
    """
    global invaders, bullets, score, lives, level
    global numInvaders, playerX, playerY, gamePaused, invadersKilled

    # Delete the "Game Over" text and Play Again button if they exist
    canvas.delete("game_over")
    if playAgainButton:
        playAgainButton.destroy()

    # Clear the game elements
    for invader in invaders:
        canvas.delete(invader["sprite"])
    for bullet in bullets:
        canvas.delete(bullet["rectangle"])

    # Reset game variables to start fresh
    invaders = []
    bullets = []
    score = 0
    lives = 3
    level = 1
    numInvaders = 6
    invadersKilled = 0
    playerX, playerY = width // 2, height - playerHeight
    gamePaused = False
    canvas.coords(playerSprite, playerX, playerY)

    # Reset the User Interface
    canvas.itemconfig(scoreText, text=f"Score: {score}")
    canvas.itemconfig(livesText, text=f"Lives: {lives}")
    canvas.itemconfig(levelText, text=f"Level: {level}")

    # Call the start screen to begin a new game
    showStartScreen()


def playerLeft(event):
    """
    Moves the player sprite to the left when
    the corresponding key is pressed.

    This function updates the player's x-coordinate
    to move the player sprite to the left,
    ensuring that the player cannot move beyond the
    left boundary of the game window.
    Movement is disabled if the game is paused.

        Parameters:
            event: The keypress event triggering the movement.

    """
    global playerX
    if gamePaused:  # stop player movement when game is paused
        return
    if playerX > 15:
        playerX = playerX - 15  # stops player moving outside of window
        canvas.coords(
            playerSprite, playerX, playerY
        )  # updates coordinates of player when key pressed


def playerRight(event):
    """
    Moves the player sprite to the right when the
    corresponding key is pressed.

    This function updates the player's x-coordinate to
    move the player sprite to the right,
    ensuring that the player cannot move beyond the right
    boundary of the game window.
    Movement is disabled if the game is paused.

        Args:
            event: The keypress event triggering the movement.
    """
    global playerX
    if gamePaused:  # stop player movement when game is paused
        return

    if playerX < width - 15:
        playerX = playerX + 15  # stops player moving outside of window
        canvas.coords(
            playerSprite, playerX, playerY
        )  # updates coordinates of player when key pressed


def pauseLevel(duration):
    """
    Temporarily pauses the game for a specified duration before
    resuming the game loop.

    This function delays the execution of the update() function,
    creating a pause
    between levels. It is used to provide a break in the gameplay.

        Args:
            duration (int): The duration of the pause in milliseconds
            before resuming the game loop.
    """
    window.after(duration, update)


def pauseGame(event):  # function to pause the game completely
    """
    Toggles the game's paused state when the p key is pressed.

    This function pauses the game when the p key is pressed
    and displays a "Game Paused"
    message on the screen. Pressing p again unpauses the game,
    removing the pause message.
    If the game is unpaused, the game loop is resumed by
    calling update().

        Args:
        event: The event object generated by the key press.
    """
    global gamePaused, pausedText
    gamePaused = not gamePaused
    if gamePaused:
        if pausedText is None:
            pausedText = canvas.create_text(
                width // 2,
                (height // 2) - 50,
                text="Game Paused",
                fill="Yellow",
                font=("Arial Bold", 40),
            )  # outputs a message when the game is paused
    else:
        if pausedText is not None:
            # Deletes pause message when the game is resumed
            canvas.delete(pausedText)
            pausedText = None
    if not gamePaused:
        update()


def cheatLives():
    """
        Increases the player's lives by 3.

    When activated, this cheat function adds 3 extra
    lives to the player, making it easier to continue
    the game. It also updates the on-screen display of
    the player's lives count to reflect the change.

        Returns:
            None
    """
    global lives
    lives += 3
    # Update lives display
    canvas.itemconfig(livesText, text=f"Lives: {lives}")


def cheatSpeed():
    """
    Reduces the speed of the invaders' movement.

    When activated, this cheat function modifies
    the global variables controlling the invaders'
    horizontal and vertical movement speeds.
    Making it easier for the player to kill the invaders.

        Returns:
            None
    """
    global moveInvaderX, moveInvaderY
    moveInvaderX = moveInvaderX // 5


def cheatBullets():
    """
    Toggles the size and speed of the player's
    bullets as a cheat mode.

    When activated, this function changes the
    bullet's size and speed:
        If the cheat mode is off, the bullets
        have a smaller size and slower speed.
        If the cheat mode is on, the bullets have
        a larger size and faster speed.

    This cheat is triggered each time the function is called,
    alternating between the normal and super bullets.
        Returns:
            None
    """
    global bulletHeight, bulletWidth, bulletSpeed, largeBullet
    largeBullet = not largeBullet
    if largeBullet:
        bulletSpeed = 15
        bulletHeight = 20
        bulletWidth = 15
    else:
        bulletSpeed = 7
        bulletHeight = 10
        bulletWidth = 5


def openSettings():
    """
    Opens the settings menu allowing the player
    to remap the game control keys.

    This function creates a new top-level window
    where the player can change their key bindings
    for the left movement, right movement, and shoot actions.
    It displays the current key settings
    and allows the player to input their desired keys.
    Once the user has entered their new key bindings,
    they can save them using the provided button.

    The settings window contains:
        An input field for remapping the Left key.
        An input field for remapping the Right key.
        An input field for remapping the Shoot key.

    After the user enters new key bindings, they can save
    their changes by clicking the Save keybinds button,
    which will apply the changes and close the settings window.

        Returns:
            None
    """
    # Creates a new top-level window for settings
    settingsWindow = Toplevel(window)
    settingsWindow.title("Game Settings")

    Label(settingsWindow, text="Left Key:").grid(
        row=0, column=0
    )  # Outputs label for the left key to be remapped
    leftKeyInput = Entry(settingsWindow)  # Allows user input for Left key
    leftKeyInput.insert(0, leftKey)  # Insert the current left key binding
    # Position the players input in the grid
    leftKeyInput.grid(row=0, column=1)

    Label(settingsWindow, text="Right Key:").grid(
        row=1, column=0
    )  # Outputs a label for the right key to be remapped
    rightKeyInput = Entry(settingsWindow)  # Player input for Right key
    rightKeyInput.insert(0, rightKey)  # Insert the current right key binding
    # Position the input in the grid
    rightKeyInput.grid(row=1, column=1)

    Label(settingsWindow, text="Shoot Key:").grid(
        row=2, column=0
    )  # Outputs label for the shoot key to be remapped
    shootKeyInput = Entry(settingsWindow)  # Allows user input for shooting key
    shootKeyInput.insert(
        0, shootKey
    )  # Updates variable shootKeyEntry to the current Shoot key binding
    # Position the player input in the grid
    shootKeyInput.grid(row=2, column=1)

    # function to save the new key binds
    def saveSettings():
        """
            Saves the updated key bindings chosen by the player.

        This function retrieves the key inputs from the settings window,
        unbinds the previous key bindings,
        and then binds the new keys to the player movement
        and shooting actions. Once the new bindings are
        applied, it closes the settings window.

        Key bindings:
            Left arrow key: Moves the player left.
            Right arrow key: Moves the player right.
            Spacebar: Fires the player's bullet.

        This function is called when the player clicks the Save
        keybinds button in the settings window.

        Returns:
            None
        """
        global leftKey, rightKey, shootKey

        # Get method retrieves the updated key bindings
        # from openSettings function
        leftKey = leftKeyInput.get()
        rightKey = rightKeyInput.get()
        shootKey = shootKeyInput.get()

        # Unbind the old key bindings to prevent dual keybinds
        window.unbind("<Left>")
        window.unbind("<Right>")
        window.unbind("<space>")

        # Binds the players input keys to the action or movement chosen
        window.bind(leftKey, playerLeft)
        window.bind(rightKey, playerRight)
        window.bind(shootKey, lambda event: shootBullet())
        settingsWindow.destroy()  # Close the settings window after saving

    # Create a button to save the new key settings
    Button(settingsWindow, text="Save keybinds", command=saveSettings).grid(
        row=3, column=0, columnspan=2
    )


# Creates a button on the game window to open the settings menu
settingsButton = Button(window, text="Settings", command=openSettings)
settingsButton.pack(
    pady=5
)  # Vertical padding so that the settings menu shows on window

# Start the game
showStartScreen()
window.mainloop()  # Keeps the window open so the game can run
