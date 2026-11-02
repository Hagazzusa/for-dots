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
