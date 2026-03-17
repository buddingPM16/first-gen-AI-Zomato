import streamlit as st
import sys
import os
import sqlite3

# Define database path for UI queries (relative to project root)
DB_PATH = os.path.join(os.path.dirname(__file__), 'phase3_indexing_storage', 'zomato.db')

# Add project root to path to reuse the LLM generator directly
sys.path.append(os.path.dirname(__file__))
from phase4_llm_integration.llm_recommender import generate_recommendation

st.set_page_config(page_title="Zomato Restaurant Recommender", page_icon="🍽️", layout="centered")

# Custom CSS to make the UI more Zomato-friendly
st.markdown("""
    <style>
    /* Zomato Red Theme */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #cb202d !important;
        color: white !important;
        border-color: #cb202d !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #e23744 !important;
        border-color: #e23744 !important;
    }
    /* Hide Streamlit header anchor link (the chain link icon) */
    .css-10trblm, h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a {
        display: none !important;
    }
    .st-emotion-cache-10trblm {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Render Zomato SVG Logo
logo_path = os.path.join(os.path.dirname(__file__), 'phase6_ui_layer', 'zomato_logo.svg')
if os.path.exists(logo_path):
    # Base64 encode SVG to display cleanly in markdown
    import base64
    with open(logo_path, "rb") as f:
        svg_bg = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<img src="data:image/svg+xml;base64,{svg_bg}" width="300" alt="Zomato Logo" style="margin-bottom: 5px;">', unsafe_allow_html=True)

st.markdown('<h3 style="text-align: left; margin-top: -15px; color: #333333; font-weight: 500;">Restaurant Recommender</h3>', unsafe_allow_html=True)
st.markdown('<p style="text-align: left; color: #666666;">Enter your preference and get personalized restaurant suggestion 🍽️</p>', unsafe_allow_html=True)

@st.cache_data
def get_locations():
    """
    Fetches distinct locations directly from the local SQLite database.
    """
    if not os.path.exists(DB_PATH):
        return ["Indiranagar"]
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT location FROM restaurants WHERE location IS NOT NULL")
    locations = sorted([row[0] for row in cursor.fetchall()])
    conn.close()
    return locations

@st.cache_data
def get_cuisines_for_location(location: str):
    """
    Fetches available cuisines for a SPECIFIC location from the database.
    """
    if not os.path.exists(DB_PATH):
        return ["Italian"]
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT cuisines FROM restaurants WHERE location = ? AND cuisines IS NOT NULL", (location,))
    all_cuisines_raw = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Process cuisines into a flat unique set
    unique_cuisines = set()
    for row in all_cuisines_raw:
        for c in row.split(','):
            unique_cuisines.add(c.strip().title())
            
    cuisines = sorted(list(unique_cuisines))
    
    return cuisines

locations_list = get_locations()

with st.form("preference_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Fallback to defaults if list is somehow empty
        default_loc = locations_list.index("Indiranagar") if "Indiranagar" in locations_list else 0
        place = st.selectbox("Location / Neighborhood", options=locations_list, index=default_loc)
        
        apply_budget = st.checkbox("Limit Budget", value=True)
        if apply_budget:
            max_price = st.number_input("Max Budget for Two (₹)", min_value=100, max_value=10000, value=2000, step=100)
        else:
            max_price = None
        
    with col2:
        # Dynamically fetch cuisines for the selected location
        cuisines_list = get_cuisines_for_location(place) if place else ["Italian"]
        if not cuisines_list: # Fallback if empty
            cuisines_list = ["Not Available"]
            
        default_cuisine = cuisines_list.index("Italian") if "Italian" in cuisines_list else 0
        cuisine = st.selectbox("Cuisine Preference", options=cuisines_list, index=default_cuisine)
        
        apply_rating = st.checkbox("Minimum Rating", value=True)
        if apply_rating:
            min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
        else:
            min_rating = None
        
    st.markdown("<br>", unsafe_allow_html=True)
    # Center the form submit button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        submit_button = st.form_submit_button(label="Find Me Food! 🚀", use_container_width=True)

if submit_button:
    if not place or not cuisine:
        st.error("Please provide both a location and a cuisine preference.")
    else:
        with st.spinner(f"Searching for the best {cuisine} spots in {place} and asking AI to review them..."):
            try:
                # Call our core LLM engine
                recommendation = generate_recommendation(
                    place=place,
                    cuisine=cuisine.lower(),
                    max_price=float(max_price) if max_price is not None else None,
                    min_rating=float(min_rating) if min_rating is not None else None,
                    top_n=5
                )
                
                # Display results
                st.success("Here are your recommendations!")
                st.markdown("---")
                st.markdown(recommendation)
                
            except Exception as e:
                st.error(f"An error occurred while generating recommendations: {str(e)}")
