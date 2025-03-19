import streamlit as st
from PIL import Image as im
import functions  # Import the functions from functions.py

# --- Streamlit App ---
st.title("E-commerce Catalog Image Generator")

# --- Layout ---
col1, col2 = st.columns(2)

# --- Image 1 Input ---
with col1:
    st.subheader("Reference Image 1")
    image1_input = st.file_uploader("Upload Image 1", type=["jpg", "jpeg", "png"], key="image1")
    desc1_input = st.text_area("Description 1", key="desc1")
    if st.button("Generate Description 1", key="gen_desc1"):
        if image1_input:
            image1 = im.open(image1_input)
            desc1_input = functions.generate_description(image1)
            st.session_state.desc1 = desc1_input
            st.text_area("Description 1", value=desc1_input, key="desc1_output")
        else:
            st.warning("Please upload an image first.")

# --- Image 2 Input ---
with col2:
    st.subheader("Reference Image 2")
    image2_input = st.file_uploader("Upload Image 2", type=["jpg", "jpeg", "png"], key="image2")
    desc2_input = st.text_area("Description 2", key="desc2")
    if st.button("Generate Description 2", key="gen_desc2"):
        if image2_input:
            image2 = im.open(image2_input)
            desc2_input = functions.generate_description(image2)
            st.session_state.desc2 = desc2_input
            st.text_area("Description 2", value=desc2_input, key="desc2_output")
        else:
            st.warning("Please upload an image first.")

# --- Prompt Input ---
st.subheader("Prompt")
prompt_input = st.text_area("Enter your prompt here", key="prompt")

# --- Buttons ---
col3, col4, col5 = st.columns(3)
with col3:
    if st.button("Refine Prompt"):
        if prompt_input:
            refined_prompt = functions.refine_prompt(prompt_input)
            st.session_state.prompt = refined_prompt
            prompt_input = refined_prompt
            st.text_area("Enter your prompt here", value=refined_prompt, key="prompt_output")
        else:
            st.warning("Please enter a prompt first.")
with col4:
    if st.button("Generate Prompt"):
        if desc1_input and desc2_input:
            generated_prompt = functions.generate_prompt(desc1_input, desc2_input)
            st.session_state.prompt = generated_prompt
            prompt_input = generated_prompt
            st.text_area("Enter your prompt here", value=generated_prompt, key="prompt_output")
        else:
            st.warning("Please generate descriptions first.")
with col5:
    if st.button("Generate Image"):
        if image1_input and image2_input and desc1_input and desc2_input and prompt_input:
            image1 = im.open(image1_input)
            image2 = im.open(image2_input)
            generated_images = functions.generate_image(image1, image2, desc1_input, desc2_input, prompt_input)
            if generated_images:
                st.subheader("Generated Images")
                cols = st.columns(4)
                for i, img in enumerate(generated_images):
                    with cols[i]:
                        st.image(img, caption=f"Generated Image {i+1}")
            else:
                st.warning("Image generation failed.")
        else:
            st.warning("Please upload images, generate descriptions, and enter a prompt.")

# --- Styling Suggestions ---
st.subheader("Product Styling")
if st.button("Generate Styling Suggestions"):
    if desc1_input and desc2_input and prompt_input:
        styling_markdown = functions.generate_style_and_convert_to_markdown(desc1_input, desc2_input, prompt_input)
        st.markdown(styling_markdown, unsafe_allow_html=True)
    else:
        st.warning("Please generate descriptions and a prompt first.")
