import streamlit as st
import json
import math
import uuid
from datetime import datetime
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="Gallery Wall Designer",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_database():
    with open('artwork_database.json', 'r') as f:
        return json.load(f)

def save_database(data):
    with open('artwork_database.json', 'w') as f:
        json.dump(data, f, indent=2)

@st.cache_data
def get_image_base64(image_path):
    """Convert image to base64 string"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

@st.cache_data  
def get_couch_base64():
    """Get couch image as base64"""
    return get_image_base64("couch.webp")

def get_artwork_pattern(style):
    """Generate CSS pattern based on artwork style"""
    patterns = {
        "Abstract": "radial-gradient(circle at 20% 30%, rgba(255,255,255,0.3) 2px, transparent 2px), radial-gradient(circle at 70% 80%, rgba(0,0,0,0.2) 1px, transparent 1px)",
        "Landscape": "linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%), linear-gradient(-45deg, rgba(255,255,255,0.1) 25%, transparent 25%)",
        "Urban": "linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px), linear-gradient(0deg, rgba(0,0,0,0.1) 1px, transparent 1px)",
        "Botanical": "radial-gradient(circle at 30% 40%, rgba(255,255,255,0.2) 3px, transparent 3px), radial-gradient(circle at 70% 20%, rgba(255,255,255,0.15) 2px, transparent 2px)",
        "Geometric": "linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%)",
        "Seascape": "repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.1) 3px, rgba(255,255,255,0.1) 6px)",
        "Portrait": "radial-gradient(ellipse at center, rgba(255,255,255,0.2) 30%, transparent 60%)",
        "Still Life": "radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 10%, transparent 40%)"
    }
    return patterns.get(style, "")

def get_drag_drop_html(artworks, selected_artworks):
    """Generate HTML/CSS/JS for drag and drop functionality"""
    
    # Get couch image
    couch_base64 = get_couch_base64()
    
    # Create artwork thumbnails HTML with real images
    artwork_html = ""
    for artwork in artworks:
        image_base64 = get_image_base64(artwork['image_path'])
        if image_base64:
            artwork_html += f"""
            <div class="artwork-item" data-id="{artwork['id']}" draggable="true">
                <div class="artwork-visual" style="
                    border: {artwork['frame_width'] * 2}px solid #8B4513;
                    border-radius: 4px;
                    width: 120px;
                    height: 90px;
                    position: relative;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    overflow: hidden;
                ">
                    <img src="data:image/png;base64,{image_base64}" 
                         style="width: 100%; height: 100%; object-fit: cover;" 
                         alt="{artwork['title']}">
                    <div class="artwork-overlay">
                        <div class="artwork-title">{artwork['title']}</div>
                        <div class="artwork-info">{artwork['width']}" × {artwork['height']}"</div>
                        <div class="artwork-price">${artwork['price']}</div>
                    </div>
                </div>
            </div>
            """
    
    # Create wall artworks HTML
    wall_artworks_html = ""
    for artwork in selected_artworks:
        x = artwork.get('wall_x', 0)
        y = artwork.get('wall_y', 0)
        width = artwork['width'] * 4
        height = artwork['height'] * 4
        image_base64 = get_image_base64(artwork['image_path'])
        
        if image_base64:
            wall_artworks_html += f"""
            <div class="wall-artwork" data-id="{artwork['id']}" draggable="true"
                 style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;">
                <div class="wall-artwork-visual" style="
                    border: {artwork['frame_width'] * 3}px solid #654321;
                    width: 100%;
                    height: 100%;
                    border-radius: 3px;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
                    overflow: hidden;
                    position: relative;
                ">
                    <img src="data:image/png;base64,{image_base64}" 
                         style="width: 100%; height: 100%; object-fit: cover;" 
                         alt="{artwork['title']}">
                    <div class="wall-artwork-title">{artwork['title']}</div>
                </div>
            </div>
            """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                background: #f0f0f0;
            }}
            
            .gallery-container {{
                display: flex;
                gap: 20px;
                padding: 20px;
                min-height: 600px;
            }}
            
            .artwork-palette {{
                width: 280px;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                max-height: 600px;
                overflow-y: auto;
            }}
            
            .palette-header {{
                color: #ecf0f1;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #3498db;
            }}
            
            .artwork-item {{
                margin: 15px auto;
                cursor: grab;
                transition: all 0.3s ease;
                user-select: none;
                display: flex;
                justify-content: center;
            }}
            
            .artwork-item:hover {{
                transform: translateY(-5px) scale(1.05);
            }}
            
            .artwork-item:active {{
                cursor: grabbing;
                transform: rotate(2deg) scale(1.1);
            }}
            
            .artwork-overlay {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(transparent, rgba(0,0,0,0.8));
                color: white;
                padding: 8px;
                border-radius: 0 0 4px 4px;
            }}
            
            .artwork-title {{
                font-size: 14px;
                font-weight: bold;
                line-height: 1.2;
                margin-bottom: 2px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            }}
            
            .artwork-info {{
                font-size: 11px;
                opacity: 0.9;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            }}
            
            .artwork-price {{
                font-size: 13px;
                font-weight: bold;
                color: #f1c40f;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            }}
            
            .wall-section {{
                flex: 1;
                display: flex;
                flex-direction: column;
            }}
            
            .wall-header {{
                text-align: center;
                margin-bottom: 20px;
                color: #2c3e50;
            }}
            
            .wall-header h2 {{
                font-size: 24px;
                margin-bottom: 8px;
            }}
            
            .wall-header p {{
                color: #7f8c8d;
                font-size: 16px;
            }}
            
            .wall-canvas {{
                flex: 1;
                min-height: 500px;
                position: relative;
                background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%);
                border-radius: 15px;
                box-shadow: inset 0 0 50px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .wall-canvas::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: 
                    /* Wall texture */
                    repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.03) 3px, rgba(255,255,255,0.03) 6px),
                    repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.02) 3px, rgba(0,0,0,0.02) 6px);
                pointer-events: none;
            }}
            
            .room-elements {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 120px;
                background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.1) 50%, #8b4513 100%);
                pointer-events: none;
            }}
            
            .couch {{
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                width: 300px;
                height: 120px;
                pointer-events: none;
                z-index: 2;
            }}
            
            .couch img {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                filter: drop-shadow(0 5px 15px rgba(0,0,0,0.4));
            }}
            
            .wall-canvas.drag-over {{
                box-shadow: 
                    inset 0 0 50px rgba(0,0,0,0.3),
                    0 0 20px rgba(52, 152, 219, 0.5);
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            }}
            
            .wall-artwork {{
                position: absolute;
                cursor: move;
                transition: transform 0.2s ease;
                z-index: 1;
            }}
            
            .wall-artwork:hover {{
                transform: scale(1.02);
                z-index: 10;
            }}
            
            .wall-artwork-visual {{
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .wall-artwork-title {{
                position: absolute;
                bottom: 5px;
                left: 5px;
                right: 5px;
                background: rgba(0,0,0,0.7);
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                padding: 4px;
                border-radius: 3px;
                text-shadow: none;
            }}
            
            .stats {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.95);
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                min-width: 120px;
                z-index: 5;
            }}
            
            .stat-item {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            .stat-item:last-child {{
                margin-bottom: 0;
                font-weight: bold;
                border-top: 1px solid #ddd;
                padding-top: 8px;
                color: #27ae60;
            }}
            
            .drop-zone-hint {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: rgba(255,255,255,0.8);
                font-size: 24px;
                text-align: center;
                pointer-events: none;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                z-index: 1;
            }}
            
            .drop-zone-hint .icon {{
                font-size: 48px;
                display: block;
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="gallery-container">
            <div class="artwork-palette">
                <div class="palette-header">🎨 Artwork Collection</div>
                {artwork_html}
            </div>
            
            <div class="wall-section">
                <div class="wall-header">
                    <h2>🖼️ Your Gallery Wall</h2>
                    <p>Drag artworks from the palette to design your wall</p>
                </div>
                
                <div class="wall-canvas" id="wall-canvas" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="room-elements">
                        <div class="couch">
                            {"<img src='data:image/webp;base64," + couch_base64 + "' alt='Couch'>" if couch_base64 else ""}
                        </div>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <span>Pieces:</span> <span id="piece-count">{len(selected_artworks)}</span>
                        </div>
                        <div class="stat-item">
                            <span>Total:</span> <span id="total-cost">${sum(art['price'] for art in selected_artworks)}</span>
                        </div>
                    </div>
                    
                    {wall_artworks_html}
                    
                    {'' if selected_artworks else '<div class="drop-zone-hint"><span class="icon">🎨</span>Drag & Drop Artworks Here!</div>'}
                </div>
            </div>
        </div>
        
        <script>
            let draggedElement = null;
            let wallArtworks = {json.dumps(selected_artworks)};
            let artworks = {json.dumps(artworks)};
            
            // Create image mapping for JavaScript access
            const imageMapping = {{
                {', '.join([f'"{artwork["image_path"]}": "{get_image_base64(artwork["image_path"])}"' for artwork in artworks if get_image_base64(artwork["image_path"])])}
            }};
            
            function getImageBase64(imagePath) {{
                return imageMapping[imagePath] || '';
            }}
            
            // Add drag event listeners to artwork items
            document.querySelectorAll('.artwork-item').forEach(item => {{
                item.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    this.style.opacity = '0.5';
                    e.dataTransfer.effectAllowed = 'copy';
                }});
                
                item.addEventListener('dragend', function(e) {{
                    this.style.opacity = '1';
                }});
            }});
            
            // Add drag event listeners to wall artworks
            document.querySelectorAll('.wall-artwork').forEach(item => {{
                item.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    this.style.opacity = '0.7';
                    e.dataTransfer.effectAllowed = 'move';
                }});
                
                item.addEventListener('dragend', function(e) {{
                    this.style.opacity = '1';
                }});
                
                // Double click to remove
                item.addEventListener('dblclick', function(e) {{
                    const artworkId = parseInt(this.dataset.id);
                    wallArtworks = wallArtworks.filter(art => art.id !== artworkId);
                    updateStreamlit();
                    this.remove();
                    updateStats();
                    e.preventDefault();
                }});
            }});
            
            function allowDrop(ev) {{
                ev.preventDefault();
                const wall = ev.currentTarget;
                wall.classList.add('drag-over');
            }}
            
            function drop(ev) {{
                ev.preventDefault();
                const wall = ev.currentTarget;
                wall.classList.remove('drag-over');
                
                if (!draggedElement) return;
                
                const rect = wall.getBoundingClientRect();
                const x = Math.max(10, ev.clientX - rect.left - 50);
                const y = Math.max(10, ev.clientY - rect.top - 50);
                
                if (draggedElement.classList.contains('artwork-item')) {{
                    // Adding new artwork
                    const artworkId = parseInt(draggedElement.dataset.id);
                    const artworkData = artworks.find(art => art.id === artworkId);
                    
                    if (artworkData && !wallArtworks.find(art => art.id === artworkId)) {{
                        const newArtwork = {{
                            ...artworkData,
                            wall_x: x,
                            wall_y: y
                        }};
                        
                        wallArtworks.push(newArtwork);
                        createWallArtwork(newArtwork, x, y);
                        updateStreamlit();
                        updateStats();
                        
                        // Remove drop zone hint if it exists
                        const hint = document.querySelector('.drop-zone-hint');
                        if (hint) hint.style.display = 'none';
                    }}
                }} else if (draggedElement.classList.contains('wall-artwork')) {{
                    // Repositioning existing artwork
                    const artworkId = parseInt(draggedElement.dataset.id);
                    const artwork = wallArtworks.find(art => art.id === artworkId);
                    
                    if (artwork) {{
                        artwork.wall_x = x;
                        artwork.wall_y = y;
                        
                        draggedElement.style.left = x + 'px';
                        draggedElement.style.top = y + 'px';
                        updateStreamlit();
                    }}
                }}
                
                draggedElement = null;
            }}
            
            function createWallArtwork(artwork, x, y) {{
                const wallArtwork = document.createElement('div');
                wallArtwork.className = 'wall-artwork';
                wallArtwork.dataset.id = artwork.id;
                wallArtwork.draggable = true;
                wallArtwork.style.left = x + 'px';
                wallArtwork.style.top = y + 'px';
                wallArtwork.style.width = (artwork.width * 4) + 'px';
                wallArtwork.style.height = (artwork.height * 4) + 'px';
                
                // Get the artwork data with image
                const artworkWithImage = artworks.find(art => art.id === artwork.id);
                const imageBase64 = getImageBase64(artworkWithImage.image_path);
                
                wallArtwork.innerHTML = `
                    <div class="wall-artwork-visual" style="
                        border: ${{artwork.frame_width * 3}}px solid #654321;
                        width: 100%;
                        height: 100%;
                        border-radius: 3px;
                        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
                        overflow: hidden;
                        position: relative;
                    ">
                        <img src="data:image/png;base64,${{imageBase64}}" 
                             style="width: 100%; height: 100%; object-fit: cover;" 
                             alt="${{artwork.title}}">
                        <div class="wall-artwork-title">${{artwork.title}}</div>
                    </div>
                `;
                
                // Add event listeners
                wallArtwork.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    this.style.opacity = '0.7';
                    e.dataTransfer.effectAllowed = 'move';
                }});
                
                wallArtwork.addEventListener('dragend', function(e) {{
                    this.style.opacity = '1';
                }});
                
                wallArtwork.addEventListener('dblclick', function(e) {{
                    const artworkId = parseInt(this.dataset.id);
                    wallArtworks = wallArtworks.filter(art => art.id !== artworkId);
                    updateStreamlit();
                    this.remove();
                    updateStats();
                    
                    // Show drop zone hint if no artworks left
                    if (wallArtworks.length === 0) {{
                        const hint = document.querySelector('.drop-zone-hint');
                        if (hint) hint.style.display = 'block';
                    }}
                    e.preventDefault();
                }});
                
                document.getElementById('wall-canvas').appendChild(wallArtwork);
            }}
            
            function getArtworkPattern(style) {{
                const patterns = {{
                    "Abstract": "radial-gradient(circle at 20% 30%, rgba(255,255,255,0.3) 2px, transparent 2px), radial-gradient(circle at 70% 80%, rgba(0,0,0,0.2) 1px, transparent 1px)",
                    "Landscape": "linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%), linear-gradient(-45deg, rgba(255,255,255,0.1) 25%, transparent 25%)",
                    "Urban": "linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px), linear-gradient(0deg, rgba(0,0,0,0.1) 1px, transparent 1px)",
                    "Botanical": "radial-gradient(circle at 30% 40%, rgba(255,255,255,0.2) 3px, transparent 3px), radial-gradient(circle at 70% 20%, rgba(255,255,255,0.15) 2px, transparent 2px)",
                    "Geometric": "linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%)",
                    "Seascape": "repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.1) 3px, rgba(255,255,255,0.1) 6px)",
                    "Portrait": "radial-gradient(ellipse at center, rgba(255,255,255,0.2) 30%, transparent 60%)",
                    "Still Life": "radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 10%, transparent 40%)"
                }};
                return patterns[style] || "";
            }}
            
            function updateStats() {{
                document.getElementById('piece-count').textContent = wallArtworks.length;
                const totalCost = wallArtworks.reduce((sum, art) => sum + art.price, 0);
                document.getElementById('total-cost').textContent = '$' + totalCost;
            }}
            
            function updateStreamlit() {{
                // Post message to parent Streamlit app
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: wallArtworks
                }}, '*');
            }}
            
            // Remove drag over class when dragging leaves
            document.getElementById('wall-canvas').addEventListener('dragleave', function(e) {{
                if (!this.contains(e.relatedTarget)) {{
                    this.classList.remove('drag-over');
                }}
            }});
            
            // Prevent default drag behavior on images
            document.addEventListener('dragover', function(e) {{
                e.preventDefault();
            }});
        </script>
    </body>
    </html>
    """
    return html_content

def main():
    st.title("🖼️ Gallery Wall Designer")
    st.markdown("**Create your perfect gallery wall with drag and drop!**")
    
    # Load data
    db = load_database()
    artworks = db['artworks']
    saved_designs = db['gallery_designs']
    
    # Initialize session state
    if 'selected_artworks' not in st.session_state:
        st.session_state.selected_artworks = []
    if 'current_design_name' not in st.session_state:
        st.session_state.current_design_name = ""
    
    # Create drag and drop interface
    drag_drop_html = get_drag_drop_html(artworks, st.session_state.selected_artworks)
    
    # Display the drag and drop component
    component_value = components.html(
        drag_drop_html,
        height=650,
        scrolling=False
    )
    
    # Update selected artworks based on component feedback
    if component_value and isinstance(component_value, list):
        st.session_state.selected_artworks = component_value
    
    # Controls section
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Auto-Arrange", help="Arrange artworks in a grid pattern"):
            if st.session_state.selected_artworks:
                artworks_per_row = min(3, len(st.session_state.selected_artworks))
                for i, artwork in enumerate(st.session_state.selected_artworks):
                    row = i // artworks_per_row
                    col = i % artworks_per_row
                    artwork['wall_x'] = 50 + col * 150
                    artwork['wall_y'] = 50 + row * 120
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All", help="Remove all artworks from the wall"):
            st.session_state.selected_artworks = []
            st.rerun()
    
    with col3:
        design_name = st.text_input("Design Name", value=st.session_state.current_design_name, placeholder="Enter design name...")
    
    with col4:
        if st.button("💾 Save Design", help="Save your current gallery design") and design_name and st.session_state.selected_artworks:
            new_design = {
                'id': str(uuid.uuid4()),
                'name': design_name,
                'created_date': datetime.now().isoformat(),
                'artworks': st.session_state.selected_artworks,
                'total_cost': sum(art['price'] for art in st.session_state.selected_artworks)
            }
            
            db['gallery_designs'].append(new_design)
            save_database(db)
            st.success(f"Design '{design_name}' saved!")
            st.session_state.current_design_name = design_name
    
    # Display current selection info
    if st.session_state.selected_artworks:
        st.markdown("### 📊 Current Selection")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Artworks", len(st.session_state.selected_artworks))
        
        with col2:
            total_cost = sum(art['price'] for art in st.session_state.selected_artworks)
            st.metric("Total Cost", f"${total_cost}")
        
        with col3:
            styles = set(art['style'] for art in st.session_state.selected_artworks)
            st.metric("Styles", len(styles))
    
    # Load saved designs
    if saved_designs:
        st.markdown("### 📚 Load Saved Design")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_design = st.selectbox(
                "Choose a design:",
                options=[None] + [f"{design['name']} (${design['total_cost']} - {len(design['artworks'])} pieces)" for design in saved_designs],
                format_func=lambda x: "Select a design..." if x is None else x
            )
        
        with col2:
            if selected_design and st.button("Load", help="Load the selected design"):
                design_name = selected_design.split(" (")[0]
                design = next(d for d in saved_designs if d['name'] == design_name)
                st.session_state.selected_artworks = design['artworks']
                st.session_state.current_design_name = design['name']
                st.rerun()
    
    # Instructions
    with st.expander("ℹ️ How to Use This Gallery Designer"):
        st.markdown("""
        **Getting Started:**
        1. **Drag & Drop**: Drag colorful artwork thumbnails from the left palette onto the wall
        2. **Reposition**: Drag artworks around the wall to find the perfect arrangement
        3. **Remove**: Double-click any artwork on the wall to remove it
        
        **Features:**
        - 🎨 **Visual Artworks**: Each piece has unique patterns and colors based on its style
        - 🛋️ **Room Context**: See how your gallery looks above a couch
        - 📊 **Live Stats**: Track piece count and total cost in real-time
        - 💾 **Save & Load**: Save your designs and load them later
        - 🎯 **Auto-Arrange**: Quick grid layout for easy starting point
        
        **Tips:**
        - Try mixing different styles and colors for visual interest
        - Consider spacing and scale when arranging pieces
        - Save multiple variations to compare different arrangements
        """)

if __name__ == "__main__":
    main()