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
