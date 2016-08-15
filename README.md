# catcom

![alt text](https://github.com/Meepasaurus/catcom/blob/master/assets/catcom1.jpg?raw=true "catcom screenshot")

- Python Super Puzzle Fighter clone built with pygame in 2010

- group project with:
 
 - me (board structure, basic block movement, and garbage blocks)
 
 - Thanat Owlarn (block generation, rotation, and additional game logic)
 
 - Alice Yang (networking and art)

## Installation

- Requires Python 2.7 and pygame-1.9.1.win32-py2.7.msi which can be found here: http://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi

- Run ```python -Main.py``` to start game.

- Music has been removed to respect copyright, but it can be replaced by uncommenting the following lines in Main.py and placing a bgm.mp3 file in the same directory:

```
pygame.mixer.init()
pygame.mixer.music.load('bgm.mp3')
pygame.mixer.music.play()
```

## Play

- ASD and arrow keys for local mode movement, W/up arrow to rotate piece.

-Networked play only works over local networks.

-Use circular pieces to break square ones of the same color. Large chains (4+ blocks) will send garbage blocks to opponent, which require 5 piece placements until they become available for breaking.

## Extra Notes

- Assets include unusued character art.
