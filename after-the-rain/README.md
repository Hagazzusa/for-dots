# After the Rain — core reconstruction

This is the surviving V7 source of a small rainy-night bus-stop game. Later local revisions were lost in a workspace rollback. This baseline preserves what remains; it is **not V37**, and it does not claim later fixes or test results.

## Run
Open `project.godot` in Godot 4.6.x Standard and press F5. Windows, macOS and Linux source project; Blender is not needed to play. Generated `.godot` imports are intentionally excluded.

## Existing controls
- WASD: walk; mouse or arrow keys: look (including while seated).
- Space: pause/help; E or Space: resume; R: restart; M: mute while paused.
- E: nearby interaction, sit/stand, board a stopped bus, dispose an empty cup, read or talk.
- F: obtain cocoa near the vending machine, then sip (three sips).
- U: open/fold a borrowed umbrella; E at its basket to borrow/return.
- Q: close story; 1/2: offered dialogue choices.
- R: restart; M: mute; Esc: release mouse; click: recapture.
- P: existing overview/photo view; R returns to the opening.

Core reconstruction adds arrow looking, explicit keyboard pause/help and phase-appropriate bus visibility. Later content must still be reconstructed and tested afresh rather than attributed to missing source.

## Editable source and third-party assets
Saved scenes, scripts, configurations, procedural audio source and packed Blender assemblies are included. See `ARCHITECTURE.md`. City derivatives use Poly Haven CC0 data; provenance/legal text is in `assets/city/licenses/`. The Noto CJK font license is in `assets/fonts/NotoSansCJK-LICENSE.txt`. No external copyrighted music samples are used.

The original catalogue needed to re-run `art/assemble_city.py` is not required for gameplay; obtain the source-relative files documented in the asset manifest if regenerating from scratch. Packed `.blend` assemblies and runtime derivatives are retained.

## Baseline status
The original preservation commit remains in history; current changes are documented in `RECOVERY.md`. Screenshots, generated cache, local performance records and private feedback notes are excluded. This repository is the durable source checkpoint; successful remote verification, not a local commit alone, establishes preservation.
