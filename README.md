# Grandpa's Games

A collection of small, gentle games made for the grandkids. Each game lives in
its own folder with its own README and run instructions.

| Game | Folder | What it is |
|---|---|---|
| Baker's Undersea Adventure | `bakers-undersea-adventure/` | A point-and-click adventure in the Freddi Fish tradition. Browser version in `web/` (open `index.html`), Python version alongside. |
| Baker's Peek-a-Boo World | `peek-a-boo/` | Tap-to-reveal games for ages 1 to 5, four bands and 18 levels, nine friends, Grandpa's recorded voice. Single HTML file, runs in any browser or on a phone home screen. |

## Running a game

Each folder is self-contained and has its own README. For example:

```bash
cd bakers-undersea-adventure
pip install -r requirements.txt
python main.py
```

```bash
cd peek-a-boo
python -m http.server 8000
```
