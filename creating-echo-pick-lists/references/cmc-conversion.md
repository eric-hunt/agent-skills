# CMC Conversion Tables

Convert a detergent's concentration (in %w/v or mM) to %CMC (Critical Micelle Concentration) so the correct calibration suffix (`_BP`, `_SP`, `_SPHigh`, `_GP`, `_GPSA`, `_GPSB`, `_BP2`, `_GPSA2`, `_GPSB2`) can be selected from the [suffix table](../SKILL.md#calibration-source-plate-type-selection) in the main skill.

**How to use:** find the detergent's row, then find where the reagent's actual concentration falls between column values (interpolating if needed) — the column header at that point is the %CMC. Table 1 is keyed on %w/v; Table 2 is keyed on mM. Use whichever matches how the reagent's concentration is expressed.

## Table 1: %CMC → % Weight/Volume

Column headers are %CMC; cell values are the corresponding %w/v concentration for that detergent.

| Detergent     | Type         | MW      | 0   | 2.5      | 5        | 10       | 14       | 50       | 100      | 200      |
| ------------- | ------------ | ------- | --- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| Triton X-100  | Non-ionic    | 628.00  | 0   | 3.88E-04 | 7.75E-04 | 1.55E-03 | 2.17E-03 | 7.75E-03 | 1.55E-02 | 3.10E-02 |
| Tween 20      | Non-ionic    | 1228.00 | 0   | 1.85E-04 | 3.70E-04 | 7.40E-04 | 1.04E-03 | 3.70E-03 | 7.40E-03 | 1.48E-02 |
| SDS           | Anionic      | 288.38  | 0   | 5.00E-03 | 1.00E-02 | 2.00E-02 | 2.80E-02 | 1.00E-01 | 2.00E-01 | 4.00E-01 |
| Brij 35       | Non-ionic    | 1200.00 | 0   | 2.75E-03 | 5.50E-03 | 1.10E-02 | 1.54E-02 | 5.50E-02 | 1.10E-01 | 2.20E-01 |
| NP-40         | Non-ionic    | 680.00  | 0   | 4.48E-03 | 8.95E-03 | 1.79E-02 | 2.51E-02 | 8.95E-02 | 1.79E-01 | 3.58E-01 |
| Chaps         | Zwitterionic | 614.88  | 0   | 1.38E-03 | 2.75E-02 | 5.50E-02 | 7.70E-02 | 2.75E-01 | 5.50E-01 | 1.10E+00 |
| CTAB          | Cationic     | 364.45  | 0   | 9.11E-03 | 1.82E-02 | 3.65E-02 | 5.10E-02 | 1.82E-01 | 3.65E-01 | 7.29E-01 |
| Pluronic F-68 | Non-ionic    | 8350.00 | 0   | 8.25E-04 | 1.65E-03 | 3.30E-03 | 4.62E-03 | 1.65E-02 | 3.30E-02 | 6.60E-02 |

## Table 2: %CMC → mM

Column headers are %CMC; cell values are the corresponding concentration in mM for that detergent.

| Detergent     | Type         | MW      | 0   | 2.5      | 5        | 10       | 14       | 50       | 100      | 200      |
| ------------- | ------------ | ------- | --- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| Triton X-100  | Non-ionic    | 628.00  | 0   | 6.00E-03 | 1.20E-02 | 2.40E-02 | 3.36E-02 | 1.20E-01 | 2.40E-01 | 4.80E-01 |
| Tween 20      | Non-ionic    | 1228.00 | 0   | 1.50E-03 | 3.00E-03 | 6.00E-03 | 8.40E-03 | 3.00E-02 | 6.00E-02 | 1.20E-01 |
| SDS           | Anionic      | 288.38  | 0   | 1.75E-01 | 3.50E-01 | 7.00E-01 | 9.80E-01 | 3.50E+00 | 7.00E+00 | 1.40E+01 |
| Brij 35       | Non-ionic    | 1200.00 | 0   | 2.25E-03 | 4.50E-03 | 9.00E-03 | 1.26E-02 | 4.50E-02 | 9.00E-02 | 1.80E-01 |
| NP-40         | Non-ionic    | 680.00  | 0   | 7.25E-03 | 1.45E-02 | 2.90E-02 | 4.06E-02 | 1.45E-01 | 2.90E-01 | 5.80E-01 |
| Chaps         | Zwitterionic | 614.88  | 0   | 2.25E-03 | 4.50E-03 | 9.00E-03 | 1.26E-02 | 4.50E-02 | 9.00E-02 | 1.80E-01 |
| CTAB          | Cationic     | 364.45  | 0   | 2.50E-02 | 5.00E-02 | 1.00E-01 | 1.40E-01 | 5.00E-01 | 1.00E+00 | 2.00E+00 |
| Pluronic F-68 | Non-ionic    | 8350.00 | 0   | 1.00E-04 | 2.00E-03 | 4.00E-03 | 5.60E-03 | 2.00E-02 | 4.00E-02 | 8.00E-02 |
