---
name: creating-echo-pick-lists
description: Reference for designing Echo 525 liquid handler methods and Echo Cherry Pick pick lists — instrument transfer limits, source-plate/calibration selection by fluid composition, source-well selector notation, and the pick list CSV header. Use when the user asks to design a method for an Echo 525, create or format a pick list for the Echo, choose a source plate type or calibration code, or troubleshoot Echo transfer volumes, dead volume, or well notation.
metadata:
  author: Eric Hunt
  version: "1.0"
license: MIT
---

# Echo 525 Pick List Design

This skill documents the _idiomatic_ format for an Echo 525 pick list — the target to design toward, sourced from Beckman Coulter's own sample pick lists and instrument documentation.

## Instrument limits

| Description              | Specification                                                                                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Drop transfer resolution | 25 nL                                                                                                                                                |
| Volume transfer range    | 25 nL – 5 µL, one well to one well.<br>25 nL – 45 µL, one well to many wells.<br>_Actual range depends on fluid type and assay (destination) plate._ |

## Source plate / labware selection

Compatible source plates for the Echo 525:

|                            | 384PP Plate | 384PP Plus Plate | 384LDV Plus Plate | Echo Qualified Reservoir |
| -------------------------- | ----------- | ---------------- | ----------------- | ------------------------ |
| Number of wells            | 384         | 384              | 384               | 6                        |
| Surface treated            | No          | Yes              | Yes               | Yes                      |
| Stated volume range (µL)   | 20–65       | 20–65            | 4.5–14            | 250–2800                 |
| Stated working volume (µL) | 45          | 45               | 9.5               | 2550                     |
| Actual volume range (µL)   | 24–62       | 24–62            | 6–12              | 300–2500                 |
| Actual working volume (µL) | 38          | 38               | 6                 | 2200                     |

**"Stated" vs. "Actual":** stated figures come from the datasheet; actual figures are the empirically-validated, more conservative numbers recommended by New England Biolabs scientists. Prefer _actual_ working volume when sizing source wells for a method.

The 384PP Plus plate is the preferred general-purpose source plate; the 384PP plate may compromise accuracy/precision for some fluid types and destination plates. 384PP Plus and the Echo Qualified Reservoir are Echo 525-only (not compatible with other Echo models). Beckman Coulter recommends 384PP Plus over 384PP for 1536-well destination targets.

### Calibration (_Source Plate Type_) selection

The _Source Plate Type_ string required by the Echo — e.g. `384PP_AQ_BP`, `384LDV_AQ_GP`, `6RES_AQ_BP2` — encodes both the physical plate **and** the fluid's composition (surfactant/CMC, glycerol, protein). It is not just the plate's part number; a given physical plate has several valid calibration strings depending on what's in it.

Prefix by plate, suffix by fluid composition:

| Source Plate             | Prefix          |
| ------------------------ | --------------- |
| 384PP Plate              | `384PP_AQ`      |
| 384PP Plus Plate         | `384PP_Plus_AQ` |
| 384LDV Plus Plate        | `384LDV_AQ`     |
| Echo Qualified Reservoir | `6RES_AQ`       |

| Suffix    | 384PP     | 384PP Plus                 | 384LDV Plus    | Reservoir                  |
| --------- | --------- | -------------------------- | -------------- | -------------------------- |
| `_BP`     | 0–2% CMC  | 0–5% CMC                   | N/A            | N/A                        |
| `_SP`     | 5–50% CMC | 2.5–50% CMC                | N/A            | N/A                        |
| `_SPHigh` | 200% CMC  | N/A                        | N/A            | N/A                        |
| `_GP`     | N/A       | 0–50% glycerol, 0–5% CMC   | 0–50% glycerol | N/A                        |
| `_GPSA`   | N/A       | 0–50% glycerol, 5–14% CMC  | N/A            | N/A                        |
| `_GPSB`   | N/A       | 0–50% glycerol, 14–50% CMC | N/A            | N/A                        |
| `_BP2`    | N/A       | N/A                        | N/A            | 0–30% glycerol, 0–2% CMC   |
| `_GPSA2`  | N/A       | N/A                        | N/A            | 0–30% glycerol, 2–30% CMC  |
| `_GPSB2`  | N/A       | N/A                        | N/A            | 0–30% glycerol, 30–50% CMC |

CMC = Critical Micelle Concentration (surfactant threshold). Example fluids: `384PP_AQ_BP` = buffer with protein; `384PP_Plus_AQ_GP` = buffer with glycerol and protein; `6RES_AQ_GPSA2` = buffer with 0–30% glycerol and 2.5–30% CMC surfactant.

**Converting a reagent's concentration to %CMC:** when the surfactant concentration is known in %w/v or mM rather than %CMC directly, use [references/cmc-conversion.md](references/cmc-conversion.md) — per-detergent lookup tables (Triton X-100, Tween 20, SDS, Brij 35, NP-40, Chaps, CTAB, Pluronic F-68) converting %CMC to %w/v and to mM. Find where the reagent's concentration falls in the detergent's row to read off %CMC, then use that value in the suffix table above.

Empirical dead/max-fill volumes and Echo insert type per plate are in the table above (Actual columns) — wicking can further cap max fill for high-CMC fluids in 384PP Plus (40 µL cap at 50–200% CMC) and 384LDV Plus (8 µL cap for 2 h at 50% CMC).

## Pick list format

### Standard header

Use this column order for import into Echo Cherry Pick:

```
Source Plate Type,Source Plate Barcode,Source Well,Transfer Volume,Destination Plate Type,Destination Plate Barcode,Destination Well
```

### Source well selector notation

| Example           | Meaning                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `A1`              | A single source well.                                                                      |
| `B1:B5`           | A contiguous range, position-paired 1:1 with a matching destination range (e.g. `P2:P6`).  |
| `{A1:P1}`         | A pooled region — any well in the braced range holds identical content; transfer from one. |
| `{A1;A2;A7;A8}`   | A discrete pooled set — semicolon-separated, non-contiguous wells with identical content.  |
| `{A1;A2;B6:B16}`  | Discrete wells and a range can be mixed inside one pooled selector.                        |
| `{C1:C6;K12:K18}` | Multiple pooled ranges in one selector.                                                    |

### The four canonical pick list flavors (Echo Cherry Pick sample files)

Each flavor has its own column set — not a subset of one universal schema. Sample files: [references/384-384_NextAvailableWell.csv](references/384-384_NextAvailableWell.csv), [references/384-384_Explicit.csv](references/384-384_Explicit.csv), [references/384_Controls.csv](references/384_Controls.csv), [references/ComplexPickList.csv](references/ComplexPickList.csv).

- **NextAvailableWell** — `Source Plate Barcode,Source Well` only. No transfer volume, destination, or plate type per row — destination is "next available well," with plate-copy/replicate count and transfer volume set in protocol settings.
- **Explicit** — `Source Plate Barcode,Source Well,Destination Plate Barcode,Destination Well,Transfer Volume`. Explicit per-row destination and volume; plate copies/replicates must be 1. No plate type column — calibration is set once in protocol settings, not per row.
- **Controls** — `Source Plate Barcode,Source Well,Destination Well,Transfer Volume`. No destination plate barcode (implicitly the same destination plate as the Explicit/NextAvailableWell list it's paired with) and no plate type; scoped to controls, combinable with either of the above.
- **ComplexPickList** — `Source Plate Barcode,Source Plate Type,Source Well,Destination Plate,Destination Well,Transfer Volume,Description`. Full form: source barcode + calibration type, a (possibly pooled) source well selector, one destination plate/well, and transfer volume (`Description` is annotation in the sample only, not a real import field). This is the flavor the [Standard header](#standard-header) above is modeled on.

**Every one of these four samples includes `Source Plate Barcode`**, which is why the Standard header requires it too — it's not needed for a single-source-plate run, but becomes required once a method pools reagents across multiple physical source plates.

## Designing a method — workflow

1. Identify each reagent's fluid composition (protein? surfactant/CMC %? glycerol %?) and pick the calibration suffix from the table above.
2. Pick the physical source plate (prefix) — default to 384PP Plus unless dead-volume economy (384LDV Plus) or reservoir-scale bulk reagent (Echo Qualified Reservoir) is needed.
3. Size source wells against the plate's _actual_ (not stated) working volume, plus the instrument's per-well dead volume.
4. Confirm every required transfer falls in 25 nL–5 µL (well-to-well) or up to 45 µL (well-to-many, i.e. pooled source); split across additional pooled source wells if not.
