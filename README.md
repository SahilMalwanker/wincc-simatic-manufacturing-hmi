<p align="center">
  <img src="assets/banner.svg" alt="Manufacturing Station HMI - paint manufacturing use case" width="100%">
</p>

<p align="center">
  <img alt="TIA Portal V17" src="https://img.shields.io/badge/TIA%20Portal-V17-0f6e78?style=flat-square">
  <img alt="SIMATIC WinCC Advanced" src="https://img.shields.io/badge/SIMATIC%20WinCC-Advanced-0f6e78?style=flat-square">
  <img alt="HMI TP700 Comfort" src="https://img.shields.io/badge/HMI-TP700%20Comfort-2f9e5b?style=flat-square">
  <img alt="PLC S7-1500" src="https://img.shields.io/badge/PLC-S7--1500%20%C2%B7%20PROFINET-4f7cac?style=flat-square">
</p>

# Manufacturing Station HMI

<p align="center">
  <b>A manufacturing-station operator interface, from UML requirements to a running SIMATIC touch panel.</b><br>
  Use case: the paint industry. Five ingredient tanks, pigment pumps, valves and an agitated mixing tank,
  operated in MANUAL or recipe-driven AUTO mode.
</p>

**[Download the final TIA Portal project](project/wincc-simatic-manufacturing-hmi.zap17)**
| [Restore instructions](#open-the-project) | [Design](docs/design.md)
| [Engineering reference](docs/hmi-reference.md) | [Test plan](docs/testing.md)

<p align="center">
  <img src="assets/gifs/auto-mode.gif" alt="AUTO mode: confirm the batch, then resin, binder and pigments flow into the mixing tank" width="800">
  <br>
  <sub>AUTO mode - confirm the batch, then resin, binder and pigments flow into the mixing tank.</sub>
</p>

## Project status

**Implemented use case: paint manufacturing and batch mixing.** The control modes, recipes,
alarms, diagnostics and user roles illustrate common manufacturing-station workflows; the
process graphics, tags and parameter bindings in this project are specific to the paint use case.

**Portfolio demonstrator.** This repository contains the HMI design, engineering printout,
recorded runtime evidence and reproducible documentation tooling. It is not a commissioned
plant control system or a safety-certified implementation.

The final `.zap17` is included unchanged under a neutral filename. **The archive retains its
original internal names and metadata**; only the public documentation and selected media are
anonymised. Restore and runtime compilation have not been verified in this environment.

The Python tools reproduce documentation data and charts, not the HMI runtime.

## Highlights

| Feature | What it does |
| --- | --- |
| **Live process mimic** | Five tanks, three pigment pumps with rotating impellers, an agitator and colour-coded pipe flow - 130 visibility animations on the main overview alone. |
| **MANUAL and AUTO** | Control-mode selection in the batch pop-up; in MANUAL every valve has its own ON / OFF pop-up. |
| **Recipes and batches** | WinCC recipe with 10 parameters (pigment, resin, solvent, viscosity, gloss, pH, mixing time, ...), data records stored on the panel, batch ID, size and start time per batch. |
| **Alarm overview** | 24 labelled warning/alarm tiles; five have configured tag-driven appearance changes. A reset command and a common alarm indicator demonstrate the workflow. |
| **I/O diagnostics** | Screens label 20 inputs and 20 outputs; the printout exposes 19 DI tags and 20 DO tags. See the documented mapping gaps. |
| **Role-based access** | Administrator, Operator and Engineer groups with WinCC authorizations, logon dialog, user view and the current user in the header. |
| **Bilingual runtime** | English and German texts on every screen, switched with a flag button. |
| **Process parameters** | Setpoints and actual values for flow, level, viscosity, density, temperature, pressure, mixing speed and pH. |

**Known limits:** the pigment parameter columns share setpoint tags, the I/O mapping has gaps,
and alarm acknowledgment is incomplete. See the [engineering reference](docs/hmi-reference.md).
The design models describe intended behavior; the printout and recordings show this build's scope.

## Demo

<details>
<summary><b>Watch manual control, alarms, language switching and recipes</b></summary>

| Manual valve control | Alarm handling |
| :---: | :---: |
| <img src="assets/gifs/manual-valves.gif" alt="Manual mode: valve pop-ups switch pipe segments on and off" width="400"> | <img src="assets/gifs/alarms.gif" alt="Alarm indicator, then flashing warning and alarm tiles" width="400"> |
| **Language switch EN / DE** | **Recipe management** |
| <img src="assets/gifs/language-switch.gif" alt="Digital I/O screens switching between English and German" width="400"> | <img src="assets/gifs/recipes.gif" alt="Recipe view: select, load and transfer a recipe" width="400"> |

</details>

<p align="center">
  <img src="assets/gifs/hardware.gif" alt="The HMI running on a real SIMATIC TP700 Comfort panel" width="480">
  <br>
  <sub>The same project running on a real SIMATIC TP700 Comfort panel.</sub>
</p>

The curated, silent process walkthrough (2 min 57 s) is in
[assets/video/hmi-walkthrough.mp4](assets/video/hmi-walkthrough.mp4).
Media uses visible privacy masks over account names and branding; login/account-entry and
company-introduction scenes are omitted from the video. Masks do not change process values.

<details>
<summary><b>Walkthrough chapters</b></summary>

| Time | Chapter |
| --- | --- |
| 00:00 | Main overview in MANUAL mode |
| 00:22 | Recipe management: edit, save and load records |
| 01:10 | Batch details and control-mode selection |
| 01:14 | Manual valve control |
| 01:41 | AUTO mode with animated pipe flow |
| 01:58 | Process parameters |
| 02:18 | Digital inputs and outputs, English and German |
| 02:38 | Alarm indicator and alarm status |

</details>

## Screens

| Process overview | Parameters |
| :---: | :---: |
| <a href="assets/screens/main-overview-auto.png"><img src="assets/screens/main-overview-auto.png" alt="Main overview in AUTO mode" width="400"></a> | <a href="assets/screens/parameters.png"><img src="assets/screens/parameters.png" alt="Parameter screen" width="400"></a> |
| **Alarm status** | **Recipe management** |
| <a href="assets/screens/alarm-status.png"><img src="assets/screens/alarm-status.png" alt="Warning and alarm tiles" width="400"></a> | <a href="assets/screens/recipe-management.png"><img src="assets/screens/recipe-management.png" alt="Recipe view" width="400"></a> |

<details>
<summary><b>More screens: manual control, batch data, diagnostics and users</b></summary>

| Manual overview | Batch details |
| :---: | :---: |
| <img src="assets/screens/main-overview-manual.png" alt="Manual overview" width="400"> | <img src="assets/screens/batch-details.png" alt="Batch details" width="400"> |
| **Digital inputs** | **Digital outputs (German)** |
| <img src="assets/screens/digital-inputs.png" alt="Digital input status" width="400"> | <img src="assets/screens/digital-outputs-de.png" alt="Digital output status in German" width="400"> |
| **Valve control** | **User management** |
| <img src="assets/screens/valve-control.png" alt="Valve control" width="400"> | <img src="assets/screens/user-management.png" alt="User management with names masked" width="400"> |

</details>

<sub>Runtime captures, 800 x 480 px. The four featured images link to their full-size versions.</sub>

## Architecture

```mermaid
flowchart LR
    U(["Operator<br/>Engineer<br/>Administrator"])
    HMI["<b>SIMATIC TP700 Comfort</b><br/>WinCC Runtime Advanced<br/>8 screens · 7 pop-ups · 3 templates<br/>recipe with 10 elements<br/>3 user groups · EN / DE"]
    PLC["<b>SIMATIC S7-1500</b><br/>CPU 1516-3 PN/DP<br/>PainMix_DB · Paramters_Paint_Mix<br/>Recipe · DI · DO"]
    P[("<b>Paint station</b><br/>5 tanks · 3 pigment pumps<br/>valves · agitated mixing tank")]
    U -->|touch| HMI
    HMI <-->|"PROFINET · S7 connection<br/>116 PLC tags, symbolic"| PLC
    PLC <-->|"20 DI · 20 DQ"| P
    classDef hmi fill:#dff0f1,stroke:#0f6e78,color:#10343a
    classDef plc fill:#e3ecf8,stroke:#4f7cac,color:#1f2933
    classDef proc fill:#fbefe0,stroke:#f2a541,color:#1f2933
    class HMI hmi
    class PLC plc
    class P proc
```

The panel (192.168.1.25) talks to the CPU (192.168.1.1) over `HMI_Connection_1`; tags are read
cyclically (1 s, 500 ms for language and agitator) through symbolic access to five PLC data sources.

## Process and I/O

<details>
<summary><b>Ingredient flow and I/O address diagram</b></summary>

```mermaid
flowchart LR
    RE[("Resin enhancer<br/>low I0.0 · high I0.1 · overflow I0.2")]
    SB[("Solvent binder<br/>low I0.3 · high I0.4 · overflow I0.5")]
    RP[("Red pigment<br/>low I0.6 · high I0.7")]
    GP[("Green pigment<br/>low I1.1 · high I1.2")]
    BP[("Blue pigment<br/>low I1.4 · high I1.5")]
    PV{{"Pigment circulation Q0.4<br/>pigment inlet valve Q1.0"}}
    MT[("Mixing tank<br/>agitator Q1.1 · running I1.7<br/>high pressure I2.0 · high temp. I2.1<br/>lid open I2.3")]
    OUT(["Outlet / filling"])
    DR(["Drain"])
    RE -->|"pump Q0.0 · inlet valve Q0.1"| MT
    SB -->|"pump Q0.2 · inlet valve Q0.3"| MT
    RP -->|"pump Q0.5 · valve open I1.0"| PV
    GP -->|"pump Q0.6 · valve open I1.3"| PV
    BP -->|"pump Q0.7 · valve open I1.6"| PV
    PV --> MT
    MT -->|"outlet valve Q1.3"| OUT
    MT -->|"drain valve Q1.2"| DR
    classDef red fill:#fbe3e6,stroke:#d1495b,color:#1f2933
    classDef green fill:#e2f4e9,stroke:#2f9e5b,color:#1f2933
    classDef blue fill:#e3ecf8,stroke:#3d6fb6,color:#1f2933
    classDef resin fill:#f6ecdc,stroke:#c08a3e,color:#1f2933
    classDef binder fill:#faf3d4,stroke:#d8b63a,color:#1f2933
    classDef mix fill:#dff0f1,stroke:#0f6e78,color:#1f2933
    class RP red
    class GP green
    class BP blue
    class RE resin
    class SB binder
    class MT,PV mix
```

  </details>

<p align="center">
  <img src="assets/charts/io-map.svg" alt="Process image: 20 digital inputs and 20 digital outputs by subsystem" width="900">
</p>

Safety and utility outputs (alarm light, emergency stop, buzzer, interlock, maintenance lockout,
batch-complete lamp, backup power, exhaust fan) complete the output image. Every address with its
signal name is listed in the [HMI reference](docs/hmi-reference.md#process-io).

## How it was built

The HMI was designed before it was configured: requirements became UML models, the models became a
mock-up driven by HMI usability principles, and the mock-up became the WinCC project.

```mermaid
flowchart LR
    A["Use cases<br/>15 use cases · 3 roles"] --> B["Activity model<br/>operator workflow"]
    B --> C["State model<br/>modes · mixing · alarms"]
    C --> D["Mock-up<br/>9 design considerations"]
    D --> E["WinCC implementation<br/>TIA Portal V17"]
    E --> F["Test plan<br/>16 test cases"]
    F --> G["Deployment<br/>TP700 Comfort"]
```

<details>
<summary><b>State model: intended operating states and transitions</b></summary>

```mermaid
stateDiagram-v2
    state "User logged in" as LoggedIn
    state "Recipe loaded" as RecipeLoaded
    state "Auto mode" as Auto
    state "Flowing complete" as Flowing
    state "Mixing (auto)" as MixAuto
    state "Manual mode" as Manual
    state "Valves OFF" as ValvesOff
    state "Valves ON" as ValvesOn
    state "Mixing (manual)" as MixManual
    state "Parameter setup" as Params
    state "Alarm" as Alarm
    state "Acknowledged" as Acked
    state "Reset" as Reset

    [*] --> LoggedIn: login
    LoggedIn --> Manual: login verified
    LoggedIn --> RecipeLoaded: load / edit recipe
    LoggedIn --> Params: input setpoints
    RecipeLoaded --> Auto: recipe load complete
    Manual --> Auto
    Auto --> Flowing: start flowing pipes
    Flowing --> MixAuto: pipe flow complete
    Manual --> ValvesOff
    ValvesOff --> ValvesOn: valve control pressed
    ValvesOn --> MixManual: agitator ON
    MixAuto --> Alarm: alarm occurs
    MixManual --> Alarm: alarm occurs
    Alarm --> Acked: acknowledge pressed
    Acked --> Reset: reset pressed
    Reset --> [*]
    Params --> [*]
```

  </details>

<details>
<summary><b>Use case and activity diagrams</b></summary>
<br>

<p align="center">
  <img src="assets/diagrams/use-case-diagram.png" alt="Use case diagram" width="720">
</p>
<p align="center">
  <img src="assets/diagrams/activity-diagram.png" alt="Activity diagram" width="900">
</p>

</details>

<details>
<summary><b>Usability principles behind the mock-up</b></summary>

| Principle | Where it shows up in the HMI |
| --- | --- |
| Low cognitive load | one overview with only tank levels, flows and mode; details live on their own screens |
| Pre-attentive processing | flashing yellow warnings and red alarms, warning triangle in the navigation bar |
| Distinguishable colours | ingredient colours on tanks and pipes, distinct MANUAL / AUTO indication |
| Segmented control | a fixed navigation bar from three screen templates |
| Easy recognition of widgets | rotating pump symbols on every pigment line, consistent button positions |
| Affordance | flag button for the language, pop-up buttons that read ON / OFF |
| Direct manipulation | touch a valve symbol to open its control pop-up |
| Limited states | MANUAL or AUTO only, selected in one place |
| Icon grouping with text | icon-and-label buttons such as *Log in* / *Log out* |

</details>

The complete models, the use-case-to-UI mapping and the design approach per UI element are in
[docs/design.md](docs/design.md); the original report is [docs/pdf/hmi-design-report.pdf](docs/pdf/hmi-design-report.pdf).

## By the numbers

Counted by [`tools/tia_printout.py`](tools/tia_printout.py) from the 290-page TIA Portal project documentation.
These describe the supplied printout, not a fresh extraction from the final archive; exact revision
equivalence has not been verified in TIA Portal.

| Screens | Objects | Dynamizations | System functions | HMI tags | Digital I/O | Alarm tiles | Recipe elements |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **8** + 7 pop-ups | **581** | **327** | **82** | **117** | **40** | **24** | **10** |

<p align="center">
  <img src="assets/charts/screen-composition.svg" alt="Configured objects per screen by object type" width="900">
</p>
<details>
<summary><b>Animation and tag-source breakdowns</b></summary>

<p align="center">
  <img src="assets/charts/dynamics.svg" alt="Dynamizations by type and system function calls" width="900">
</p>
<p align="center">
  <img src="assets/charts/tag-sources.svg" alt="HMI tags by PLC data block and data type" width="900">
</p>

</details>

The main overview carries 209 of the 581 objects and 130 of the 136 visibility animations - the pipe
network is drawn from graphic segments that appear while an ingredient flows. Screen-level detail,
tags, I/O, alarms, recipes and user groups are documented in the [HMI reference](docs/hmi-reference.md).

## Testing

16 proposed test cases cover authentication, mode switching, valve control, I/O, tank monitoring,
alarms, parameters, recipes, language, navigation and batch data. The walkthrough illustrates
related workflows, including operation on a real TP700 Comfort panel; it is not a test execution
record and does not establish that all expected outcomes passed. See [docs/testing.md](docs/testing.md).

In this repository, [GitHub Actions](.github/workflows/ci.yml) runs `pytest` on every push: the
parser re-extracts all tables from the TIA Portal printout and compares them with [`data/`](data),
and every local link and image in the documentation is checked.

## Open the project

1. Install a licensed TIA Portal V17 engineering environment with WinCC support for the
  TP700 Comfort and the configured S7-1500 devices.
2. Download [project/wincc-simatic-manufacturing-hmi.zap17](project/wincc-simatic-manufacturing-hmi.zap17).
3. In TIA Portal, use **Project > Retrieve** to restore the archive into a separate working directory.
4. Check device support and project diagnostics, then compile the PLC and HMI before simulation.
5. Review users, credentials, network addresses and safety behavior before connecting hardware.
  Never download this demonstrator to an operating plant without an engineering review.

The archive is a byte-for-byte copy of the supplied final project. ZIP integrity and copy identity
are checked here; TIA Portal restore, compilation and runtime behavior require the vendor tools.
The internal project name may differ from the neutral archive filename.

## Repository structure

```text
wincc-simatic-manufacturing-hmi/
├── assets/
│   ├── banner.svg               animated header
│   ├── charts/                  data-driven charts (generated)
│   ├── diagrams/                UML diagrams
│   ├── gifs/                    runtime animations
│   ├── screens/                 runtime screenshots
│   └── video/                   silent walkthrough (MP4)
├── data/                        tables extracted from the TIA Portal printout
├── project/                     final native TIA Portal V17 archive
├── docs/
│   ├── design.md                UML models, design considerations, design approach
│   ├── hmi-reference.md         device, screens, I/O, alarms, recipes, users, tags
│   ├── testing.md               test plan with walkthrough timestamps
│   └── pdf/                     design report, UML diagrams, TIA Portal project documentation
├── tests/                       pytest suite
├── tools/
│   ├── tia_printout.py          TIA Portal printout -> CSV / JSON
│   └── build_charts.py          CSV / JSON -> SVG charts
└── .github/workflows/ci.yml     tests on every push
```

## Reproduce the data and charts

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python tools/tia_printout.py docs/pdf/tia-portal-project-documentation.pdf --out data
python tools/build_charts.py --data data --out assets/charts
pytest
```

`tia_printout.py` rebuilds the supplied English-language TIA Portal *project documentation* PDF
from glyph positions, font weights and sizes. It is verified against this project's export;
other layouts, languages or projects may require parser changes.

## Tech stack

| Area | Used |
| --- | --- |
| HMI engineering | SIMATIC WinCC Advanced in TIA Portal V17, WinCC Runtime Advanced simulation |
| HMI hardware | SIMATIC TP700 Comfort, 7" touch, 800 x 480 px |
| Controller | SIMATIC S7-1500, CPU 1516-3 PN/DP, PROFINET, symbolic tag access |
| WinCC features | screen templates, pop-up screens, graphic lists, recipes and recipe view, user administration, multilingual texts, scheduled tasks, system functions |
| Modelling | UML use case, activity and state diagrams |
| Tooling | Python, pypdfium2, matplotlib, pytest, GitHub Actions, Mermaid |

## License

Repository-authored tooling and documentation are released under the [MIT License](LICENSE).
Third-party product graphics and software shown in the captures retain their respective rights;
no vendor software or runtime license is included.

SIMATIC, WinCC, TIA Portal and related product names are trademarks of Siemens AG. This is an
independent project; it is not affiliated with or endorsed by Siemens.
