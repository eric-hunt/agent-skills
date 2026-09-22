---
name: creating-echo-picklists
description: Reference for designing Echo 525 liquid handler methods and Echo Cherry Pick picklists — instrument transfer limits, which bound constrains which end of a transfer, source-plate/calibration selection by fluid composition, source-well selector notation, and the picklist CSV header. Use when the user asks to design a method for an Echo 525, create or format a picklist for the Echo, choose a source plate type or calibration code, or troubleshoot Echo transfer volumes, dead volume, or well notation.
metadata:
  author: Eric Hunt
  version: "1.0"
  summary: Designing Echo 525 liquid handler methods and formatting Cherry Pick picklists
license: MIT
---

# Echo 525 Picklist Design

This skill documents the _idiomatic_ format for an Echo 525 picklist — the target to design toward, sourced from Beckman Coulter's own sample picklists and instrument documentation. It is a standard to reconcile an implementation against, not a description of any one implementation.

## Instrument limits

| Description              | Specification                                                                                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Drop transfer resolution | 25 nL                                                                                                                                                |
| Volume transfer range    | 25 nL – 5 µL, one well to one well.<br>25 nL – 45 µL, one well to many wells.<br>_Actual range depends on fluid type and assay (destination) plate._ |

Source: Beckman Coulter, _Echo 525 Liquid Handler Instructions For Use_, PN 001-11665 Rev 05 (July 2022), §5 Instrument Specifications — which restates the figures from the earlier Labcyte _Technical Specifications_ v2.0 (Dec 2015) unchanged, so they are current rather than a pre-acquisition leftover.

### The two bounds constrain different ends of the transfer

This is the thing to get right, and it is easy to get wrong: reading both as source-side per-row caps leads to the false conclusion that pooling a source lifts the ceiling from 5 µL to 45 µL.

**5 µL well-to-well is a _destination_-side limit, and a fluid-dependent guideline rather than a firmware bound.** The destination plate sits **inverted** above the source. A large bolus of low-surface-tension fluid can fail to stay in the destination well and fall out — onto the source plate, contaminating the stock, which ruins the run and the reagent together. That is what the vendor's qualifier means:

> _NOTE Actual transfer range is dependent on fluid type and assay plate._

In practice (bench experience on a 525, not vendor documentation): aqueous transfers well above 5 µL are routine — ATP in water, or water alone. Buffers formulated with a surfactant such as Triton X-100 are where it bites, and the failure mode is the contamination one above. Nothing about the _source_ arrangement changes this, because the risk is at the destination.

**Working range is a _source_-side limit, and it applies to the pool rather than the well.** A single transfer _can_ span source wells when the selector is pooled — the instrument drains one well of the pool and carries on into the next. A 10 µL reaction's ~9.9 µL water backfill is routinely dispensed from 384LDV Plus labware, whose wells hold only 9.5 µL working, out of a selector like `{A1:H1}`.

Rev 05 states the per-plate form with a third line the 2015 datasheet lacked —

> 25 nL to Working Range (one to many wells)

— and Table 5.1 gives the working range per plate: **45 µL** for 384PP and 384PP Plus, **9.5 µL** for 384LDV Plus, **2550 µL** for 6RES. Note that the headline "45 µL" is simply the 384PP working volume: the instrument limit and the labware limit are the same number because they are the same constraint.

**Consequences for planning.** The retention ceiling depends on the fluid, so it belongs per liquid class rather than as a constant — `BP` and `BP2` (aqueous buffer, protein) have no practical ceiling, while classes carrying surfactant or glycerol have 5 µL. Treat it as a warning to a human rather than a hard failure, since the judgement is empirical. The droplet floor is the opposite: it is a hard bound, and **the check belongs on the volume asked for, not the volume dispensed** — a 13 nL request dispensed as 25 nL passes a dispensed-side check while being a 1.9x inflation of the intended concentration. Pool capacity needs no separate check if pools are sized as `ceiling(total volume / working volume)` wells, which makes a per-row source bound unreachable by construction.

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

**"Stated" vs. "Actual":** stated figures are from the vendor documentation (the IFU's Table 5.1). **The actual figures are bench experience on a 525, not a vendor claim** — they are the more conservative numbers that work in practice, and they exist because the stated ones do not. Prefer _actual_ working volume when sizing source wells for a method.

The stated 20 µL minimum for a 384PP is the clearest case: at that fill the acoustic survey frequently fails, because the depth determination is not accurate enough near the floor of the well. A well filled to the "minimum" is therefore a well the instrument may refuse to survey. Plan against the actual figures by default, and express the difference as an inward **margin** on the vendor specification (`c(4, 3)` µL on a 384PP resolves 20–65 to 24–62) rather than as a second set of absolute volumes — a margin is inward by construction, so "empirical is never more permissive than spec" stays true without anyone checking it.

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

Treat the two halves as **two independent axes on the reagent**: the prefix is a property of the labware the reagent sits in, and the suffix is a property of the fluid itself (its liquid class). Assembling the code from those two plus the instrument's `_AQ_` infix — rather than storing the code as a literal string — means a source plate whose prefix disagrees with its own labware cannot be spelled, and the only reachable error is a liquid class the chosen plate does not offer, which is a question with a real answer.

**Write the liquid class without its leading underscore** (`BP`, not `_BP`). The underscore is the instrument's punctuation joining the two halves, not part of the class name; carrying it into the data means every consumer has to know whether to strip it.

**Converting a reagent's concentration to %CMC:** when the surfactant concentration is known in %w/v or mM rather than %CMC directly, use [references/cmc-conversion.md](references/cmc-conversion.md) — per-detergent lookup tables (Triton X-100, Tween 20, SDS, Brij 35, NP-40, Chaps, CTAB, Pluronic F-68) converting %CMC to %w/v and to mM. Find where the reagent's concentration falls in the detergent's row to read off %CMC, then use that value in the suffix table above.

Empirical dead/max-fill volumes and Echo insert type per plate are in the table above (Actual columns) — wicking can further cap max fill for high-CMC fluids in 384PP Plus (40 µL cap at 50–200% CMC) and 384LDV Plus (8 µL cap for 2 h at 50% CMC).

## Picklist format

### Standard header

The idiomatic column order for import into Echo Cherry Pick:

```
Source Plate Type,Source Plate Barcode,Source Well,Transfer Volume,Destination Plate Type,Destination Plate Barcode,Destination Well
```

`Source Plate Barcode` belongs **per row, read off the source plan** rather than stamped on from a single argument. A real method may draw from more than one physical source plate of the same type, and a scalar applied to every row both loses that distinction and can disagree with the plan describing it.

When pooling multiple plate layouts or runs into one method, insert a `Component` column after `Source Plate Type` to disambiguate which reagent or run a pooled transfer belongs to.

### Source well selector notation

| Example           | Meaning                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `A1`              | A single source well.                                                                      |
| `B1:B5`           | A contiguous range, position-paired 1:1 with a matching destination range (e.g. `P2:P6`).  |
| `{A1:P1}`         | A pooled region — any well in the braced range holds identical content; transfer from one. |
| `{A1;A2;A7;A8}`   | A discrete pooled set — semicolon-separated, non-contiguous wells with identical content.  |
| `{A1;A2;B6:B16}`  | Discrete wells and a range can be mixed inside one pooled selector.                        |
| `{C1:C6;K12:K18}` | Multiple pooled ranges in one selector.                                                    |

**Beyond row Z.** A 1536-well plate is 32 x 48, so its row labels run past `Z` and a single-letter formatter cannot address it. Confirm the instrument's own convention for those labels before emitting them — it is instrument-facing, and a formatter that silently produces a malformed address (rather than refusing) will put volume in the wrong place.

### The four canonical picklist flavors (Echo Cherry Pick sample files)

Each flavor has its own column set — not a subset of one universal schema. Sample files: [references/384-384_NextAvailableWell.csv](references/384-384_NextAvailableWell.csv), [references/384-384_Explicit.csv](references/384-384_Explicit.csv), [references/384_Controls.csv](references/384_Controls.csv), [references/ComplexPickList.csv](references/ComplexPickList.csv).

- **NextAvailableWell** — `Source Plate Barcode,Source Well` only. No transfer volume, destination, or plate type per row — destination is "next available well," with plate-copy/replicate count and transfer volume set in protocol settings.
- **Explicit** — `Source Plate Barcode,Source Well,Destination Plate Barcode,Destination Well,Transfer Volume`. Explicit per-row destination and volume; plate copies/replicates must be 1. No plate type column — calibration is set once in protocol settings, not per row.
- **Controls** — `Source Plate Barcode,Source Well,Destination Well,Transfer Volume`. No destination plate barcode (implicitly the same destination plate as the Explicit/NextAvailableWell list it's paired with) and no plate type; scoped to controls, combinable with either of the above.
- **ComplexPickList** — `Source Plate Barcode,Source Plate Type,Source Well,Destination Plate,Destination Well,Transfer Volume,Description`. Full form: source barcode + calibration type, a (possibly pooled) source well selector, one destination plate/well, and transfer volume (`Description` is annotation in the sample only, not a real import field). This is the flavor the [Standard header](#standard-header) above is modeled on.

**Every one of these four samples includes `Source Plate Barcode`**, which is why the Standard header requires it too — it's not needed for a single-source-plate run, but becomes required once a method pools reagents across multiple physical source plates.

The flavors differ in **which columns exist**, not in how a column is spelled, so each is its own schema rather than a variant of one. Emission is therefore better modelled as a pluggable formatter per flavor than as options on a single writer; the Standard header above is the ComplexPickList-shaped one.

## Designing a method — workflow

1. Identify each reagent's fluid composition (protein? surfactant/CMC %? glycerol %?) and pick the calibration suffix from the table above.
2. Pick the physical source plate (prefix) — default to 384PP Plus unless dead-volume economy (384LDV Plus) or reservoir-scale bulk reagent (Echo Qualified Reservoir) is needed.
3. Size source wells against the plate's _actual_ (not stated) working volume, plus the instrument's per-well dead volume.
4. Confirm every required transfer falls in 25 nL–5 µL (well-to-well) or up to 45 µL (well-to-many, i.e. pooled source); split across additional pooled source wells if not.
