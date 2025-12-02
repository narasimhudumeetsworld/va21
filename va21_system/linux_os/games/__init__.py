#!/usr/bin/env python3
"""
VA21 Research OS - Classic Games Suite
========================================

Bundled classic games for VA21 OS, inspired by how Microsoft
bundled games with Windows OS.

Featured Games:
- Zork I: The Great Underground Empire
- Zork II: The Wizard of Frobozz
- Zork III: The Dungeon Master

These legendary text adventure games from Infocom (1980-1982)
are the inspiration for VA21's own Zork-style interface.

Historical Source:
- https://github.com/historicalsource/zork1
- https://github.com/historicalsource/zork2
- https://github.com/historicalsource/zork3

Om Vinayaka - Where adventure meets research.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════════════════════════
# GAME DATA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GameInfo:
    """Information about a game."""
    id: str
    name: str
    year: int
    description: str
    author: str
    source_url: str
    story_file: str  # Z-machine story file
    icon: str = "🎮"


# Classic Zork Trilogy
ZORK_GAMES = {
    "zork1": GameInfo(
        id="zork1",
        name="Zork I: The Great Underground Empire",
        year=1980,
        description="""
ZORK I: The Great Underground Empire
=====================================

"West of House. You are standing in an open field west of a white house,
with a boarded front door. There is a small mailbox here."

The legendary adventure begins! Explore the Great Underground Empire,
solve puzzles, collect treasures, and try not to get eaten by a grue.

Originally created by Tim Anderson, Marc Blank, Bruce Daniels, and
Dave Lebling at MIT in 1977-1979, released by Infocom in 1980.

This is where interactive fiction began.
""",
        author="Infocom (Tim Anderson, Marc Blank, Bruce Daniels, Dave Lebling)",
        source_url="https://github.com/historicalsource/zork1",
        story_file="zork1.z3",
        icon="🏰"
    ),
    
    "zork2": GameInfo(
        id="zork2",
        name="Zork II: The Wizard of Frobozz",
        year=1981,
        description="""
ZORK II: The Wizard of Frobozz
===============================

The adventure continues in the deeper regions of the Great Underground
Empire. The Wizard of Frobozz, once a respected enchanter, has gone
quite mad and now roams the caverns casting spells on unwary adventurers.

Can you survive the wizard's mischief and recover more treasures from
the Empire?

Released by Infocom in 1981.
""",
        author="Infocom (Marc Blank, Dave Lebling)",
        source_url="https://github.com/historicalsource/zork2",
        story_file="zork2.z3",
        icon="🧙"
    ),
    
    "zork3": GameInfo(
        id="zork3",
        name="Zork III: The Dungeon Master",
        year=1982,
        description="""
ZORK III: The Dungeon Master
=============================

The final chapter of the Zork trilogy. You have conquered the depths
of the Great Underground Empire, evaded the Wizard of Frobozz, and
now you stand at the edge of the Endless Stair.

The Dungeon Master awaits. Will you prove yourself worthy of joining
the Circle of Enchanters?

Released by Infocom in 1982. A fitting conclusion to one of gaming's
greatest trilogies.
""",
        author="Infocom (Marc Blank, Dave Lebling)",
        source_url="https://github.com/historicalsource/zork3",
        story_file="zork3.z3",
        icon="👑"
    )
}


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN MINI ZORK (Pure Python implementation)
# ═══════════════════════════════════════════════════════════════════════════════

class MiniZork:
    """
    A mini Zork-inspired text adventure built into VA21.
    This serves as a tutorial and demonstration of the interface.
    """
    
    def __init__(self):
        self.current_room = "start"
        self.inventory = []
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.lamp_on = False
        self.grue_warning = 0
        
        # Room definitions
        self.rooms = {
            "start": {
                "name": "West of House",
                "description": """You are standing in an open field west of a white house,
with a boarded front door. There is a small mailbox here.
A path leads north around the house.""",
                "exits": {"north": "north_house", "south": "forest", "east": "front_door"},
                "items": ["mailbox"],
                "dark": False
            },
            "front_door": {
                "name": "Front Door",
                "description": "The door is boarded shut. You cannot enter this way.",
                "exits": {"west": "start"},
                "items": [],
                "dark": False
            },
            "north_house": {
                "name": "North of House",
                "description": """You are facing the north side of a white house.
There is no door here, and all the windows are boarded up.
A path leads around the house to the west and east.""",
                "exits": {"west": "start", "east": "behind_house", "north": "forest_path"},
                "items": [],
                "dark": False
            },
            "behind_house": {
                "name": "Behind House",
                "description": """You are behind the white house. A path leads into the forest
to the east. In one corner of the house there is a small window which is open.""",
                "exits": {"west": "north_house", "east": "forest", "in": "kitchen"},
                "items": [],
                "dark": False
            },
            "kitchen": {
                "name": "Kitchen",
                "description": """You are in the kitchen of the white house. A table seems to
have been used recently for the preparation of food. A passage leads to the west
and a dark staircase can be seen leading upward. A dark chimney leads down.""",
                "exits": {"out": "behind_house", "west": "living_room", "up": "attic", "down": "cellar"},
                "items": ["sack", "bottle"],
                "dark": False
            },
            "living_room": {
                "name": "Living Room",
                "description": """You are in the living room. There is a doorway to the east,
a wooden door with strange gothic lettering to the west, which appears to be nailed shut,
a trophy case, and a large oriental rug in the center of the room.
Above the trophy case hangs an elvish sword of great antiquity.""",
                "exits": {"east": "kitchen"},
                "items": ["sword", "lamp", "rug"],
                "dark": False
            },
            "cellar": {
                "name": "Cellar",
                "description": """You are in a dark and damp cellar with a narrow passageway
leading north, and a crawlway to the south. On the west is the bottom of a steep
metal ramp which is unclimbable.""",
                "exits": {"up": "kitchen", "north": "troll_room"},
                "items": [],
                "dark": True
            },
            "troll_room": {
                "name": "Troll Room",
                "description": """This is a small room with passages to the east and south
and a forbidding hole leading west. Bloodstains and deep scratches (perhaps made by an
axe) mar the walls. A nasty-looking troll, brandishing a bloody axe, blocks all passages
out of the room.""",
                "exits": {"south": "cellar", "east": "maze_entrance"},
                "items": ["troll"],
                "dark": True,
                "troll_alive": True
            },
            "maze_entrance": {
                "name": "Maze Entrance",
                "description": """This is the entrance to a maze of twisty little passages,
all alike. The way back is to the west.""",
                "exits": {"west": "troll_room"},
                "items": ["treasure"],
                "dark": True
            },
            "attic": {
                "name": "Attic",
                "description": """This is the attic. The only exit is a stairway leading down.
A large coil of rope is lying in the corner. A nasty knife is lying here.""",
                "exits": {"down": "kitchen"},
                "items": ["rope", "knife"],
                "dark": False
            },
            "forest": {
                "name": "Forest",
                "description": """This is a forest, with trees in all directions. To the east,
there appears to be sunlight.""",
                "exits": {"north": "start", "east": "clearing", "south": "forest", "west": "forest"},
                "items": [],
                "dark": False
            },
            "forest_path": {
                "name": "Forest Path",
                "description": """This is a path winding through a dimly lit forest. The path
heads north-south here. One particularly large tree with some low branches stands here.""",
                "exits": {"south": "north_house", "north": "clearing", "up": "tree"},
                "items": [],
                "dark": False
            },
            "tree": {
                "name": "Up a Tree",
                "description": """You are about 10 feet above the ground nestled among some
large branches. The nearest branch above you is beyond your reach.
On a branch is a small bird's nest containing a jewel-encrusted egg.""",
                "exits": {"down": "forest_path"},
                "items": ["egg"],
                "dark": False
            },
            "clearing": {
                "name": "Clearing",
                "description": """You are in a clearing, with a forest surrounding you on all
sides. A path leads south. There is an open grating, descending into darkness.""",
                "exits": {"south": "forest_path", "down": "grating"},
                "items": ["leaves"],
                "dark": False
            },
            "grating": {
                "name": "Grating Room",
                "description": """You are in a small room below the grating. Dim light filters
down from above. A passage leads south into darkness.""",
                "exits": {"up": "clearing", "south": "cellar"},
                "items": [],
                "dark": True
            }
        }
        
        # Item descriptions
        self.item_descriptions = {
            "mailbox": "a small mailbox",
            "sack": "a brown sack",
            "bottle": "a glass bottle",
            "sword": "an elvish sword",
            "lamp": "a brass lantern",
            "rug": "a large oriental rug",
            "rope": "a coil of rope",
            "knife": "a rusty knife",
            "egg": "a jewel-encrusted egg",
            "leaves": "a pile of leaves",
            "treasure": "a golden chalice",
            "troll": "a nasty-looking troll"
        }
        
        # Treasures and their values
        self.treasures = {
            "egg": 10,
            "treasure": 25,
            "sword": 5
        }
    
    def start(self) -> str:
        """Start the game."""
        return """
╔════════════════════════════════════════════════════════════════╗
║           MINI ZORK - A VA21 Text Adventure                    ║
║                 Inspired by Infocom's Zork                     ║
╠════════════════════════════════════════════════════════════════╣
║  Commands: go <direction>, look, take <item>, drop <item>      ║
║            inventory, examine <item>, open <item>, score       ║
║            turn on lamp, turn off lamp, attack troll, quit     ║
║                                                                ║
║  Directions: north, south, east, west, up, down, in, out       ║
╚════════════════════════════════════════════════════════════════╝

""" + self.look()
    
    def process_command(self, command: str) -> str:
        """Process a player command."""
        if self.game_over:
            return "The game is over. Type 'restart' to play again."
        
        command = command.lower().strip()
        self.moves += 1
        
        # Parse command
        words = command.split()
        if not words:
            return "I beg your pardon?"
        
        verb = words[0]
        args = " ".join(words[1:]) if len(words) > 1 else ""
        
        # Handle commands
        if verb in ["look", "l"]:
            return self.look()
        
        elif verb in ["go", "walk", "move"] or verb in ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d", "in", "out"]:
            direction = args if verb == "go" else verb
            return self.go(direction)
        
        elif verb in ["take", "get", "grab"]:
            return self.take(args)
        
        elif verb in ["drop", "put"]:
            return self.drop(args)
        
        elif verb in ["inventory", "i", "inv"]:
            return self.show_inventory()
        
        elif verb in ["examine", "x", "look at"]:
            return self.examine(args)
        
        elif verb == "open":
            return self.open_item(args)
        
        elif verb == "turn" and "lamp" in command:
            if "on" in command:
                return self.lamp_on_off(True)
            elif "off" in command:
                return self.lamp_on_off(False)
        
        elif verb == "attack":
            return self.attack(args)
        
        elif verb == "score":
            return self.show_score()
        
        elif verb == "quit":
            self.game_over = True
            return self.show_score() + "\nThanks for playing Mini Zork!"
        
        elif verb == "restart":
            self.__init__()
            return self.start()
        
        elif verb == "help":
            return self.show_help()
        
        else:
            return f"I don't know how to '{verb}'."
    
    def look(self) -> str:
        """Look around the current room."""
        room = self.rooms[self.current_room]
        
        # Check for darkness
        if room.get("dark", False) and not self.lamp_on:
            self.grue_warning += 1
            if self.grue_warning >= 3:
                self.game_over = True
                return """It is pitch dark. You are likely to be eaten by a grue.

*** You have been eaten by a grue ***

Your score is {} in {} moves.
Would you like to RESTART?""".format(self.score, self.moves)
            return """It is pitch dark. You are likely to be eaten by a grue.
(You should find a light source!)"""
        
        self.grue_warning = 0
        
        # Build description
        result = f"\n{room['name']}\n"
        result += room['description'] + "\n"
        
        # List visible items
        items = [i for i in room.get("items", []) if i != "troll" or room.get("troll_alive", False)]
        if items:
            result += "\nYou can see: " + ", ".join(self.item_descriptions.get(i, i) for i in items)
        
        # List exits
        exits = list(room.get("exits", {}).keys())
        if exits:
            result += f"\nExits: {', '.join(exits)}"
        
        return result
    
    def go(self, direction: str) -> str:
        """Move in a direction."""
        # Normalize direction
        direction_map = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "u": "up", "d": "down"
        }
        direction = direction_map.get(direction, direction)
        
        room = self.rooms[self.current_room]
        exits = room.get("exits", {})
        
        if direction not in exits:
            return "You can't go that way."
        
        # Check for troll
        if self.current_room == "troll_room" and room.get("troll_alive", False) and direction != "south":
            return "The troll blocks your way with a menacing growl!"
        
        self.current_room = exits[direction]
        return self.look()
    
    def take(self, item: str) -> str:
        """Take an item."""
        if not item:
            return "Take what?"
        
        room = self.rooms[self.current_room]
        items = room.get("items", [])
        
        # Can't take in dark
        if room.get("dark", False) and not self.lamp_on:
            return "It's too dark to see what you're doing."
        
        # Find item
        for i in items:
            if item in i or i in item:
                if i == "troll":
                    return "I don't think the troll would like that."
                if i == "mailbox":
                    return "The mailbox is firmly anchored."
                if i == "rug":
                    return "The rug is too heavy to carry."
                
                room["items"].remove(i)
                self.inventory.append(i)
                
                # Score for treasures
                if i in self.treasures:
                    self.score += self.treasures[i]
                
                return f"Taken: {self.item_descriptions.get(i, i)}"
        
        return f"I don't see any {item} here."
    
    def drop(self, item: str) -> str:
        """Drop an item."""
        if not item:
            return "Drop what?"
        
        for i in self.inventory:
            if item in i or i in item:
                self.inventory.remove(i)
                self.rooms[self.current_room]["items"].append(i)
                return f"Dropped: {self.item_descriptions.get(i, i)}"
        
        return f"You're not carrying any {item}."
    
    def show_inventory(self) -> str:
        """Show inventory."""
        if not self.inventory:
            return "You are empty-handed."
        
        result = "You are carrying:\n"
        for item in self.inventory:
            result += f"  - {self.item_descriptions.get(item, item)}\n"
        return result
    
    def examine(self, item: str) -> str:
        """Examine an item."""
        if not item:
            return "Examine what?"
        
        # Check inventory and room
        all_items = self.inventory + self.rooms[self.current_room].get("items", [])
        
        for i in all_items:
            if item in i or i in item:
                if i == "mailbox":
                    return "The mailbox is closed. You can OPEN it."
                elif i == "lamp":
                    state = "on" if self.lamp_on else "off"
                    return f"A brass lantern. It is {state}."
                elif i == "sword":
                    return "An elvish sword of great antiquity. Its blade glows faintly blue."
                elif i == "troll":
                    return "A nasty-looking troll with a bloody axe. He looks hungry."
                elif i == "egg":
                    return "A beautiful jewel-encrusted egg, worth a fortune!"
                else:
                    return f"You see nothing special about the {i}."
        
        return f"I don't see any {item}."
    
    def open_item(self, item: str) -> str:
        """Open an item."""
        if "mailbox" in item:
            return """Opening the mailbox reveals a leaflet.

(Strewn on the leaflet:)
WELCOME TO ZORK!

ZORK is a game of adventure, danger, and low cunning. In it you will
explore some of the most amazing territory ever seen by mortals.

To get started, try: GO NORTH"""
        
        return "You can't open that."
    
    def lamp_on_off(self, on: bool) -> str:
        """Turn lamp on or off."""
        if "lamp" not in self.inventory:
            return "You're not carrying the lamp."
        
        if on:
            self.lamp_on = True
            self.grue_warning = 0
            return "The brass lantern is now on, casting a warm glow."
        else:
            self.lamp_on = False
            return "The brass lantern is now off."
    
    def attack(self, target: str) -> str:
        """Attack something."""
        if "sword" not in self.inventory and "knife" not in self.inventory:
            return "You have no weapon!"
        
        if "troll" in target:
            room = self.rooms.get("troll_room", {})
            if self.current_room != "troll_room" or not room.get("troll_alive", False):
                return "There's no troll here!"
            
            weapon = "sword" if "sword" in self.inventory else "knife"
            
            if weapon == "sword":
                room["troll_alive"] = False
                room["items"].remove("troll")
                self.score += 15
                return """With a mighty swing of your elvish sword, you strike the troll!
The troll staggers back, then crumbles into dust!
The blue glow of your sword fades slightly.

(Your score just went up by 15 points!)"""
            else:
                return """You attack the troll with your rusty knife!
The troll laughs and knocks the knife from your hand.
The troll's axe swings... and misses!
You'd better find a better weapon!"""
        
        return f"Attacking the {target} isn't going to help."
    
    def show_score(self) -> str:
        """Show current score."""
        max_score = sum(self.treasures.values()) + 15  # +15 for troll
        rank = "Beginner"
        if self.score >= 10:
            rank = "Amateur Adventurer"
        if self.score >= 25:
            rank = "Novice Adventurer"
        if self.score >= 40:
            rank = "Junior Adventurer"
        if self.score >= max_score:
            rank = "Master Adventurer"
        
        return f"""Your score is {self.score} out of a possible {max_score}, in {self.moves} moves.
This gives you the rank of {rank}."""
    
    def show_help(self) -> str:
        """Show help."""
        return """
╔════════════════════════════════════════════════════════════════╗
║                      MINI ZORK HELP                            ║
╠════════════════════════════════════════════════════════════════╣
║  Movement:   go north (or just: north, n)                      ║
║              north, south, east, west, up, down, in, out       ║
║                                                                ║
║  Actions:    look (l) - describe your surroundings             ║
║              take <item> - pick something up                   ║
║              drop <item> - put something down                  ║
║              inventory (i) - see what you're carrying          ║
║              examine <item> - look at something closely        ║
║              open <item> - open something                      ║
║              attack <target> - attack with weapon              ║
║                                                                ║
║  Light:      turn on lamp - light your lamp                    ║
║              turn off lamp - extinguish your lamp              ║
║                                                                ║
║  Game:       score - see your score                            ║
║              quit - end the game                               ║
║              restart - start over                              ║
║                                                                ║
║  Tips:       Watch out for grues in dark places!               ║
║              Find treasures to increase your score.            ║
║              The sword might be useful against enemies...      ║
╚════════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════════════════════
# GAMES LAUNCHER
# ═══════════════════════════════════════════════════════════════════════════════

class VA21GamesLauncher:
    """
    VA21 Games Launcher
    
    Provides access to bundled games including the classic Zork trilogy
    and the built-in Mini Zork.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, games_dir: str = "/va21/games"):
        self.games_dir = games_dir
        self.mini_zork = None
        
        # Check for Frotz (Z-machine interpreter)
        self.frotz_available = self._check_frotz()
        
        print(f"[Games] VA21 Games Launcher v{self.VERSION} initialized")
    
    def _check_frotz(self) -> bool:
        """Check if Frotz is available."""
        try:
            result = subprocess.run(
                ["which", "frotz"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_games_list(self) -> List[Dict]:
        """Get list of available games."""
        games = []
        
        # Add Mini Zork (always available)
        games.append({
            "id": "mini_zork",
            "name": "Mini Zork",
            "description": "A built-in Zork-inspired adventure. Perfect for beginners!",
            "icon": "🎮",
            "available": True,
            "builtin": True
        })
        
        # Add classic Zork games
        for game_id, game in ZORK_GAMES.items():
            # Check if story file exists
            story_path = os.path.join(self.games_dir, game.story_file)
            available = os.path.exists(story_path) and self.frotz_available
            
            games.append({
                "id": game_id,
                "name": game.name,
                "description": game.description.strip().split('\n')[2],  # First line of description
                "icon": game.icon,
                "year": game.year,
                "author": game.author,
                "source_url": game.source_url,
                "available": available,
                "builtin": False
            })
        
        return games
    
    def render_games_menu(self) -> str:
        """Render the games menu."""
        games = self.get_games_list()
        
        lines = [
            "",
            "╔" + "═" * 70 + "╗",
            "║" + " VA21 GAMES - Classic Text Adventures ".center(70) + "║",
            "╠" + "═" * 70 + "╣",
            "║" + " Bundled games inspired by the golden age of interactive fiction ".center(70) + "║",
            "╠" + "═" * 70 + "╣",
        ]
        
        for i, game in enumerate(games, 1):
            status = "✓" if game["available"] else "✗"
            name = f"{game['icon']} {game['name']}"
            if len(name) > 50:
                name = name[:47] + "..."
            
            lines.append(f"║  {i}. {name:<52} [{status}]  ║")
        
        lines.extend([
            "╠" + "═" * 70 + "╣",
            "║" + "  Enter number to play, or 'back' to return ".center(70) + "║",
            "╚" + "═" * 70 + "╝",
        ])
        
        return "\n".join(lines)
    
    def launch_game(self, game_id: str) -> Tuple[bool, str]:
        """Launch a game."""
        if game_id == "mini_zork":
            return True, "mini_zork"
        
        if game_id not in ZORK_GAMES:
            return False, f"Unknown game: {game_id}"
        
        game = ZORK_GAMES[game_id]
        story_path = os.path.join(self.games_dir, game.story_file)
        
        if not os.path.exists(story_path):
            return False, f"""
Game not installed: {game.name}

To install, download from:
{game.source_url}

The Z-machine story file should be placed at:
{story_path}
"""
        
        if not self.frotz_available:
            return False, """
Frotz interpreter not found!

To play classic Zork games, install Frotz:
  Debian/Ubuntu: sudo apt install frotz
  Alpine: sudo apk add frotz
  macOS: brew install frotz
"""
        
        # Launch with Frotz
        try:
            subprocess.run(["frotz", story_path])
            return True, "Game ended."
        except Exception as e:
            return False, f"Error launching game: {e}"
    
    def get_game_info(self, game_id: str) -> Optional[str]:
        """Get detailed info about a game."""
        if game_id == "mini_zork":
            return """
╔════════════════════════════════════════════════════════════════╗
║                       MINI ZORK                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  A built-in text adventure inspired by the classic Zork.       ║
║                                                                ║
║  Explore a mysterious white house and the depths below.        ║
║  Collect treasures, solve puzzles, avoid the grue!             ║
║                                                                ║
║  This is a tutorial game designed to introduce you to the      ║
║  text adventure interface used throughout VA21 OS.             ║
║                                                                ║
║  Type 'play mini_zork' to start your adventure!                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
        
        if game_id in ZORK_GAMES:
            game = ZORK_GAMES[game_id]
            return f"""
╔{'═' * 70}╗
║{f' {game.icon} {game.name} '.center(70)}║
╠{'═' * 70}╣
{game.description}

Author: {game.author}
Year: {game.year}
Source: {game.source_url}
╚{'═' * 70}╝
"""
        
        return None
    
    def play_mini_zork(self) -> MiniZork:
        """Start a Mini Zork game session."""
        self.mini_zork = MiniZork()
        return self.mini_zork


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_games_launcher = None

def get_games_launcher() -> VA21GamesLauncher:
    """Get the games launcher singleton."""
    global _games_launcher
    if _games_launcher is None:
        _games_launcher = VA21GamesLauncher()
    return _games_launcher


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN / TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    launcher = get_games_launcher()
    print(launcher.render_games_menu())
    
    # Test Mini Zork
    print("\n" + "=" * 60)
    print("Testing Mini Zork...")
    print("=" * 60)
    
    game = launcher.play_mini_zork()
    print(game.start())
    
    # Play a few moves
    test_commands = [
        "open mailbox",
        "go north",
        "go east",
        "in",
        "look",
        "take sack",
        "west",
        "take lamp",
        "take sword",
        "inventory",
        "score"
    ]
    
    for cmd in test_commands:
        print(f"\n> {cmd}")
        print(game.process_command(cmd))
