me · MD
# LM2596 Buck Converter — 12 V → 5 V
 
A fixed-output 5 V step-down (buck) converter built around the **LM2596T-5.0** switching regulator, designed in **KiCad 10**. Two-layer through-hole board, 71 × 45 mm, with ground pours on both layers and four M3 mounting holes.
 
This is a prototype design reproduced from a LM2596 design guide. It passes KiCad's electrical and design-rule checks, and the power stage has been verified in LTspice against TI's transient model (see [Simulation](#simulation)) — but it has **not** been prototyped or thermally tested. See [Operating limits](#operating-limits) before building.
 
## Design summary
 
| Parameter | Value |
| --- | --- |
| Regulator | LM2596T-5.0 (fixed 5 V, 150 kHz) |
| Input | 12 V nominal |
| Output | 5 V |
| Output target | 3 A (design target, not a validated rating) |
| Board | 71 × 45 mm, 2 layers, 1.6 mm nominal |
| Mounting | 4 × 3.2 mm M3 holes |
 
Power tracks are 1.25–1.5 mm with a short 0.9 mm switch-pin escape. Both copper layers have GND zones. A 0.35 mm bottom-layer trace carries feedback directly from C3's positive pad. U1 sits near the top edge to allow an external heatsink (heatsink not yet selected).
 
## Bill of materials
 
| Ref | Value | Footprint |
| --- | --- | --- |
| U1 | LM2596T-5.0 | TO-220-5 staggered (Package_TO_SOT_THT) |
| J1 | 12 V input | Phoenix MKDS 5.08 mm 1×02 |
| J2 | 5 V output | Phoenix MKDS 5.08 mm 1×02 |
| C1 | 680 µF / 35 V | CP_Radial D10 mm P5 mm |
| C2 | 100 nF / 50 V | C_Disc D5 mm P5 mm |
| C3 | 220 µF / 25 V | CP_Radial D8 mm P3.5 mm |
| D1 | 1N5822 | DO-201AD P15.24 mm |
| L1 | 33 µH, Isat ≥ 3.5 A | L_Radial D12.5 mm P7 mm |
| H1–H4 | M3 mounting hole | MountingHole 3.2 mm |
 
C1/C2/C3 correspond to Cin/Cin2/Cout in the source guide. No adjustable-output divider is fitted.
 
## Connections
 
| Net | Connected pins |
| --- | --- |
| VIN | J1.1, C1.1, C2.1, U1.1 |
| SW | U1.2, D1.1 (cathode/band), L1.1 |
| +5V | L1.2, C3.1, J2.1, U1.4 (FB) |
| GND | J1.2, C1.2, C2.2, U1.3, U1.5, D1.2 (anode), C3.2, J2.2 |
 
J1 pin 1 is input positive; J2 pin 1 is output positive; both pin 2 terminals are ground. Follow the `+` markings on the electrolytic footprints and the cathode band on D1. U1 uses the staggered TO-220-5 footprint, not a straight five-pin footprint.
 
## Files
 
- `Buck_Converter.kicad_pro` — project file. Open this in KiCad, then double-click the schematic or PCB.
- `Buck_Converter.kicad_sch` — schematic.
- `Buck_Converter.kicad_pcb` — placed, routed board with filled ground zones.
- `sym-lib-table`, `fp-lib-table` — library tables (reference standard KiCad 10 libraries).
- `ltspice/` — LTspice validation of the power stage. `Buck_Converter_LTspice.asc` is the schematic (open it and hit Run); `LM2596_5P0_TRANS.lib` is TI's official LM2596-5.0 transient model, ported from PSpice syntax; `LM2596_5P0_TRANS.asy` is the matching symbol; `Buck_Converter_LTspice.plt` restores the plot panes. All four files must stay together in the same folder.
 
## Validation
 
KiCad 10.0.6 ERC and DRC (with zone refill and schematic parity) both report zero violations, zero unconnected items, and zero parity issues, with no rule exclusions.
 
These checks verify CAD connectivity and geometry only — no prototype measurement or thermal test has been performed.
 
## Simulation
 
The power stage (D1, L1, C1–C3) plus TI's official LM2596-5.0 PSpice transient model were simulated in LTspice (`ltspice/Buck_Converter_LTspice.asc`), 12 V in, 150 kHz switching, transient analysis to steady state:
 
| Load | Simulated output |
| --- | --- |
| 1 A (5 Ω) | 4.99 V |
| 3 A design target (1.667 Ω) | 4.31 V, 120 mV ripple |
 
At the 3 A design target the loop sags to 4.31 V instead of regulating to 5.0 V. This is a real result, not a simulation artifact — it was confirmed by checking that regulation is accurate at light load (1 A) and only degrades as load approaches the design target, consistent with [Operating limits](#operating-limits) already flagging 3 A as unvalidated. Treat 3 A as the point where this design's regulation margin runs out, not as a safe operating current.
 
This is a transient-model simulation, not a hardware measurement — it doesn't account for PCB parasitics, the specific 1N5822's real diode curve, or thermal effects.
 
## Operating limits
 
- **12 V nominal input only** — C1 (35 V) and D1 (40 V) don't support the guide's 7–40 V range.
- **3 A is an unvalidated target** — LTspice shows regulation sagging to 4.31 V at 3 A vs. 4.99 V at 1 A ([Simulation](#simulation)), and the 1N5822 falls short of TI's recommended 3.9 A diode rating at that load.
- Verify real part ratings/footprints before ordering, and bring the board up on a current-limited supply, unloaded first.
 
## Source
 
Reproduced from the LM2596 buck converter design guide, cross-referenced against the [Texas Instruments LM2596 datasheet, Rev. G](https://www.ti.com/lit/ds/symlink/lm2596.pdf) (§9.2.1 and §9.4).
 
