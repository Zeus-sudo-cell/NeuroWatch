# NEURO//WATCH

> A cyberpunk operating-system dashboard built entirely from text.

## Overview

NEURO//WATCH is a futuristic real-time system monitoring dashboard built entirely in Python and rendered using terminal-based ASCII graphics.

The project transforms ordinary system statistics into an immersive visual experience by combining live hardware monitoring with animated terminal art. Instead of displaying plain numbers, NEURO//WATCH presents CPU, memory, disk, network, thermal, battery, and process information through cyberpunk-inspired HUD panels, waveforms, sparklines, DNA animations, and Matrix-style effects.

Built under the Code Olympics 2026 challenge constraints, the project demonstrates how advanced visual interfaces can be created without GUI frameworks, using only Python, ANSI terminal graphics, and creative ASCII rendering techniques.

---

## Features

- Real-time CPU monitoring
- Memory utilization tracking
- Disk usage and I/O statistics
- Live network upload/download monitoring
- Process explorer
- Thermal sensor monitoring
- Battery monitoring
- Animated DNA helix visualization
- Matrix rain effects
- ASCII sparklines and graphs
- Interactive multi-screen dashboard
- Keyboard navigation
- Futuristic boot sequence
- Cyberpunk HUD design

---

## Technology Stack

- Python
- psutil
- ANSI Escape Sequences
- ASCII Graphics
- Terminal UI Rendering

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/neuro-watch.git
cd neuro-watch
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python art.py
```

---

## Controls

| Key | Action |
|------|---------|
| ↑ / ↓ | Navigate Menu |
| Enter | Open Dashboard |
| C | CPU Deep Dive |
| M | Memory & Disk |
| N | Network Monitor |
| T | Thermals & Processes |
| Q | Quit |

---

## Screens

### Home HUD
The central command dashboard displaying live system metrics and animated visualizations.

### CPU Deep Dive
Detailed CPU statistics, utilization history, frequency information, and per-core activity.

### Memory & Disk
Memory allocation, swap usage, disk utilization, and storage activity.

### Network Monitor
Real-time upload/download traffic, connection statistics, and network analytics.

### Thermals & Processes
Temperature monitoring, battery information, uptime statistics, and live process tracking.

---

## Project Goal

The goal of this project was to transform ordinary system monitoring into an immersive visual experience using only terminal graphics and ASCII rendering.

On launch, the application performs a futuristic boot sequence and initializes live hardware sensors.

The dashboard continuously tracks CPU usage, memory consumption, disk activity, network traffic, running processes, battery status, and thermal information.

Instead of displaying plain statistics, the data is visualized through animated waveforms, sparklines, DNA helix animations, Matrix-style effects, and cyberpunk HUD panels.

Users can navigate between dedicated monitoring screens for CPU analysis, memory and disk statistics, network activity, and process monitoring using keyboard controls.

All visual elements are rendered directly in the terminal without any graphical user interface frameworks.

The project demonstrates how real-time data visualization, animation, and interactive dashboards can be created using only Python, psutil, ANSI terminal graphics, and creative ASCII art techniques.

---

## Requirements

```txt
psutil==7.2.2
```

---

## Why This Project?

Most system monitoring tools focus on functionality.

NEURO//WATCH focuses on both functionality and visual experience.

It explores how terminal applications can become engaging, animated, and aesthetically rich while still delivering useful real-time information.

---

## Demo

Record and include a short demonstration video showing:

- Boot sequence
- Home dashboard
- CPU screen
- Memory & Disk screen
- Network monitor
- Process monitor
- Visual effects and animations

---

## License

Created for Code Olympics 2026.
