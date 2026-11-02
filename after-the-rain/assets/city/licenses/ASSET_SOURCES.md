# City exterior asset sources

Retrieved 2026-11-01 from the official Poly Haven asset download service, using published file metadata. All 37 downloaded asset files passed expected byte length and publisher MD5 checks. Exact source URLs, byte sizes, hashes, source-relative paths: `download_manifest.json`.

## License
All four assets: **CC0 1.0 Universal**, raw legal code included as `CC0-1.0.txt` (https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt).
Official asset license evidence: https://polyhaven.com/license . This page explicitly permits commercial use and redistribution (including in a sold product), and says attribution is not required. Credit is nevertheless appropriate: "Assets from Poly Haven (CC0)". No account/payment/checkbox acceptance or executable plugin was used. No third-party code is included or run. These are asset data only. Publisher page imagery/logos are not part of this asset license and are not included.

## Selected assets (all 1K)
- **Modular Urban Apartments Facade**: https://polyhaven.com/a/modular_urban_apartments_facade . `modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf`, binary + 12 JPG PBR textures. 147 individually named modules, 5 materials, 270,045 triangles for the entire catalogue (not a single building). Prefer extracting a small useful subset rather than instantiating the entire demonstration catalogue.
- **Modular Factory Facade**: https://polyhaven.com/a/modular_factory_facade . `modular_factory_facade/modular_factory_facade_1k.gltf`, binary + 15 JPG PBR textures. 192 modules, 6 materials, 175,014 triangles for complete catalogue. Brick, doors, windows, trim and garages support a complementary older industrial street frontage.
- **Asphalt 02**: https://polyhaven.com/a/asphalt_02 . `asphalt_02/` diffuse, OpenGL normal, roughness JPG. Physical repeat width 3 m from official source. Author Rob Tuytel.
- **Concrete Wall 007**: https://polyhaven.com/a/concrete_wall_007 . `concrete_wall_007/` diffuse, OpenGL normal, roughness JPG. Physical repeat width 2.2 m from official source. Authors Charlotte Baglioni (photography), Dario Barresi (processing), Rico Cilliers (tiling).

## Integration notes
- glTF Y-up; mesh vertices use metre-like real-world dimensions (doors ~2.3–2.8 m tall). Nodes have demonstration-layout translations; do not preserve these as building placement.
- Both `*_module_inventory.json` files list every node name/index, local bounds, dimensions, source-layout translation and triangle count. Many windows/doors are locally centred around X=-1.5 rather than origin. Normalize based on actual mesh bounds if desired; architectural grid alignment should respect wall/trim geometry rather than assuming each origin is centred.
- Standard packed ARM textures use R=AO, G=roughness, B=metalness. `nor_gl` is the OpenGL normal direction used by Godot.
- Download glTF material relations are intact. glTF materials may need artistic adaptation for rainy night: darker albedo/wet roughness on roadway, restrained emissive window inserts, avoid adding many dynamic lights.
- These assets are realistic modular meshes with proper texture detail. Use limited near/midrange facades, shared textures/materials, and simplified dark distant volumes rather than repeating the entire high-detail catalogue.
- No HDRI, giant scene, executable add-on, or accounts needed. Total verified asset payload: 36.67 MiB. Original files preserved without modification; project derivatives can be optimized separately.

## Used in v5
Runtime derivatives use Modular Urban Apartments Facade, Asphalt 02 and Concrete Wall 007. Factory Facade was researched/downloaded as an alternative but is not instantiated in this scene. Building assembly and optimization are original local scripts; packed editable Blender source preserves texture dependencies. The runtime assets and packed editable Blender assemblies are included. Re-running assemble_city.py from original catalogue data requires obtaining the licensed source files listed in download_manifest.json into a sibling city_asset_sources directory; those original catalogue downloads are not required to run this project.
