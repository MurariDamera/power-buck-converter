me · MD
# LM2596 Buck Converter — 12 V → 5 V
 
A fixed-output 5 V step-down (buck) converter built around the **LM2596T-5.0** switching regulator, designed in **KiCad 10**. Two-layer through-hole board, 71 × 45 mm, with ground pours on both layers and four M3 mounting holes.
 
This is a prototype design reproduced from a LM2596 design guide. It passes KiCad's electrical and design-rule checks but has **not** been simulated, prototyped, or thermally tested. See [Operating limits](#operating-limits) before building.
 
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
 
C1/C2/C3 correspond to Cin/Cin2/Cout in the source guide. No adjustable-output divider is fitted. `BOM.csv` lists values and assigned footprints — it is not a fully sourced purchasing BOM.
 
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
- `BOM.csv` — component values and assigned footprints.
- `sym-lib-table`, `fp-lib-table` — library tables (reference standard KiCad 10 libraries).
- `build_design.py` — the generator that produced the project, schematic, and board. **Running it overwrites those files, including any manual edits.** Normal editing should be done in KiCad directly.
- `verify_connectivity.py` — checks an exported netlist against the four expected nets above. Requires a `reports/netlist.xml` exported from KiCad.
Fabrication outputs (Gerbers, drills) are not included — export them from KiCad when you're ready to order.
 
## Validation
 
KiCad 10.0.6 ERC and DRC (with zone refill and schematic parity) both report zero violations, zero unconnected items, and zero parity issues, with no rule exclusions.
 
These checks verify CAD connectivity and geometry only. **No LTspice simulation, prototype measurement, thermal test, or control-loop stability test has been performed.**
 
## Operating limits
 
**Use 12 V nominal input.** The guide's 7–40 V range is not a valid rating for this board with its 35 V input capacitor (C1) and 40 V diode. The regulator's own voltage limit does not set the assembled board's limit.
 
**3 A is a target, not a validated rating.** TI's LM2596 datasheet (§9.2.1.2.4) calls for a diode current rating ≥ 1.3× max load — 3.9 A at 3 A load. The 1N5822 does not meet this; it was retained to reproduce the guide. Select a higher-rated Schottky and verify its footprint before a 3 A build. U1 needs thermal design and a heatsink at high load.
 
Before ordering parts or boards, select real manufacturer parts and confirm each footprint/rating:
 
- **U1** — LM2596T-5.0 fixed-output, staggered TO-220 lead dimensions matching the footprint.
- **L1** — 33 µH, saturation ≥ 3.5 A with margin, adequate RMS rating, low DCR; footprint is 12.5 mm dia / 7 mm pitch. Footprint geometry does not establish current rating.
- **C1** — 680 µF / 35 V low-ESR aluminium electrolytic, 10 mm dia / 5 mm pitch, adequate ripple rating.
- **C3** — 220 µF / 25 V low-ESR aluminium electrolytic, 8 mm dia / 3.5 mm pitch; size ESR/ripple per TI's output-cap guidance. Do not substitute a ceramic/polymer part by capacitance alone.
- **C2** — 100 nF / ≥ 50 V, disc, 5 mm pitch.
- **D1** — DO-201AD, 15.24 mm formed lead pitch; band faces the footprint's K marking.
- **J1 / J2** — 5.08 mm pitch, rated for the intended current.
Start prototype testing with a current-limited 12 V supply: confirm unloaded 5 V output, then increase load while watching output ripple and component temperatures.
 
## Source
 
Reproduced from the LM2596 buck converter design guide, cross-referenced against the [Texas Instruments LM2596 datasheet, Rev. G](https://www.ti.com/lit/ds/symlink/lm2596.pdf) (§9.2.1 and §9.4).
 
