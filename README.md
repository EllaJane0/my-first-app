# Gallery Wall Designer Game

A fun Streamlit application for designing gallery walls with various artworks.

## Features

- Browse and filter artworks by style and price
- Drag and position artworks on a customizable wall
- Auto-arrange functionality for quick layouts
- Save and load gallery designs
- Visual preview with real-time updates
- Cost tracking for your gallery wall

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## How to Run

```bash
streamlit run gallery_wall_designer.py
```

## How to Play

1. **Select Artworks**: Browse the catalog in the sidebar and add artworks to your wall
2. **Position Artworks**: Use the controls to position each piece on your wall
3. **Auto-Arrange**: Click the auto-arrange button for a quick grid layout
4. **Save Your Design**: Give your design a name and save it for later
5. **Load Previous Designs**: Select from your saved designs to continue editing

## Files

- `gallery_wall_designer.py` - Main Streamlit application
- `artwork_database.json` - JSON database containing artwork data and saved designs
- `requirements.txt` - Python dependencies