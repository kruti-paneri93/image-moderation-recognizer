import streamlit as st
from PIL import Image
import io
from rekognition_helper import RekognitionHelper

# Page configuration
st.set_page_config(
    page_title="Smart Image Moderator",
    page_icon="🛡️",
    layout="wide"
)

# Initialize Rekognition helper
@st.cache_resource
def get_rekognition_helper():
    return RekognitionHelper()

rekognition = get_rekognition_helper()

# Title and description
st.title("🛡️ Smart Image Moderator")
st.markdown("""
Upload an image to detect inappropriate content using **AWS Rekognition**.
This tool identifies: explicit content, violence, drugs, alcohol, and more.
""")

# Sidebar for settings
st.sidebar.header("⚙️ Settings")
confidence_threshold = st.sidebar.slider(
    "Confidence Threshold (%)",
    min_value=0,
    max_value=100,
    value=60,
    help="Minimum confidence level to flag content as inappropriate"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Detection Categories")
st.sidebar.markdown("""
- Explicit Nudity
- Suggestive Content
- Violence
- Visually Disturbing
- Rude Gestures
- Drugs
- Tobacco
- Alcohol
- Gambling
- Hate Symbols
""")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png'],
        help="Supported formats: JPG, JPEG, PNG"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'JPEG')
        image_bytes = img_byte_arr.getvalue()
        
        # Analyze button
        if st.button("🔍 Analyze Image", type="primary"):
            with st.spinner("Analyzing image..."):
                # Detect moderation labels
                moderation_response = rekognition.detect_moderation_labels(
                    image_bytes,
                    min_confidence=confidence_threshold
                )
                
                # Analyze safety
                safety_analysis = rekognition.analyze_safety(
                    moderation_response,
                    threshold=confidence_threshold
                )
                
                # Store results in session state
                st.session_state['analysis'] = safety_analysis

with col2:
    st.subheader("📋 Analysis Results")
    
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        # Display verdict
        if analysis['is_safe'] is None:
            st.error(f"⚠️ {analysis['verdict']}: {analysis['message']}")
        elif analysis['is_safe']:
            st.success(f"{analysis['verdict']}")
            st.info(analysis['message'])
        else:
            st.error(f"{analysis['verdict']}")
            st.warning(analysis['message'])
        
        # Display detailed labels
        if analysis['labels']:
            st.markdown("---")
            st.markdown("### 🏷️ Detected Labels")
            
            for label in analysis['labels']:
                confidence = label['Confidence']
                name = label['Name']
                parent_name = label.get('ParentName', '')
                
                # Color code based on confidence
                if confidence >= 80:
                    color = "🔴"
                elif confidence >= 60:
                    color = "🟡"
                else:
                    color = "🟢"
                
                # Display label
                if parent_name:
                    st.markdown(f"{color} **{parent_name} → {name}**: {confidence:.1f}%")
                else:
                    st.markdown(f"{color} **{name}**: {confidence:.1f}%")
                
                # Progress bar
                st.progress(confidence / 100)
        else:
            if analysis['is_safe']:
                st.balloons()
                st.success("🎉 No inappropriate content detected!")
    else:
        st.info("👆 Upload an image and click 'Analyze' to see results")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by <strong>AWS Rekognition</strong> | Built with <strong>Streamlit</strong></p>
    <p style='font-size: 0.8em; color: gray;'>⚠️ This tool is for educational purposes. Results may not be 100% accurate.</p>
</div>
""", unsafe_allow_html=True)