# After the Rain — reconstruction

This small rainy-night bus-stop game is being reconstructed from its surviving V7 source. Later local revisions were lost in a workspace rollback. The preservation commit remains in history; this is **not V37**, and missing historical code or test results are not claimed as recovered.

## Run
Open `project.godot` in Godot 4.6.x Standard and press F5. Windows, macOS and Linux source project; Blender is not needed to play. Generated `.godot` imports are intentionally excluded.

## Existing controls
- WASD: walk; mouse or arrow keys: look (including while seated).
- Space: pause/help; E or Space: resume; R: restart; M: mute while paused.
- E: nearby interaction, sit/stand, board a stopped bus, dispose an empty cup, read or talk.
- F: obtain cocoa near the vending machine, then sip (three sips).
- U: open/fold a borrowed umbrella; E at its basket to borrow/return.
- G: optional umbrella-loan conversation when facing the passenger while holding it; 1 lend, 2 keep, Q cancel.
- T: while seated, quietly skip the remaining wait (not the approaching bus).
- Q: close story; 1/2: offered dialogue choices.
- R: restart; M: mute; Esc: release mouse; click: recapture.
- P: separate overview camera; P or E returns without moving your body or advancing the reader.
- E after the ending: linger by the bus window; E finishes, R restarts.
- E near the flower-window staff/cat: optional wave or greeting when offered.

Reconstruction adds arrow looking, explicit keyboard pause/help, phase-appropriate bus visibility, an elapsed evening clock starting23:40, and optional umbrella lending. First arrival is75seconds; later arrivals are33seconds after departure. There is no last-bus deadline. Flower-window staff, a sheltered cat and a gentle rain lull are also reconstructed. The optional overview and post-ending window linger, cocoa steam/gloved grip, and passenger work/walk conversation are reconstructed too. A bag and folded borrowed umbrella appear beside the window only when that passenger actually boarded the same bus. These are newly implemented and tested features, not recovered historical source. Window activity, puddle/gutter detail and a reproducible48-second original radio arrangement are also rebuilt. See `RECOVERY.md` for restoration status and verification limits.

## Editable source and third-party assets
Saved scenes, scripts, configurations, procedural audio source and packed Blender assemblies are included. See `ARCHITECTURE.md`. City derivatives use Poly Haven CC0 data; provenance/legal text is in `assets/city/licenses/`. The Noto CJK font license is in `assets/fonts/NotoSansCJK-LICENSE.txt`. No external copyrighted music samples are used.

The original catalogue needed to re-run `art/assemble_city.py` is not required for gameplay; obtain the source-relative files documented in the asset manifest if regenerating from scratch. Packed `.blend` assemblies and runtime derivatives are retained.

## Baseline status
The original preservation commit remains in history; current changes are documented in `RECOVERY.md`. Screenshots, generated cache, local performance records and private feedback notes are excluded. This repository is the durable source checkpoint; successful remote verification, not a local commit alone, establishes preservation.
