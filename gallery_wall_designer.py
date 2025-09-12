import streamlit as st
import json
import math
import uuid
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def create_wall_visualization(selected_artworks, wall_width=120, wall_height=80):
    fig = go.Figure()
    
    # Add wall background
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=wall_width, y1=wall_height,
        fillcolor="lightgray",
        opacity=0.3,
        line=dict(color="black", width=2)
    )
    
    # Add artworks
    for artwork in selected_artworks:
        x = artwork.get('wall_x', 0)
        y = artwork.get('wall_y', 0)
        width = artwork['width'] + (artwork['frame_width'] * 2)
        height = artwork['height'] + (artwork['frame_width'] * 2)
        
        # Add frame
        fig.add_shape(
            type="rect",
            x0=x, y0=y, x1=x+width, y1=y+height,
            fillcolor="brown",
            opacity=0.8,
            line=dict(color="darkbrown", width=1)
        )
        
        # Add artwork
        fig.add_shape(
            type="rect",
            x0=x+artwork['frame_width'], 
            y0=y+artwork['frame_width'], 
            x1=x+width-artwork['frame_width'], 
            y1=y+height-artwork['frame_width'],
            fillcolor=artwork['color'],
            opacity=0.9,
            line=dict(color="black", width=1)
        )
        
        # Add title
        fig.add_annotation(
            x=x + width/2,
            y=y + height/2,
            text=artwork['title'][:15] + ('...' if len(artwork['title']) > 15 else ''),
            showarrow=False,
            font=dict(size=8, color="white"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=1
        )
    
    fig.update_layout(
        title="Gallery Wall Preview",
        xaxis=dict(range=[0, wall_width], title="Width (inches)"),
        yaxis=dict(range=[0, wall_height], title="Height (inches)"),
        showlegend=False,
        height=500,
        plot_bgcolor="white"
    )
    
    return fig

def main():
    st.title("🖼️ Gallery Wall Designer Game")
    st.markdown("Design your perfect gallery wall by selecting and positioning artworks!")
    
    # Load data
    db = load_database()
    artworks = db['artworks']
    saved_designs = db['gallery_designs']
    
    # Initialize session state
    if 'selected_artworks' not in st.session_state:
        st.session_state.selected_artworks = []
    if 'current_design_name' not in st.session_state:
        st.session_state.current_design_name = ""
    if 'wall_dimensions' not in st.session_state:
        st.session_state.wall_dimensions = {'width': 120, 'height': 80}
    
    # Sidebar for artwork selection
    with st.sidebar:
        st.header("🎨 Artwork Catalog")
        
        # Filters
        st.subheader("Filters")
        style_filter = st.selectbox(
            "Style",
            ["All"] + list(set(art['style'] for art in artworks))
        )
        
        price_range = st.slider(
            "Price Range ($)",
            min_value=min(art['price'] for art in artworks),
            max_value=max(art['price'] for art in artworks),
            value=(min(art['price'] for art in artworks), max(art['price'] for art in artworks))
        )
        
        # Filter artworks
        filtered_artworks = [
            art for art in artworks
            if (style_filter == "All" or art['style'] == style_filter) and
               price_range[0] <= art['price'] <= price_range[1]
        ]
        
        st.subheader("Available Artworks")
        for artwork in filtered_artworks:
            with st.expander(f"{artwork['title']} - ${artwork['price']}"):
                st.write(f"**Artist:** {artwork['artist']}")
                st.write(f"**Style:** {artwork['style']}")
                st.write(f"**Dimensions:** {artwork['width']}\" x {artwork['height']}\"")
                st.write(f"**Frame Width:** {artwork['frame_width']}\"")
                
                # Color preview
                st.color_picker("Color Preview", artwork['color'], disabled=True, key=f"color_{artwork['id']}")
                
                if st.button(f"Add to Wall", key=f"add_{artwork['id']}"):
                    if artwork not in st.session_state.selected_artworks:
                        new_artwork = artwork.copy()
                        new_artwork['wall_x'] = len(st.session_state.selected_artworks) * 25
                        new_artwork['wall_y'] = len(st.session_state.selected_artworks) * 15
                        st.session_state.selected_artworks.append(new_artwork)
                        st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🖼️ Your Gallery Wall")
        
        # Wall dimensions
        st.subheader("Wall Settings")
        wall_col1, wall_col2 = st.columns(2)
        with wall_col1:
            st.session_state.wall_dimensions['width'] = st.number_input(
                "Wall Width (inches)", 
                min_value=60, 
                max_value=200, 
                value=st.session_state.wall_dimensions['width']
            )
        with wall_col2:
            st.session_state.wall_dimensions['height'] = st.number_input(
                "Wall Height (inches)", 
                min_value=40, 
                max_value=120, 
                value=st.session_state.wall_dimensions['height']
            )
        
        # Display wall visualization
        if st.session_state.selected_artworks:
            fig = create_wall_visualization(
                st.session_state.selected_artworks,
                st.session_state.wall_dimensions['width'],
                st.session_state.wall_dimensions['height']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select artworks from the sidebar to start designing your gallery wall!")
    
    with col2:
        st.header("🎮 Design Controls")
        
        if st.session_state.selected_artworks:
            st.subheader("Selected Artworks")
            
            total_cost = sum(art['price'] for art in st.session_state.selected_artworks)
            st.metric("Total Cost", f"${total_cost}")
            
            # Artwork positioning
            for i, artwork in enumerate(st.session_state.selected_artworks):
                with st.expander(f"{artwork['title']}"):
                    col_x, col_y = st.columns(2)
                    with col_x:
                        new_x = st.number_input(
                            "X Position", 
                            min_value=0, 
                            max_value=st.session_state.wall_dimensions['width'] - artwork['width'],
                            value=int(artwork.get('wall_x', 0)),
                            key=f"x_{artwork['id']}_{i}"
                        )
                    with col_y:
                        new_y = st.number_input(
                            "Y Position", 
                            min_value=0, 
                            max_value=st.session_state.wall_dimensions['height'] - artwork['height'],
                            value=int(artwork.get('wall_y', 0)),
                            key=f"y_{artwork['id']}_{i}"
                        )
                    
                    st.session_state.selected_artworks[i]['wall_x'] = new_x
                    st.session_state.selected_artworks[i]['wall_y'] = new_y
                    
                    if st.button(f"Remove", key=f"remove_{artwork['id']}_{i}"):
                        st.session_state.selected_artworks.pop(i)
                        st.rerun()
            
            # Auto-arrange button
            if st.button("🎯 Auto-Arrange"):
                # Simple grid arrangement
                artworks_per_row = math.ceil(math.sqrt(len(st.session_state.selected_artworks)))
                for i, artwork in enumerate(st.session_state.selected_artworks):
                    row = i // artworks_per_row
                    col = i % artworks_per_row
                    artwork['wall_x'] = col * (st.session_state.wall_dimensions['width'] // artworks_per_row)
                    artwork['wall_y'] = row * (st.session_state.wall_dimensions['height'] // (len(st.session_state.selected_artworks) // artworks_per_row + 1))
                st.rerun()
        
        # Save/Load designs
        st.subheader("💾 Save/Load Designs")
        
        design_name = st.text_input("Design Name", value=st.session_state.current_design_name)
        
        col_save, col_load = st.columns(2)
        
        with col_save:
            if st.button("Save Design") and design_name and st.session_state.selected_artworks:
                new_design = {
                    'id': str(uuid.uuid4()),
                    'name': design_name,
                    'created_date': datetime.now().isoformat(),
                    'wall_dimensions': st.session_state.wall_dimensions,
                    'artworks': st.session_state.selected_artworks,
                    'total_cost': sum(art['price'] for art in st.session_state.selected_artworks)
                }
                
                db['gallery_designs'].append(new_design)
                save_database(db)
                st.success(f"Design '{design_name}' saved!")
                st.session_state.current_design_name = design_name
        
        with col_load:
            if saved_designs:
                selected_design = st.selectbox(
                    "Load Design",
                    options=[None] + [design['name'] for design in saved_designs],
                    format_func=lambda x: "Select a design..." if x is None else x
                )
                
                if selected_design and st.button("Load"):
                    design = next(d for d in saved_designs if d['name'] == selected_design)
                    st.session_state.selected_artworks = design['artworks']
                    st.session_state.wall_dimensions = design['wall_dimensions']
                    st.session_state.current_design_name = design['name']
                    st.rerun()
        
        # Clear all button
        if st.button("🗑️ Clear All"):
            st.session_state.selected_artworks = []
            st.session_state.current_design_name = ""
            st.rerun()
    
    # Display saved designs
    if saved_designs:
        st.header("📚 Saved Designs")
        for design in saved_designs:
            with st.expander(f"🖼️ {design['name']} - ${design['total_cost']} ({len(design['artworks'])} pieces)"):
                st.write(f"**Created:** {design['created_date'][:10]}")
                st.write(f"**Wall Size:** {design['wall_dimensions']['width']}\" x {design['wall_dimensions']['height']}\"")
                st.write(f"**Artworks:** {', '.join([art['title'] for art in design['artworks']])}")

if __name__ == "__main__":
    main()