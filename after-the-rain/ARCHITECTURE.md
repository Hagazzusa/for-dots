# After the Rain — scene architecture

The core composition below began in the surviving prototype. The reconstruction boundaries and timing additions are documented in the final section; version labels describe provenance, not recovered later source.

## Editor-first composition

Open `main.tscn`. The local Scene dock now contains authored scene instances, not an empty root whose script constructs the set. Open each component scene to edit its stable children; enable **Editable Children** on an instance only when an intentional instance override is needed. Imported shelter geometry remains an instance of `assets/shelter.glb`, with original Blender source under `art/`.

| Boundary | Responsibility / editable data |
| --- | --- |
| `main.tscn` + `scripts/session.gd` | Composition root, one-time signal wiring, interaction priority, session warmth/note/boarding/ending state. Inspector radii tune seat, vending, boarding and disposal reach. Does not construct world geometry. |
| `scenes/world.tscn` + `scripts/world.gd` | Authored road, buildings, lights, environment and BusStop instance. Shelter bounds exported; named placement anchors exposed through `anchor()`. |
| `scenes/bus_stop.tscn` | Authored shelter GLB instance, collision, signage/lights, and Start/Seat/Stand/Vending/Boarding anchors. ArrivalDisplay and TrashCan are independent saved instances. |
| `scenes/player.tscn` + `scripts/player.gd` | CharacterBody3D, collision and camera; movement, look, sit/stand/reset; emits action intents rather than locating gameplay siblings. Inspector speed/sensitivity and safe movement bounds. |
| `scenes/held_drink.tscn` + `scripts/held_drink.gd` | Camera-local pose, movement impulses, sip animation and steam. Inspector resting/sipping offsets, tilts, pose speed and impulse scale. Owns CocoaCup instance, not drink inventory. |
| `scenes/cocoa_cup.tscn` + `liquid_cup.gd` | Saved hollow vessel/rim/walls and Liquid mesh node. Only the deforming liquid mesh is rebuilt. Inspector initial fill, fill-change speed, spring strength/damping. Bounded damped surface approximation, not CFD or simulated spilling. |
| `DrinkSession` + `scripts/drink_session.gd` | Inventory, dispensing/sip debounce, delayed fill change, three servings and empty-cup disposal. Emits notes, chime request and fill target changes. Inspector timing and serving count. |
| `scenes/night_bus.tscn` + `scripts/night_bus.gd` | Route state and arrival/phase signals. `config/bus_schedule.tres` is shared immutable tuning for durations and route endpoints; each instance owns elapsed time, phase and pause state. |
| `scenes/bus_visual.tscn` + `scripts/bus_visual.gd` | Saved bus meshes, lights and door nodes; local door tween only. Inspector door travel and duration. |
| `scenes/rain.tscn` + `scripts/rain.gd` | Saved MultiMeshInstance3D, drop mesh and material; procedural population/transform updates. Inspector speed, wind, count and shelter cutoff bounds. |
| `scenes/ambience.tscn` + `scripts/ambience.gd` | Saved rain/engine/chime AudioStreamPlayers and streams; explicit shelter/bus mix. Inspector filter frequencies, volume targets and smoothing. |
| `scenes/hud.tscn` + `scripts/hud.gd` | Saved labels, guide and ending overlay; `present()` receives text/visibility without querying siblings or owning game state. |
| `scenes/arrival_display.tscn` + `scripts/arrival_display.gd` | World-space destination/countdown labels. Session passes phase and seconds; no independent route timer. |
| `scenes/trash_can.tscn` | Authored bin, collision and Interaction Marker3D. Session resolves proximity/priority; DrinkSession decides whether disposal is valid. |
| `scenes/onboard_view.tscn` + `scripts/onboard_view.gd` | Authored window-side interior/camera. Explicit `begin/advance/reset`; one finished signal per ride. Inspector duration, travel and gentle sway. Eight-second tableau, not a bus driving simulation. |

The three final entries are v4 enhancements added after the baseline refactor gate. Their integration/visual verification is separate from the persistence test below.

## Dependency and update rules

Children keep local paths only. The composition root injects cross-system commands and connects signals once in `_ready()`, after child initialization. No service locator, global gameplay autoload or per-frame tree search is required. Independent scenes initialize without a gameplay parent. Input capture, active camera and Master mute are necessarily project/global concerns; two whole playable sessions are not intended to run together.

Player movement remains `_physics_process()` with `move_and_slide()`. Session `_process()` preserves the original relative subsystem order: compute interaction hint; advance bus; advance drink; present held drink/liquid; decay warmth and note; mix ambience; present HUD; advance rain. The added onboard advancement and arrival-display presentation sit between drink advancement and held-drink presentation. Door tweens remain engine-managed. Bus advancement intentionally accepts **at most one state transition per call**, discarding overshoot as v3 did; do not replace it with a catch-up loop without changing tests/timing intentionally. Hint computation retains the prototype's possible one-frame boundary lag.

## Saved ownership, procedural exceptions and resources

- Stable world/prop/player/UI/door/cup geometry is serialized with valid owners. Nested GLB scene references must survive a `PackedScene.pack()` / save / reload cycle; do not flatten or recreate the shelter in `_ready()`.
- `config/rain_positions.json` stores the exact baked v3 rain positions after world RNG consumption. Session injects them; rain's independent seeded fallback is for standalone viewing, **not** a replacement for that sequence. The production update consumes no additional random numbers.
- Rain allocates a fresh MultiMesh and positions array per instance. Cocoa allocates its own liquid mesh and duplicated mutable liquid material; springs/fill/velocity are instance state. Authored immutable mesh/material resources may be shared.
- The bus schedule is shared immutable configuration. Bus presentation duplicates mutable materials per instance before applying phase visibility/fade; door motion changes authored nodes. Never mutate cached shared materials to fade or recolor an individual instance.
- `default_bus_layout.tres` defines Master and ShelterRain plus low-pass effect. No runtime `add_bus()` call is allowed. Audio players/volumes are per instance, but ShelterRain filter and Master mute are explicitly one **shared project mix**. Multiple simultaneously active ambience scenes cannot have independent low-pass filters; repeated loads do not leak global buses.
- Reset is a coordinated session command, not scene reconstruction. Each subsystem resets its own mutable state; signal connections are not re-added on restart.

## Reproducible checks

From the project directory, with installed Godot 4.6.3:

```sh
godot --headless --editor --path . --quit
godot --headless --path . --script res://tests/authored_scene_persistence.gd
godot --headless --path . --script res://tests/component_isolation.gd
godot --headless --path . --script res://tests/player_cup_isolation.gd
godot --headless --path . --script res://tests/audio_rain_isolation.gd
godot --headless --path . -- --test
```

`authored_scene_persistence.gd` actually packs, saves to `user://`, reloads with cache ignored, compares all node paths/classes/transforms, mesh types/surface counts/bounds and collision types, checks owner ancestry and the imported GLB reference, then deletes temporary files. It also drives two real `night_bus.tscn` instances through arrival, waits for real door tweens, checks signal count/state/reset isolation, verifies immutable materials are unchanged, demonstrates a duplicated local material edit, and repeats two-instance ambience creation three times. Orphan-node and bus counts must return to baseline. The test does not replace GPU/GUI visual inspection; headless dummy rendering cannot establish pixel correctness, rain visibility or liquid appearance.

Other tests cover controller timings/intent debounce, cup/player instance isolation and liquid bounds, rain arrays and HUD, and full gameplay disposal/boarding/ending/restart. Always check process exit **and** log for script/assertion errors. Also play in the actual GUI: walk/sit/sip, inspect extreme cup tilts, miss and catch a bus, dispose/refill, board with a cup and restart during/after the window ride. Preserve previous version snapshots when updating this architecture.

## Final integration verification
Seven headless suites passed on Godot 4.6.3: gameplay, player/cup, component state, rain/audio, authored persistence, disposal/display, onboard isolation. Shared-desktop GUI verified baseline locomotion/dispense/seated sip and boarding with a cup, moving window view, ending and restart; three sips followed by bin disposal. Cloud audio initialization failed and fell back to dummy driver; sound not auditioned. Software graphics VSync mode warning is environmental. No game script/parser errors.

## v4.1 front entry correction
The +X-facing bus previously placed its x2.4 entry above the x2.35 axle. Door, steps, light and body aperture now center at x2.8; front axle is x1.35. Lower entry edge x2.15 minus tire front x1.83 gives 0.32 m clear longitudinal gap. Authored floor has an entry notch. Doors recess to two interior tracks before sliding rearward; close reverses sequence. Boarding marker is x2.8 at the safe curb z2.65. `tests/bus_clearance.gd` checks actual transformed mesh bounds through closed, open, transit and reversal. `tests/bus_review.tscn` is an optional curb-side visual QA scene; normal main scene remains unchanged.

## v5 city authorship and budget
`scenes/city_layout.tscn` instances two independently authored building scenes. Its `layout` Resource exposes seed, rows, spacing, setbacks, height range, envelope and node budget. The editor-only Rebuild preview action replaces only Generated; saving persists the instances. Runtime never consumes city RNG or regenerates content. Original rain inputs/order remain unchanged.

Poly Haven CC0 facade modules were assembled and material-merged in Blender. Packed high-detail source is preserved; runtime GLBs are reduced to 20,021 / 19,076 triangles, 9 material surfaces each. Default city: 16 buildings, 81 nodes, 16 mesh instances, 144 surfaces, 16 simple box colliders. Front doors face the street; minimum nominal gap is 1 m and clear street interval is z[-2,18]. Bus lane and safe walking bounds remain unchanged. World save/reopen contains 365 nodes with intact imported assets.

`tests/city_layout.gd` verifies repeatable seed/type/transforms, actual mesh envelope, no overlap, road setbacks, no automatic generation, node budget, invalid-build preservation and owner persistence. `tests/city_before.tscn` and `tests/city_review.tscn` provide identical-camera comparison; local captures live in art/. These review scenes are not the normal gameplay entry point.

License/source/hash evidence is in assets/city/licenses/. Factory facade was evaluated but is not included in the runtime streetscape. This remains a small atmospheric diorama, not a fully traversable or photorealistic simulated city.

Runtime street surfaces use metre-scaled UV PlaneMeshes with original floor collision retained, avoiding triple texture projections on broad horizontal surfaces. Render scale remains native 1.0: reducing pixel resolution did not materially help this software-renderer bottleneck. Default city uses lightweight distant modules; config/city_layout_detailed.tres selects the preserved 20k-triangle variants through the same editor baker. Performance figures are device-specific, not a guarantee.

## V5 city validation and quality tiers
CityLayout explicitly bakes 16 reusable CC0-derived building scene instances into its saved Generated subtree; there is no generation at runtime. Fixed seed, actual bounds, street setbacks, instance ownership and save/reopen are covered by tests/city_layout.gd. Each building has one simple box collider. Default background meshes are 4,704/4,482 triangles; config/city_layout_detailed.tres selects the preserved 20,021/19,076 variants. The Blender high-detail assembly is retained separately. The comparison harness tests/city_before.tscn and tests/city_review.tscn uses one camera and paused bus; local captures/metrics are in art/. Metrics are short samples, not percentile profiling. Final native GUI regression: walk to vending, dispense, sit, sip, stand, board while carrying cup, window ride, ending, restart. Core headless regression and actual bus-clearance suite passed after final asset replacement. Cloud audio remains dummy/not auditioned; cloud software rasterization remains ~10 FPS in the comparison view despite reducing visible primitives from 157k to 54k. No external publication or automatic ZIP delivery.

## V6 optional stories
StoryCorner composes authored Objects (Memo/Route/Passenger/Radio), StoryPanel, and RadioAudio. It owns only optional-content targeting and local UI/audio lifecycle. Session provides camera/position, prioritizes stand/boarding/bin over content, and closes content on board/restart. StoryText Resources are immutable inputs; each panel copies page/choice arrays. Radio duplicates its stream resource before configuring loop playback, uses existing Master bus, and starts off. Geometry is saved, shadowless primitive composition; only passenger and radio stand add simple box colliders. New Korean font is bundled with its license. The original 16-second radio synthesis source is in art/. No mandatory objectives or plot flags gate the bus. Tests/story_integration.gd covers directional target selection, optional reading, boarding with dialogue open and full reset; story_panel.gd and story_radio.gd cover independent instances and cleanup. Baseline bench regression now explicitly faces the seat because E intentionally selects looked-at content before the broad seat-radius fallback.
Final GUI checks: Korean memo/route/passenger pages and both dialogue control hints are legible at 1280×720; radio caption toggles; movement around new props reaches vending, dispense and boarding/end/reset still work. Route board was moved left to x−1.65 after visual QA revealed it obscured the arrival display. Final story save/reopen and integration test passes after this correction. Four harmless parameter-shadow warnings were fixed; the remaining GUI diagnostics are the pre-existing cloud VSync/audio-device/dummy-driver limitations.

## V7 a short rainy walk
Exploration owns only optional borrow/return and flower-note interaction; Session injects the independent held umbrella and shared reading panel. HeldUmbrella is a saved camera attachment, separate from HeldDrink. Rain receives a canopy center/enabled command and hides only nearby drops beneath its radius; ambience receives an optional umbrella flag, preserving four-argument callers. This is a visual/audio approximation, not cloth or water simulation. Player bounds expand only on the shelter side (x ±12, z −8..2.65), never into the road. NeighborhoodWalk owns its saved ground collision and flower display. Passenger owns its idle/walk/return/boarded lifecycle and receives bus phase, entry point and dialogue flag; no sibling searches. Its movement disables blocking collision and follows authored safe waypoint offsets. The session closes passenger reading only while that specific story is active. A fresh independent QA agent caught stale story ownership closing later flower notes; closing the panel now clears its owner. Tests/v7_qa.gd reproduces and guards that case alongside real capsule navigation, three bus cycles and item/reset/interaction priorities.
Final validation: all 15 focused suites plus main gameplay regression passed on Godot 4.6.3. Actual engine review verified umbrella+filled cocoa framing, Korean flower note fit, and passenger walking along the curb then disappearing at the entry when boarded. The tiny shop is an authored display vignette, not an accessible shop interior. Umbrella/cocoa use separate camera attachments; no cloth, splashes or full fluid simulation is implied. Native audio remains unavailable, so mix and loop behavior are programmatically verified only.


## Reconstruction boundaries

| Saved unit | Ownership / injected context |
| --- | --- |
| `EveningClock` / `WeatherCycle` | Clock owns simulation elapsed time; weather reads it deterministically. The completed evening has no last-bus cutoff. |
| `PauseOverlay` | Always-processing keyboard help overlay owns tree pause and resume; emits restart/mute requests. Esc remains mouse release, not implicit pause. |
| `UmbrellaExchange` / `EveningConversation` | Optional loan and work/walk state; immutable exported story Resources and exact-reader identity guards. Neither gates boarding. |
| `FlowerLife` / `RainCat` / `RainCover` | Explicitly stepped local events; one authored awning volume drives both shelter decisions and rain masking. |
| `OverviewView` / `OnboardView` | Camera ownership and authored rest poses; overview preserves the body/page, optional linger keeps the completed ending available. |
| `OnboardCompanion` | Peripheral props appear only from the root's actual same-bus snapshot, never an inferred loan alone. |
| `DrinkSession` / `HeldDrink` | Session is the sole sip timing/fill/heat owner. Presentation receives normalized sip progress and shelter context; approved procedural liquid remains independent. |
| `WindowLife` / `RainDetails` | Private CPU-phased materials/buffers; fixed authored geometry and no new lights. Window uses evening time, physical drips use resettable presentation time. |

Shared evening clock/weather are evaluated before their consumers. Quiet-wait advances only skipped evening time, not drink, passenger walking or physical rain trajectories. Pause freezes the session tree. After the default ending the clock is fixed, while optional window linger and physical rain presentation can continue; restart resets both clocks. Newly added effects do not consume world RNG or shader wall-clock `TIME`.

Use `tools/run_checks.sh` for the serial aggregate and `tools/export-audit.py` for the isolated production-PCK gate. Both use an external disk-backed QA directory and a shared lock, exclude their own fixtures from the runtime pack, and must be supplemented by ordinary-game native inspection. A fixture/test flag is never the user handoff scene. Public validation notes are in `RECOVERY.md`; local screenshots and raw logs are not project assets.

## Shared evening pocket

| Unit | Saved ownership | Contract / state |
|---|---|---|
| NeighborhoodExtension | `scenes/neighborhood_extension.tscn` | Owns local reader markers, private heater PCM and seated idle phase. Session injects StoryPanel, updates phase, supplies its cover to World/Rain and suspends it when boarding. |
| GlassRefuge | Saved imported GLB child, authored floor/wall colliders and pendant | Runtime creates only per-instance transparent material overrides. Original geometry remains unchanged. The asymmetric front entry is open. |
| ParkedCar | `scenes/parked_car.tscn` | 99 authored primitive nodes, two occupant roots and one static chassis collider; no autonomous vehicle/camera/global state. `art/build_parked_car.py` regenerates this scene only. |
| Story data | `config/story_car.tres`, `story_refuge.tres`, existing flower/passenger Resources | Shared immutable Korean content; the existing reader copies page/choice arrays. No new dialogue manager or quest flags. |

The expanded bounds add a small right-side pavement pocket, not an open-city streaming system. The bus lane, schedule, original interaction ordering and approved liquid component remain unchanged. Boarding and an already-open reader retain priority over optional neighborhood observations.
