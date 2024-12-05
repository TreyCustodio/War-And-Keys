"""
A Singleton Sprite Manager class
Author: Liz Matthews, 7/21/2023

Provides on-demand loading of images for a pygame program.
Will load entire sprite sheets if given an offset.

"""

from pygame import image, Surface, Rect, SRCALPHA, transform
from os.path import join
from utils import vec

class SpriteManager(object):
   """A singleton factory class to create and store sprites on demand."""
   
   # The singleton instance variable
   _INSTANCE = None
   
   @classmethod
   def getInstance(cls):
      """Used to obtain the singleton instance"""
      if cls._INSTANCE == None:
         cls._INSTANCE = cls._SM()
      
      return cls._INSTANCE
   
   
      
   # Do not directly instantiate this class!
   class _SM(object):
      """An internal SpriteManager class to contain the actual code. Is a private class."""
      
      # Folder in which images are stored
      _IMAGE_FOLDER = "images"
      
      _ENEMY_FOLDER = "images\\enemies"

      _ROOM_FOLDER = "images\\levels"

      

      # Static information about the sprite sizes of particular image sheets.
      _SPRITE_SIZES = {

         ## Titles
         "pause.png":(56*2,14*2),
         "chars.png":(8,16), 
         "trey_logo.png":(321,58),
         "title.png":(160,96),

         ## Backgrounds
         "bg_1.png":(320,180),

         ## Player
         "player_1.png":(32,32),
         "player_2.png":(32,32),
         
         ## Enemies
         "ground_1.png":(64,32),
         "ground_2.png":(179, 174),
         "ground_3.png":(179, 174),
         "ground_4.png":(179, 174),
         "ground_5.png":(179, 174),

         "flyer_3.png":(141, 136),
         "flyer_4.png":(56, 59),
         "flyer_5.png":(67, 82),
         "flyer_6.png":(90, 76),
      }
      
      # A default sprite size
      _DEFAULT_SPRITE = (16,16)
      
      # A list of images that require to be loaded with transparency
      _TRANSPARENCY = ["pause.png", "player_1.png", "player_2.png", "bullet.png",
                       "ground_1.png", "ground_2.png", "ground_3.png", "ground_4.png", "ground_5.png",
                       ]
      
      _TRANSPARENCY.extend([f"flyer_{i}.png" for i in range(1, 7)])
      
      # A list of images that require to be loaded with a color key
      _COLOR_KEY = ["chars.png"]
      
      def __init__(self):
         # Stores the surfaces indexed based on file name
         # The values in _surfaces can be a single Surface
         #  or a two dimentional grid of surfaces if it is an image sheet
         self._surfaces = {}      
      
      def __getitem__(self, key):
         return self._surfaces[key]
   
      def __setitem__(self, key, item):
         self._surfaces[key] = item
      
      def getSize(self, fileName):
         spriteSize = SpriteManager._SM._SPRITE_SIZES.get(fileName,
                                             SpriteManager._SM._DEFAULT_SPRITE)
         return spriteSize
      
      def getSprite(self, fileName, offset=None, enemy = False, scale = False):
         # If this sprite has not already been loaded, load the image from memory
         
         if fileName not in self._surfaces.keys():
            
            self._loadImage(fileName, offset != None, scale=scale)
         
         # If this is an image sheet, return the correctly offset sub surface
         if offset != None:
            return self[fileName][offset[1]][offset[0]]
         
         # Otherwise, return the sheet created
         return self[fileName]
      
      def getLevel(self, fileName):
         if fileName not in self._surfaces.keys():
            self._loadImage(fileName, level = True)
         return self[fileName]
      
      def getFx(self, room_dir, fileName, offset = None):
         if fileName not in self._surfaces.keys():
            self._loadFx(room_dir, fileName, offset != None)
         else:
            delattr
            self._loadFx(room_dir, fileName, offset != None)
         
         if offset != None:
            return self[fileName][offset[1]][offset[0]]
         return self[fileName]
      
      def getEnemy(self, fileName, direction):
         if fileName not in self._surfaces.keys():
            self._loadImage(fileName, sheet = True, enemy = True)
         return self[fileName][direction][0]
      
      def _loadImage(self, fileName, sheet=False, level = False, enemy = False, scale = False):
         # Load the full image
         if level:
            fullImage = image.load(join(SpriteManager._SM._ROOM_FOLDER, fileName))
         elif enemy:
            fullImage = image.load(join(SpriteManager._SM._ENEMY_FOLDER, fileName))
         else:
            fullImage = image.load(join(SpriteManager._SM._IMAGE_FOLDER, fileName))
         
         if scale:
            fullImage = transform.scale2x(fullImage)
         
         self._loadRoutine(fullImage, fileName, sheet)
         
      def _loadFx(self, room_dir, fileName, sheet = False):
          effects_folder = SpriteManager._SM._ROOM_FOLDER + "\\"+room_dir
          fullImage = image.load(join(effects_folder, fileName))
          self._loadRoutine(fullImage, fileName, sheet, True)

      def _loadRoutine(self, fullImage, fileName, sheet = False, transparent = False):
         if not transparent:
            # Look up some information about the image to be loaded
            transparent = fileName in SpriteManager._SM._TRANSPARENCY
         colorKey = fileName in SpriteManager._SM._COLOR_KEY
         
         # Detect if a transparency is needed
         if transparent:
            fullImage = fullImage.convert_alpha()
         else:
            fullImage = fullImage.convert()
         
         # If the image to be loaded is an image sheet, split it up based on the sprite size
         if sheet:
            
            #  Array of sprites
            self[fileName] = []
            
            # Try to get the sprite size, use the default size if it is not stored
            spriteSize = self.getSize(fileName)

            # See how big the sprite sheet is
            sheetDimensions = fullImage.get_size()
            
            # Iterate over the entire sheet, increment by the sprite size
            for y in range(0, sheetDimensions[1], spriteSize[1]):
               self[fileName].append([])
               for x in range(0, sheetDimensions[0], spriteSize[0]):
                  
                  # If we need transparency
                  if transparent:
                     sprite = Surface(spriteSize, SRCALPHA, 32)
                  else:
                     sprite = Surface(spriteSize)
                  
                  sprite.blit(fullImage, (0,0), Rect((x,y), spriteSize))
                  
                  # If we need to set the color key
                  if colorKey:
                     sprite.set_colorkey(sprite.get_at((0,0)))
                  
                  # Add the sprite to the end of the current row
                  self[fileName][-1].append(sprite)
         else:
            # Not a sprite sheet, full image is what we wish to store
            self[fileName] = fullImage
               
            # If we need to set the color key
            if colorKey:
               self[fileName].set_colorkey(self[fileName].get_at((0,0)))
            
         