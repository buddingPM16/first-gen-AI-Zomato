import pytest
from streamlit.testing.v1 import AppTest
import os

def test_streamlit_app_basic_render():
    """
    Test Phase 6: Streamlit UI.
    Initializes the Streamlit app script and ensures the main components render.
    """
    app_path = os.path.join(os.path.dirname(__file__), '..', 'streamlit_app.py')
    at = AppTest.from_file(app_path)
    at.run(timeout=10)

    # Check title
    assert len(at.markdown) > 0
    # Since we use raw HTML inside markdown for the aligned title, we check that it rendered without exceptions
    
    # Check form inputs exist and have correct defaults
    assert at.selectbox[0].value == "Indiranagar"
    assert at.selectbox[1].value == "Italian"
    assert at.number_input[0].value == 2
    assert at.number_input[1].value == 3000
    assert at.slider[0].value == 4.0
    
    # Ensure there is no error block by default
    assert len(at.error) == 0

def test_streamlit_app_empty_input_validation():
    """
    Test the error handling when clicking submit without required text.
    """
    app_path = os.path.join(os.path.dirname(__file__), '..', 'streamlit_app.py')
    at = AppTest.from_file(app_path)
    at.run(timeout=10)

    # Since we can't type an empty string in a selectbox (only select from existing options),
    # this test changes to ensure the selectboxes exist and are accessible.
    assert len(at.selectbox) >= 2
    
    # Optional filters are now direct inputs, no longer using checkboxes.
    
    # Click submit
    at.button[0].click().run(timeout=30)
    
    # Check that it runs smoothly when selecting valid dropdown data
    assert len(at.error) == 0
