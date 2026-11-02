# Continuity checklist

Use after a rollback or an extension. This is a review checklist, not a claim that a new test run occurred.
Baseline: `9f6165c30b83d68415bae7053312344880c546f2`; see [world expansion verification](../WORLD_EXPANSION.md) for that checkpoint's verification and known audio-shutdown limitation.

## Text and staging

- [ ] Preserve all eight source clues with their status ledger; do not relabel draft actions as shipped animation.
- [ ] Keep holiday unspecified, 23:40 opening, ordinary repeating route 08 and Market Street passenger destination.
- [ ] Preserve flower closed status plus late-pickup promise; owner retreat/wave must not imply business reopening or pickup completion.
- [ ] Preserve soboro, crunchy-top memory, tea at home and rain-obscured view; no mandatory spouse exposition or new question list.
- [ ] Keep exactly two adult car occupants; card relationship clue stays optional. No player entry, dialogue, driving or third occupant.
- [ ] Preserve source-concept provenance and actual derived GLB identity; do not claim Blender/Cycles parity or full source landscape in-game.
- [ ] Refuge bench canon is the carpenter's former home bench, repaired at the workshop—not a newly made second-origin bench.

## Interaction and time

- [ ] Original stop and refuge remain the only two player seat identities. Each stand action uses its own clear exit position.
- [ ] Eligible bus boarding has priority; an open reader consumes E before standing. Q closes the reader without relocating the player.
- [ ] Cocoa, held umbrella, T quiet wait, pause and overview remain compatible with either seat. Missing a bus while seated does not relocate the player.
- [ ] Passenger interaction requires actual waiting availability; opening a loan panel cannot authorize transfer after boarding begins.
- [ ] One umbrella has one owner: basket, player or passenger. Interrupted passenger approach retraces the path without canceling a committed loan.
- [ ] Passenger who boarded and departed stays absent on later arrivals. Same-bus companion requires actual recorded presence; otherwise loan recollection is memory, not phantom speech.
- [ ] Flower/car/refuge observations do not alter bus timing, award items, determine the ending or teleport any character.
- [ ] Reset restores passenger, umbrella, ambient visit, car pose, reader and original opening consistently. Car heater stops on boarding and releases its stream on teardown.
- [ ] Ignoring all new observations still permits the original ride and quiet ending.

## Evidence anchors

Paths below are relative to the `after-the-rain/` project root, one directory above this document.

`config/story_{passenger,flower,car,refuge}.tres`; `scenes/neighborhood_extension.tscn`; `scripts/neighborhood_extension.gd`, `glass_refuge.gd`, `flower_life.gd`, `waiting_passenger.gd`, `umbrella_exchange.gd`, `onboard_companion.gd`; `art/build_parked_car.py`; `assets/refuge/README.md`; `WORLD_EXPANSION.md`.
Relevant regression coverage: `tests/world_expansion.gd`, `tests/refuge_seating.gd` and the passenger/umbrella lifecycle suites. Documentation review alone does not substitute for rerunning them after code changes.
