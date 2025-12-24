# Scene Optimizer - Omniverse Extension

A powerful extension for NVIDIA Omniverse that analyzes and optimizes USD scenes for improved performance.

## Features

- **Scene Analysis**: Identifies optimization opportunities in USD scenes
- **Duplicate Mesh Detection**: Finds and merges duplicate meshes
- **Material Optimization**: Removes unused materials and optimizes assignments
- **Performance Statistics**: Provides detailed scene statistics
- **Hidden Geometry Removal**: Removes hidden/unused geometry
- **High-Poly Mesh Detection**: Identifies meshes that could benefit from simplification

## Installation

1. Ensure you have NVIDIA Omniverse installed
2. Copy this extension to your Omniverse extensions directory:
   - Windows: `%LOCALAPPDATA%\ov\pkg\`
   - Linux: `~/.local/share/ov/pkg/`
   - macOS: `~/Library/Application Support/ov/pkg/`

3. Restart Omniverse or reload extensions

## Usage

1. Open Omniverse Create or Code
2. Load a USD scene
3. Open the Extension Manager (Window > Extensions)
4. Enable "Scene Optimizer"
5. Open the Scene Optimizer window from the menu
6. Click "Analyze Scene" to identify optimization opportunities
7. Select desired optimizations and click "Apply Optimizations"

## Project Structure

```
scene_optimizer/
├── extension.toml          # Extension configuration
├── extension/
│   ├── __init__.py         # Extension entry point
│   ├── scene_optimizer.py  # Main UI window
│   ├── analyzer.py         # Scene analysis logic
│   ├── optimizer.py       # Optimization implementation
│   └── ui/
│       └── __init__.py    # UI utilities
└── README.md
```

## Development

This extension demonstrates:
- Omniverse Kit extension development
- USD API usage
- Scene graph traversal and manipulation
- UI development with omni.ui
- Performance optimization techniques

## Requirements

- NVIDIA Omniverse (Create or Code)
- Python 3.x
- USD/OpenUSD knowledge



