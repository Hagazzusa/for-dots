# Reconstruction checkpoints

The surviving V7 baseline is preserved in Git history. Later local revisions were lost; this work reconstructs selected behavior and validates new code. It is not recovery of the original later source.

## Core stage design
| Unit | Responsibility | Interface / ownership |
|---|---|---|
| Player scene | Mouse and keyboard look, locomotion | Inspector keyboard speed; seated look; existing anti-warp mouse guard |
| NightBus + Visual | Route phase and distant visual fade | Route owns opacity; private cached materials; session still owns boarded root hiding |
| PauseOverlay scene | Explicit pause/help and keyboard navigation | Owns only pause it acquired; restart/mute signals wired by session; saved controls/font |
| Session | Compose components, gate source-only regression entry | Never disable gameplay for an unavailable test runner |
| Source review fixtures | Clearly identified visual test scenes | TEST ONLY title/banner; not dependencies of normal main |

No liquid, cup geometry, bus door/wheel geometry, schedule or content changes belong to this stage. Esc remains mouse release; Space is explicit pause. No focus-loss automatic pause. Tests are fresh evidence, not inherited results from lost revisions.

### Core validation notes
Godot4.6.3 Compatibility. The first fresh gate exposed an old test assuming material sharing while parked; its full-opacity sharing assertion now explicitly selects full opacity, while a new test checks private waiting/fade resources. New integration-test audio is stopped/drained before teardown. Real input tests wait for dispatched press/release frames rather than assuming synchronous event delivery.

Native keyboard play verified seated arrow look, ordinary arrival/boarding, pause during the window ride, the default ending and restart. Help is readable at1180×812 and636×356; Home/End reaches overflow content. Portrait478×718 exposed a real focus bug: Tab could focus a button outside the scroll area. Focus changes now queue scroll reveal, with a dedicated Home→Tab regression. A source-only review fixture was inspected with its red TEST ONLY banner and distinct window title, then closed; it is never the normal scene.

No audible audition is claimed on the cloud Dummy audio driver. The native cloud renderer is llvmpipe; performance is not representative of a hardware-GPU desktop. Later content/overview polish and other remembered features remain subsequent reconstruction stages.

Final core gate (2026-11-02):21 serial checks including import and main, zero failures; bus visibility58 checks and pause62 checks. A145-file production PCK passes isolated normal and `--test` runs with input enabled and no source fixtures. Native portrait Home→Tab recheck reveals the focused Restart button correctly. The ordinary main opening was restored at1180×812 after fixtures. Original liquid and bus-door geometry remain unchanged.

## Evening stage design
EveningClock owns elapsed simulation time and starts23:40. NightBus owns first/repeated wait durations (67/25seconds plus8second approach), cycle count and exact remaining-wait skip. SeatedT advances only that remaining waiting time and the displayed clock, not drink physics, passenger motion or an already approaching bus. No deadline or forced last bus.

UmbrellaExchange owns optional loan state; StoryPanel supplies Resource identity and a close event. Explicit G opens a1/2 choice only while holding the umbrella and facing an available passenger. Q does not lend; accepting transfers the single shared item and leaves its basket unavailable until restart. The reconstructed G interface and dialogue are new, not claimed identical to missing historical code. Same-bus voice is conditional on the passenger actually being aboard; a later bus retains only a memory. Existing passenger movement is preserved.

The exchange's three-mesh folded umbrella follows the recipient's authored hand. While bound, it suppresses the old decorative umbrella, so the NPC does not already hold a second umbrella before borrowing. Reset hides the loan prop; freeing/rebinding restores the independent original NPC appearance. Independent review found that early player boarding could leave the sibling prop visible after the passenger disappeared; boarding now refreshes its presentation immediately, covered by a root integration assertion.

The existing three-cycle passenger regression now derives its simulation duration from first/repeated schedules rather than its former fixed190seconds; its original three-cycle/no-ghost assertion is retained.

### Evening native verification and input correction
Native play confirmed the optional loan's cancel/keep/lend branches, one visible transferred umbrella, seated T changing23:40 to23:41 as the arrival begins, ordinary boarding, the completed ending and R resetting the clock/countdown. The ordinary main opening was restored after inspection.

Correction to the earlier core note: the first seated-look check did not prove remote logical-only arrow input. The evening pass reproduced that gap and changes arrow polling to logical keycodes, leaving physical WASD unchanged. Held Left now visibly rotates in the native game; release and pause/resume do not leave rotation stuck. A real key-event regression supplements the earlier direct-method checks.

Final evening gate (2026-11-02):24 serial checks, zero failures, including logical-only press/hold/release through the real input dispatcher and actual passenger walking onto the same bus. The synthetic-input test now settles initial viewport frames and explicitly flushes buffered events before asserting key state; it still asserts physical arrow state is false. Production PCK audit:150 files, isolated normal and `--test` runs both playable, no source fixtures. No liquid or bus-door geometry changes.

## Neighborhood stage design
WeatherCycle owns the deterministic180-second rain-lull envelope from evening simulation time (45-second onset,12-second fade,18-second hold,12-second return). Rain keeps every baked trajectory advancing and varies only the drawn subset; Ambience reduces only its rain target by up to4.5dB. Quiet-wait intentionally advances this evening time; ordinary pause freezes it. No survival penalty or last-bus deadline.

The flower-shop awning has one authored RainCover volume, injected identically into the world's shelter check and rain masking. It follows the actual underside and footprint, not a broad proximity radius. FlowerLife and RainCat are independent saved compositions with explicit stepping and local state, no new lights, collisions or global timers. Optional E gestures never gate boarding; reset starts a fresh encounter. These are fresh reconstructions of remembered scenes, not recovered original source or wording.

Neighborhood validation (2026-11-02):27 serial checks/0 failures, including36 weather checks and37 flower/cat checks. Actual intermediate mesh bounds, two-instance state, pause, save/reopen, unchanged rain trajectories and shared cover decisions are tested. Headless Dummy MultiMesh readback is not treated as render proof; native inspection separately confirmed the sheltered view and cat placement. The physical walking test now targets the actual paper's relocated marker while retaining capsule collision movement, rather than the former window-center waypoint.

Native ordinary play: walked to the flower window, saw the staff appear, used E for the visible wave and Korean response; watched the cat move out during the lull and accepted its E greeting; entered the awning and observed the shelter response; read the paper at its actual location; reset, quietly waited, boarded normally and restored the ordinary opening. Cloud audio remains unauditioned. Production PCK158files passes isolated normal/`--test` play with fixtures excluded.

## Views stage design
The default8-second ride and completion remain intact. OnboardView now respects the full authored camera rest transform; optional E after completion shows the window again with bounded camera-only sway at the fixed endpoint, without replaying completion. E returns to the ending; R resets. OverviewView is a separate saved camera and never teleports the player. Session suspends only the reader's presentation/input and player motion while viewing; P/E restores the same seat/body/page, without a second E interaction. Camera ownership is restored only when still owned by the overview.

The oversized emissive bus-interior panel is removed, existing steps use a dark nonemissive material, and the existing entry light is restrained. Seven simple authored details make the boarding space legible; door/wheel geometry and0.32m clearance are preserved. Near-view rain shrinks smoothly within0.45–1.8m of the actual active camera, without changing any trajectory, RNG sequence or population. This is a lightweight visual approximation, not collision-driven droplets.

Views validation (2026-11-02):30 serial checks/0 failures;160-file production PCK passes both isolated modes. Tests include10,000 linger steps, authored-camera variation, weak camera ownership, actual P/E dispatch preserving seat/reader, suppressed hidden choices, reset, near-camera scale bounds,635 bus clarity/door-sweep checks and the original cup regressions. Independent review caught an overview-only U hint despite disabled U; removed and regression-covered. No runtime errors in native log.

Native ordinary game verified: open dialogue→P overview→E returns to the same unanswered dialogue; seated P/E restores the same seat; clearer steps/aisle and normal boarding; default ending→E window linger→Space pause→resume→E ending→R opening. Korean ending/help text is readable. Near-camera rain no longer creates the earlier large foreground streaks. The normal opening is left playable, not a fixture. Original liquid source remains byte-identical.

## Warmth stage design
DrinkSession is the single owner of sip duration and normalized progress (−1 inactive,0–1 active), cup age and a bounded presentation heat value. The approved default1.3-second sip and liquid fill/slosh remain unchanged; varied sip durations no longer drift from a separate presentation timer. Heat fades over180seconds to a small floor while cocoa remains, resets on refill, and never imposes a survival penalty.

HeldDrink receives heat/shelter/umbrella state explicitly. Three CPU-phased textured billboard wisps replace sphere particles, with quieter drift under cover and no shader wall-clock time. A small authored coat/gloved grip supports the cup. Steam hides while sipping, empty, boarding or in overview. The seated attachment uses a world-height floor to keep cup and grip above the bench even when looking down. The approved liquid script and six-part cup scene remain byte-identical.

Warmth validation (2026-11-02):32 serial checks/0 failures,163-file isolated production pack passes normal and`--test`. Timing variants0.65/1.3/2.6seconds, exact approved midpoint pose,180-second heat floor/refill, extreme seated camera pitches, private/resettable steam and actual grip surface/bench bounds pass. Steam is6 triangles and the authored grip448 triangles. Native seated cocoa showed faint rising wisps and a supporting glove; consecutive F sips visibly lowered the liquid, the empty cup had no steam, and extreme downward look/overview-return/reset stayed usable. Normal opening restored. No perceptual cloud-audio claim.

### Remaining reconstruction scope
The original later source has not been recovered. Passenger thanks/true same-bus visual continuity and optional work/walk conversation, window activity, puddle ripples, gutter droplets and the later procedural radio arrangement are not yet reconstructed at this checkpoint. Existing V7 radio and stories remain playable. Tests here validate new code only, not parity with lost revisions.
