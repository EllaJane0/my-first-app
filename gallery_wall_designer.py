import streamlit as st
import json
import math
import uuid
from datetime import datetime
import streamlit.components.v1 as components

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

def get_drag_drop_html(artworks, selected_artworks, wall_width=800, wall_height=600):
    """Generate HTML/CSS/JS for drag and drop functionality"""
    
    # Create artwork thumbnails HTML
    artwork_html = ""
    for artwork in artworks:
        artwork_html += f"""
        <div class="artwork-item" data-id="{artwork['id']}" draggable="true" 
             style="background-color: {artwork['color']}; border: {artwork['frame_width']}px solid #8B4513;">
            <div class="artwork-title">{artwork['title']}</div>
            <div class="artwork-info">{artwork['width']}" x {artwork['height']}"</div>
            <div class="artwork-price">${artwork['price']}</div>
        </div>
        """
    
    # Create wall artworks HTML
    wall_artworks_html = ""
    for artwork in selected_artworks:
        x = artwork.get('wall_x', 0)
        y = artwork.get('wall_y', 0)
        width = artwork['width'] * 3  # Scale for display
        height = artwork['height'] * 3  # Scale for display
        
        wall_artworks_html += f"""
        <div class="wall-artwork" data-id="{artwork['id']}" 
             style="left: {x}px; top: {y}px; width: {width}px; height: {height}px; 
                    background-color: {artwork['color']}; 
                    border: {artwork['frame_width']}px solid #8B4513;">
            <div class="wall-artwork-title">{artwork['title']}</div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .gallery-container {{
                display: flex;
                gap: 20px;
                font-family: Arial, sans-serif;
            }}
            
            .artwork-palette {{
                width: 300px;
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .artwork-palette h3 {{
                margin: 0 0 20px 0;
                color: #333;
                text-align: center;
            }}
            
            .artwork-item {{
                width: 100px;
                height: 80px;
                margin: 10px;
                border-radius: 8px;
                cursor: grab;
                display: inline-block;
                position: relative;
                text-align: center;
                transition: transform 0.2s;
            }}
            
            .artwork-item:hover {{
                transform: scale(1.05);
            }}
            
            .artwork-item:active {{
                cursor: grabbing;
                transform: rotate(5deg);
            }}
            
            .artwork-title {{
                font-size: 10px;
                font-weight: bold;
                color: white;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                margin-top: 5px;
            }}
            
            .artwork-info {{
                font-size: 8px;
                color: white;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            }}
            
            .artwork-price {{
                font-size: 9px;
                font-weight: bold;
                color: #FFD700;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            }}
            
            .wall-canvas {{
                flex: 1;
                min-height: {wall_height}px;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                border: 3px solid #333;
                border-radius: 10px;
                position: relative;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
            }}
            
            .wall-canvas.drag-over {{
                border-color: #007bff;
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            }}
            
            .wall-artwork {{
                position: absolute;
                border-radius: 5px;
                cursor: move;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            
            .wall-artwork:hover {{
                transform: scale(1.02);
                z-index: 10;
            }}
            
            .wall-artwork-title {{
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                text-align: center;
                padding: 2px;
            }}
            
            .wall-header {{
                text-align: center;
                margin: 20px 0;
                color: #333;
            }}
            
            .stats {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(255,255,255,0.9);
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .drop-zone-hint {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #999;
                font-size: 18px;
                text-align: center;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="gallery-container">
            <div class="artwork-palette">
                <h3>🎨 Artwork Collection</h3>
                {artwork_html}
            </div>
            
            <div style="flex: 1;">
                <div class="wall-header">
                    <h2>🖼️ Your Gallery Wall</h2>
                    <p>Drag artworks from the palette to design your wall</p>
                </div>
                
                <div class="wall-canvas" id="wall-canvas" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="stats">
                        <div><strong>Pieces:</strong> <span id="piece-count">{len(selected_artworks)}</span></div>
                        <div><strong>Total:</strong> $<span id="total-cost">{sum(art['price'] for art in selected_artworks)}</span></div>
                    </div>
                    
                    {wall_artworks_html}
                    
                    {'' if selected_artworks else '<div class="drop-zone-hint">Drop artworks here to start designing!</div>'}
                </div>
            </div>
        </div>
        
        <script>
            let draggedElement = null;
            let wallArtworks = {json.dumps(selected_artworks)};
            
            // Add drag event listeners to artwork items
            document.querySelectorAll('.artwork-item').forEach(item => {{
                item.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    e.dataTransfer.setData('text/plain', '');
                }});
            }});
            
            // Add drag event listeners to wall artworks for repositioning
            document.querySelectorAll('.wall-artwork').forEach(item => {{
                item.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    e.dataTransfer.setData('text/plain', '');
                }});
                
                // Double click to remove
                item.addEventListener('dblclick', function(e) {{
                    const artworkId = parseInt(this.dataset.id);
                    wallArtworks = wallArtworks.filter(art => art.id !== artworkId);
                    updateStreamlit();
                    this.remove();
                    updateStats();
                }});
            }});
            
            function allowDrop(ev) {{
                ev.preventDefault();
                ev.currentTarget.classList.add('drag-over');
            }}
            
            function drop(ev) {{
                ev.preventDefault();
                ev.currentTarget.classList.remove('drag-over');
                
                if (!draggedElement) return;
                
                const rect = ev.currentTarget.getBoundingClientRect();
                const x = ev.clientX - rect.left;
                const y = ev.clientY - rect.top;
                
                if (draggedElement.classList.contains('artwork-item')) {{
                    // Adding new artwork
                    const artworkId = parseInt(draggedElement.dataset.id);
                    const artworkData = {json.dumps(artworks)}.find(art => art.id === artworkId);
                    
                    if (artworkData && !wallArtworks.find(art => art.id === artworkId)) {{
                        const newArtwork = {{
                            ...artworkData,
                            wall_x: Math.max(0, x - 50),
                            wall_y: Math.max(0, y - 40)
                        }};
                        
                        wallArtworks.push(newArtwork);
                        createWallArtwork(newArtwork, x - 50, y - 40);
                        updateStreamlit();
                        updateStats();
                    }}
                }} else if (draggedElement.classList.contains('wall-artwork')) {{
                    // Repositioning existing artwork
                    const artworkId = parseInt(draggedElement.dataset.id);
                    const artwork = wallArtworks.find(art => art.id === artworkId);
                    
                    if (artwork) {{
                        artwork.wall_x = Math.max(0, x - 50);
                        artwork.wall_y = Math.max(0, y - 40);
                        
                        draggedElement.style.left = artwork.wall_x + 'px';
                        draggedElement.style.top = artwork.wall_y + 'px';
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
                wallArtwork.style.width = (artwork.width * 3) + 'px';
                wallArtwork.style.height = (artwork.height * 3) + 'px';
                wallArtwork.style.backgroundColor = artwork.color;
                wallArtwork.style.border = artwork.frame_width + 'px solid #8B4513';
                wallArtwork.innerHTML = `<div class="wall-artwork-title">${{artwork.title}}</div>`;
                
                // Add event listeners
                wallArtwork.addEventListener('dragstart', function(e) {{
                    draggedElement = this;
                    e.dataTransfer.setData('text/plain', '');
                }});
                
                wallArtwork.addEventListener('dblclick', function(e) {{
                    const artworkId = parseInt(this.dataset.id);
                    wallArtworks = wallArtworks.filter(art => art.id !== artworkId);
                    updateStreamlit();
                    this.remove();
                    updateStats();
                }});
                
                document.getElementById('wall-canvas').appendChild(wallArtwork);
            }}
            
            function updateStats() {{
                document.getElementById('piece-count').textContent = wallArtworks.length;
                const totalCost = wallArtworks.reduce((sum, art) => sum + art.price, 0);
                document.getElementById('total-cost').textContent = totalCost;
            }}
            
            function updateStreamlit() {{
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
        </script>
    </body>
    </html>
    """
    return html_content

def main():
    st.title("🖼️ Gallery Wall Designer")
    st.markdown("**Drag and drop artworks to create your perfect gallery wall!**")
    
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
        height=700,
        scrolling=False
    )
    
    # Update selected artworks based on component feedback
    if component_value and isinstance(component_value, list):
        st.session_state.selected_artworks = component_value
    
    # Controls section
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Auto-Arrange"):
            # Simple grid arrangement
            if st.session_state.selected_artworks:
                artworks_per_row = math.ceil(math.sqrt(len(st.session_state.selected_artworks)))
                for i, artwork in enumerate(st.session_state.selected_artworks):
                    row = i // artworks_per_row
                    col = i % artworks_per_row
                    artwork['wall_x'] = col * 120
                    artwork['wall_y'] = row * 100
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.selected_artworks = []
            st.rerun()
    
    with col3:
        design_name = st.text_input("Design Name", value=st.session_state.current_design_name, key="design_name_input")
    
    with col4:
        if st.button("💾 Save Design") and design_name and st.session_state.selected_artworks:
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
        
        # Show selected artworks details
        with st.expander("🎨 Selected Artworks Details"):
            for artwork in st.session_state.selected_artworks:
                st.write(f"**{artwork['title']}** by {artwork['artist']} - {artwork['style']} - ${artwork['price']}")
    
    # Load saved designs
    if saved_designs:
        st.markdown("### 📚 Saved Designs")
        selected_design = st.selectbox(
            "Load a saved design:",
            options=[None] + [f"{design['name']} (${design['total_cost']})" for design in saved_designs],
            format_func=lambda x: "Select a design..." if x is None else x
        )
        
        if selected_design and st.button("Load Design"):
            design_name = selected_design.split(" (")[0]
            design = next(d for d in saved_designs if d['name'] == design_name)
            st.session_state.selected_artworks = design['artworks']
            st.session_state.current_design_name = design['name']
            st.rerun()
    
    # Instructions
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Instructions:**
        1. **Drag & Drop**: Drag artworks from the left palette onto the wall canvas
        2. **Reposition**: Drag artworks on the wall to reposition them
        3. **Remove**: Double-click any artwork on the wall to remove it
        4. **Auto-Arrange**: Click the auto-arrange button for a quick grid layout
        5. **Save**: Enter a design name and click save to store your creation
        6. **Load**: Select from saved designs to continue editing
        
        **Tips:**
        - Try different combinations of styles and colors
        - Consider the scale and spacing of your pieces
        - Save multiple variations to compare later
        """)

if __name__ == "__main__":
    main()