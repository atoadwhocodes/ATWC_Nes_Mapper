# Uploaded pack review and 0031 decisions

Reviewed representative sheets at native resolution and archive contents. This is an integration suitability review, not an exhaustive animation-frame audit.

| Pack | Findings | Decision |
|---|---|---|
| WILLIBAB Overworld | Native 1x terrain, miniature buildings, forest, water, mountains and volcanic variants. Supplied README credits Willibab / Monsteretrope and states CC BY without a version. | Selected terrain and miniature buildings integrated in 0031. Retain supplied credit and license. |
| The Jade Pack | Four color families; distinctive roofs, shop signs, interiors, furniture and banners. Supplied README states CC-BY without a version or explicit author name. | Reserve for a coherent themed settlement; not mixed into existing farm. |
| Free Jade Update | Two style folders, directional character sheets and color variations. | Reserve for a later NPC pass; confirm attribution/terms before distribution. |
| Classic Quest Town | Native 1x modular shops and larger town buildings, doorways and signs; also 2x/3x copies. README credits Willibab, states CC BY and separately prohibits raw asset redistribution. | Good local town candidate. Not integrated or copied into this build. |
| Cat Side-Kicks 12 Colors | Twelve cat strips; inspected orange 112x16 sheet (seven 16px cells). | Good companion candidate, requires animation/behavior mapping and license confirmation. Not integrated. |
| Colour 16x16 Retro Characters 3 Skin Tones | Color and skin-tone folders, character poses and weapon/action sheets. Representative green character and weapon sheets inspected. | Future NPC/character source; simplify to sprite palettes and confirm terms before distribution. Not integrated. |

## NES conversion
0031 converts selected WILLIBAB source regions into native 2bpp CHR. Each metatile selects one background palette; the regional map has a dedicated palette family with day, dusk and night variants. Shared background color remains green by day. Slot 0 (sky), slot 3 and slot 6 (water animation) are excluded from regional art allocation. Sprite tile 0..3 in page128 retains the miniature farmer.

The first 65536 CHR bytes, collision maps and existing destination coordinates are unchanged from 0030. The mapper's existing banking loads region-specific CHR; no new mapper capability is claimed. Artwork conversion is deterministic, with 51 unique background tiles used out of 160 available.

Public GitHub source changes exclude uploaded asset sheets and ROM binaries. This private build package includes the selected CC BY overworld sheets with the supplied attribution. Other packs remain separate uploads.
