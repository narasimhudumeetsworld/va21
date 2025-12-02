# VA21 Games - Classic Text Adventures

## 🎮 Bundled Games

VA21 OS comes with classic text adventure games, just like how Microsoft used to bundle games with Windows!

### Built-in Games

#### 🎮 Mini Zork
A built-in Zork-inspired adventure written in Python. No additional software needed!

```
> play mini_zork

West of House
You are standing in an open field west of a white house,
with a boarded front door. There is a small mailbox here.

> open mailbox
Opening the mailbox reveals a leaflet...
```

### Classic Zork Trilogy (Optional)

The legendary Zork games from Infocom (1980-1982) that inspired VA21's interface:

| Game | Year | Description |
|------|------|-------------|
| 🏰 Zork I: The Great Underground Empire | 1980 | The adventure begins! |
| 🧙 Zork II: The Wizard of Frobozz | 1981 | Deeper into the Empire |
| 👑 Zork III: The Dungeon Master | 1982 | The epic conclusion |

## Installing Classic Zork Games

### 1. Install Frotz (Z-Machine Interpreter)

```bash
# Debian/Ubuntu
sudo apt install frotz

# Alpine
sudo apk add frotz

# macOS
brew install frotz
```

### 2. Download Game Files

The original Zork source code is available on GitHub:

- [Zork I](https://github.com/historicalsource/zork1)
- [Zork II](https://github.com/historicalsource/zork2)
- [Zork III](https://github.com/historicalsource/zork3)

You'll need to compile the ZIL source to Z-machine format, or find pre-compiled `.z3` files.

### 3. Place Game Files

Copy the `.z3` story files to `/va21/games/`:

```
/va21/games/
├── zork1.z3
├── zork2.z3
└── zork3.z3
```

## Playing Games in VA21

### From the Zork Interface

```
> games

╔══════════════════════════════════════════════════════════════════════╗
║              VA21 GAMES - Classic Text Adventures                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  1. 🎮 Mini Zork                                            [✓]      ║
║  2. 🏰 Zork I: The Great Underground Empire                 [✓]      ║
║  3. 🧙 Zork II: The Wizard of Frobozz                       [✓]      ║
║  4. 👑 Zork III: The Dungeon Master                         [✓]      ║
╚══════════════════════════════════════════════════════════════════════╝

> play 1
```

### With Keyboard Shortcut

Press `Ctrl+G` to open the games menu.

### Ask the Helper AI

```
You: play zork
AI: Starting Mini Zork... enjoy your adventure!
```

## Why Zork?

VA21's entire interface is inspired by Zork and the golden age of interactive fiction. Just as Zork pioneered natural language input in games, VA21 brings that same philosophy to operating system control.

> "West of House. You are standing in an open field west of a white house..."

These immortal words began millions of adventures. Now, that same spirit of exploration powers VA21.

## Credits

- **Original Zork**: Tim Anderson, Marc Blank, Bruce Daniels, Dave Lebling (MIT/Infocom)
- **Historical Source**: Available at github.com/historicalsource
- **Mini Zork**: Built for VA21 by Prayaga Vaibhav
- **Frotz Interpreter**: Open source Z-machine implementation

## License

Mini Zork is part of VA21 OS and follows its license.

The original Zork games are property of their respective copyright holders.
The source code is available for educational purposes at Historical Source.

---

*Om Vinayaka - Where adventure meets research* 🎮
