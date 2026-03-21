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

# Custom CSS to make the UI ultra-premium and Zomato-friendly
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base Font Override */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }

    /* Main App Background Override - Colorful Vibrant */
    .stApp {
        background: linear-gradient(120deg, #ffebee 0%, #fce4ec 50%, #f3e5f5 100%);
    }
    
    /* Center Layout Container & Add Shadow */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        max-width: 800px !important;
    }
    
    /* Form Container (Premium Colorful Card Look) */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(226, 55, 68, 0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stForm"]:hover {
        box-shadow: 0 16px 50px rgba(226, 55, 68, 0.25);
    }
    
    /* Zomato Red Theme for Buttons */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(203, 32, 45, 0.3);
        transition: all 0.3s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(203, 32, 45, 0.4);
    }
    
    /* Input Styling */
    .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #f8fafc !important;
        transition: border-color 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"]:hover, .stNumberInput input:hover {
        border-color: #cb202d !important;
    }

    /* Checkbox & Text Adjustments */
    .stCheckbox span {
        font-weight: 500;
        color: #4a5568;
    }
    
    /* Success/Message Cards */
    .stMarkdown, .stException {
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
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

st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
logo_path = os.path.join(os.path.dirname(__file__), 'phase6_ui_layer', 'zomato_logo.svg')
if os.path.exists(logo_path):
    import base64
    with open(logo_path, "rb") as f:
        svg_bg = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<img src="data:image/svg+xml;base64,{svg_bg}" width="250" alt="Zomato Logo" style="margin-bottom: 10px;">', unsafe_allow_html=True)

st.markdown('<h2 style="margin-top: -10px; color: #1a202c; font-weight: 700; letter-spacing: -0.5px;">Restaurant Recommender</h2>', unsafe_allow_html=True)
st.markdown('<p style="color: #718096; font-size: 1.1rem; margin-bottom: 30px;">Discover highly personalized dining experiences tailored exactly to your taste. 🥂</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
        
        # Direct budget input without a checkbox toggle
        max_price = st.number_input("Max Budget for Two (₹)", min_value=100, max_value=10000, value=3000, step=100, help="Set to maximum (10,000) for virtually no budget limit.")
        
    with col2:
        # Dynamically fetch cuisines for the selected location
        cuisines_list = get_cuisines_for_location(place) if place else ["Italian"]
        if not cuisines_list: # Fallback if empty
            cuisines_list = ["Not Available"]
            
        default_cuisine = cuisines_list.index("Italian") if "Italian" in cuisines_list else 0
        cuisine = st.selectbox("Cuisine Preference", options=cuisines_list, index=default_cuisine)
        
        # Direct slider without a checkbox toggle
        min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1, help="Set to 0.0 to search all ratings.")
        
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
                
                # Display results with premium Markdown wrapping
                st.markdown("<br>", unsafe_allow_html=True)
                st.success("✨ Found your perfect match!")
                
                # Wrap AI response inside a styled card
                st.markdown(
                    f"""
                    <div style="background-color: white; padding: 30px; border-radius: 12px; border: 1px solid #f0f0f0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                        {recommendation}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            except Exception as e:
                st.error(f"An error occurred while generating recommendations: {str(e)}")
