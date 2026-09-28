import streamlit as st
import os
from google import genai
from supabase import create_client

st.set_page_config(page_title="AI Journal", layout="centered")
st.title("📝 AI Daily Journal Engine")

# Fetch keys securely from environment variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not all([GEMINI_KEY, SUPABASE_URL, SUPABASE_KEY]):
    st.error("Setup Incomplete: Missing cloud environment secret keys.")
else:
    # Initialize connection clients
    ai_client = genai.Client(api_key=GEMINI_KEY)
    db_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    user_entry = st.text_area("Write about your day or ideas:")

    if st.button("Analyze & Save Log", type="primary"):
        if not user_entry.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Processing with cloud brain..."):
                try:
                    # 1. Ask Gemini to extract a core summary action item
                    prompt = f"Extract a one-sentence, bulleted action item or main takeaway from this journal entry: {user_entry}"
                    response = ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    ai_result = response.text
                    
                    # 2. Save the result straight to your Supabase cloud database
                    data_to_save = {"content": f"Entry: {user_entry} | AI Insight: {ai_result}"}
                    db_client.table("journal_logs").insert(data_to_save).execute()
                    
                    st.success("Successfully processed and saved to database!")
                    st.subheader("🤖 AI Extracted Action Item:")
                    st.markdown(ai_result)
                    
                except Exception as e:
                    st.error(f"Error during cloud run: {e}")
