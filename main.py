import os
import json
import logging
import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- 1. Configuration & Initial Setup ---

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler() # Outputs logs to the console
    ]
)
logger = logging.getLogger(__name__)

# Page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Advanced AI Content Planner",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. State Management ---

# Initialize session state variables in a structured way
def initialize_state():
    """Initializes all necessary session state variables."""
    if "app_state" not in st.session_state:
        st.session_state.app_state = {
            "templates": {},
            "history": [],
            "last_prompt": "",
            "last_raw_response": "",
            "google_api_key": "",
            "model": None,
        }
        logger.info("Session state initialized.")

initialize_state()

# --- 3. API & Model Handling ---

def configure_genai():
    """Configures the Generative AI model if the API key is set."""
    api_key = st.session_state.app_state.get("google_api_key")
    if not api_key:
        st.warning("Please enter your Google API Key in the sidebar to begin.")
        return False
    try:
        genai.configure(api_key=api_key)
        st.session_state.app_state["model"] = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Google Generative AI model configured successfully.")
        return True
    except Exception as e:
        st.error(f"Failed to configure Google AI: {e}")
        logger.error(f"Google AI configuration failed: {e}")
        return False

# Caching wrapper to prevent duplicate API calls for the same prompt
@st.cache_data(show_spinner="Calling the AI model...")
def generate_from_model(_model_config, prompt: str) -> dict:
    """
    Generates content from the model and expects a JSON response.
    _model_config is a dummy argument to ensure st.cache_data re-runs if the model changes.
    """
    model = st.session_state.app_state.get("model")
    if not model:
        logger.error("Model not initialized. Cannot generate content.")
        return {"error": "Model not initialized."}

    logger.info(f"Generating content for prompt: {prompt[:100]}...")
    st.session_state.app_state["last_prompt"] = prompt

    try:
        # Instruct the model to respond in JSON format
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        raw_response_text = response.text
        st.session_state.app_state["last_raw_response"] = raw_response_text
        logger.info("Successfully received response from model.")
        return json.loads(raw_response_text)
    except Exception as e:
        logger.error(f"An error occurred during API call: {e}")
        st.session_state.app_state["last_raw_response"] = f"Error: {e}"
        return {"error": f"Failed to generate content. Details: {e}"}


# --- 4. UI Components ---

def render_sidebar():
    """Renders the sidebar UI components."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key Input
        api_key_input = st.text_input(
            "Google API Key",
            type="password",
            help="Get your key from Google AI Studio.",
            value=st.session_state.app_state.get("google_api_key", "")
        )
        if api_key_input != st.session_state.app_state.get("google_api_key"):
            st.session_state.app_state["google_api_key"] = api_key_input
            # Attempt to re-configure the model when the key changes
            if configure_genai():
                st.rerun()

        st.header("📝 Content Settings")
        
        # Content creation settings
        settings = {
            "social_media": st.selectbox("Platform", ["LinkedIn", "Twitter", "Instagram", "Facebook", "YouTube", "TikTok", "Blog"]),
            "content_type": st.selectbox("Content Type", ["Post", "Article Outline", "Image Prompt", "Tagline", "Story", "Video Script", "Thread"]),
            "tone": st.selectbox("Tone", ["Professional", "Casual", "Inspirational", "Humorous", "Educational", "Authoritative"]),
            "audience": st.text_input("Target Audience", "Tech enthusiasts, educators, marketers"),
            "length": st.slider("Desired Length (words)", 50, 1500, 400, 50),
            "language": st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"]),
            "seo_keywords": st.text_input("SEO Keywords (optional)", "AI, content creation, automation"),
        }

        render_template_manager()
        render_debug_info()
        
        return settings

def render_template_manager():
    """Renders the UI for managing prompt templates."""
    with st.sidebar.expander("🗂️ Prompt Template Library", expanded=False):
        templates = st.session_state.app_state["templates"]
        names = ["<Create New>"] + list(templates.keys())
        chosen = st.selectbox("Load or Create Template", names)

        # Determine the base prompt for the text area
        if chosen != "<Create New>":
            base_template = templates.get(chosen, "")
        else:
            base_template = ""
        
        custom_prompt = st.text_area("Edit Prompt Template", value=base_template, height=200, key="prompt_template_editor")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Template Name", value=chosen if chosen != "<Create New>" else "")
            if st.button("💾 Save", use_container_width=True):
                if new_name and custom_prompt.strip() and new_name != "<Create New>":
                    templates[new_name] = custom_prompt
                    st.success(f"Template '{new_name}' saved.")
                    logger.info(f"Saved template: {new_name}")
                else:
                    st.error("Provide a name and prompt to save.")
        
        with col2:
            if chosen != "<Create New>":
                if st.button("🗑️ Delete", use_container_width=True):
                    if chosen in templates:
                        del templates[chosen]
                        st.success(f"Template '{chosen}' deleted.")
                        logger.info(f"Deleted template: {chosen}")
                        st.rerun()

def render_debug_info():
    """Renders an expander with debugging information."""
    with st.sidebar.expander("🐞 Debug Info", expanded=False):
        st.write("**Last Prompt Sent to Model:**")
        st.code(st.session_state.app_state.get("last_prompt", "N/A"), language="text")
        st.write("**Last Raw Response from Model:**")
        st.code(st.session_state.app_state.get("last_raw_response", "N/A"), language="json")

def render_main_content(settings):
    """Renders the main content area of the application."""
    st.title("🧠 Advanced AI Content Planner")
    
    topic = st.text_input("Enter your primary content topic or idea", "The future of AI in personalized education")

    if st.button("🚀 Generate Content", type="primary", use_container_width=True, disabled=not st.session_state.app_state.get("model")):
        if not topic.strip():
            st.error("Please enter a valid topic.")
            return

        # Use the custom prompt from the editor if it's not empty
        prompt_template = st.session_state.get('prompt_template_editor', '').strip()
        
        if prompt_template:
            # Simple variable replacement for user-defined templates
            prompt = prompt_template.format(
                topic=topic,
                platform=settings['social_media'],
                content_type=settings['content_type'],
                tone=settings['tone'],
                audience=settings['audience'],
                length=settings['length'],
                language=settings['language'],
                seo_keywords=settings['seo_keywords']
            )
        else:
            # Build the detailed, structured prompt
            prompt = f"""
            You are an expert content strategist. Generate a content package based on the following specifications.
            Your response MUST be a valid JSON object with the keys "outline", "hashtags", and "image_prompt".

            - **Topic:** "{topic}"
            - **Platform:** {settings['social_media']}
            - **Content Type:** {settings['content_type']}
            - **Tone:** {settings['tone']}
            - **Target Audience:** {settings['audience']}
            - **Desired Length (approx words):** {settings['length']}
            - **Language:** {settings['language']}
            - **SEO Keywords to include:** "{settings['seo_keywords']}"

            **JSON Structure to follow:**
            {{
              "outline": "A detailed, well-structured outline or the full content text, formatted with Markdown.",
              "hashtags": ["list", "of", "relevant", "hashtags"],
              "image_prompt": "A descriptive prompt for an AI image generator (like DALL-E or Midjourney) to create a compelling visual for this content."
            }}
            """

        # The _model_config parameter is a trick to make caching work with the model object
        model_config_id = id(st.session_state.app_state.get("model"))
        result = generate_from_model(model_config_id, prompt)
        
        if result and "error" not in result:
            st.success("Content package generated successfully!")
            
            # Store result in session state for display and history
            st.session_state.generated_content = result
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "settings": settings,
                "result": result
            }
            st.session_state.app_state["history"].insert(0, history_entry)
            logger.info(f"Added new entry to history for topic: {topic}")
        else:
            st.error("Failed to generate content. Check the Debug Info in the sidebar for details.")
            st.session_state.generated_content = None

def render_output_tabs():
    """Renders the output tabs for generated content and history."""
    if "generated_content" in st.session_state and st.session_state.generated_content:
        content_tab, history_tab = st.tabs(["📄 Generated Content", f"🗂️ History ({len(st.session_state.app_state['history'])})"])

        with content_tab:
            render_generated_content(st.session_state.generated_content)
        
        with history_tab:
            render_history()
    else:
        # Show history tab even if there's no new content
        if st.session_state.app_state['history']:
             _, history_tab = st.tabs(["📄 Generated Content", f"🗂️ History ({len(st.session_state.app_state['history'])})"])
             with history_tab:
                render_history()

def render_generated_content(result):
    """Displays the generated content and provides export options."""
    st.subheader("📝 Content Outline / Text")
    st.markdown(result.get("outline", "No outline was generated."))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 Hashtags")
        st.info(" ".join(f"#{tag}" for tag in result.get("hashtags", [])))

    with col2:
        st.subheader("🖼️ AI Image Prompt")
        st.code(result.get("image_prompt", "No image prompt was generated."))

    # Export options
    st.subheader("⬇️ Export")
    export_data = {
        "topic": st.session_state.app_state["history"][0]["topic"],
        **st.session_state.app_state["history"][0]["settings"],
        **result,
        "generated_at": st.session_state.app_state["history"][0]["timestamp"]
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"content_{export_data['topic'].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        df = pd.json_normalize(export_data)
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"content_{export_data['topic'].replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def render_history():
    """Renders the content generation history."""
    st.subheader("Past Content Generations")
    history = st.session_state.app_state["history"]

    if not history:
        st.info("No content has been generated yet.")
        return

    for i, entry in enumerate(history):
        with st.expander(f"**{entry['topic']}** - {datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')}"):
            st.markdown(f"**Platform:** {entry['settings']['social_media']} | **Type:** {entry['settings']['content_type']}")
            st.markdown(f"**Tone:** {entry['settings']['tone']} | **Audience:** {entry['settings']['audience']}")
            
            st.markdown("---")
            st.markdown("**Outline:**")
            st.markdown(entry['result'].get('outline', 'N/A'))
            
            st.markdown("**Hashtags:**")
            st.info(" ".join(f"#{tag}" for tag in entry['result'].get("hashtags", [])))

            if st.button("🗑️ Delete from History", key=f"delete_{i}", use_container_width=True):
                st.session_state.app_state["history"].pop(i)
                logger.info(f"Deleted history entry for topic: {entry['topic']}")
                st.rerun()


# --- 5. Main Application Flow ---

def main():
    """Main function to run the Streamlit app."""
    settings = render_sidebar()
    
    # Only proceed if the model is configured
    if st.session_state.app_state.get("model"):
        render_main_content(settings)
        render_output_tabs()
    else:
        st.info("Enter your Google API Key in the sidebar to activate the planner.")

if __name__ == "__main__":
    main()
