import streamlit as st
import os
from google import genai
from supabase import create_client
from datetime import datetime
from st_audrec import st_audrec

# 1. Advanced Page Layout & Theme Styling
st.set_page_config(page_title="AI Voice Memory Diary", layout="wide", page_icon="🔮")

st.markdown("""
    <style>
    .main-title { font-size:40px !important; font-weight: 700; color: #4A90E2; text-align: center; margin-bottom: 20px;}
    .diary-card { padding: 15px; border-radius: 10px; background-color: #f8f9fa; border-left: 5px solid #4A90E2; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🔮 AI Voice Memory Diary Matrix</p>', unsafe_allow_html=True)

# Fetch secure connection keys from cloud environment settings
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not all([GEMINI_KEY, SUPABASE_URL, SUPABASE_KEY]):
    st.error("Setup Incomplete: System keys are missing from environment settings configurations.")
else:
    # Initialize connection clients
    ai_client = genai.Client(api_key=GEMINI_KEY)
    db_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 2. Split Workspace Layout Engine: Left side for inputs, Right side for Calendar
    left_panel, right_panel = st.columns()

    # --- LEFT PANEL: THE INTERACTIVE CONVERSATION ENGINE ---
    with left_panel:
        st.subheader("🎙️ Speak or Chat with Your Diary")
        
        # Browser-based Audio Microphone recorder tool
        st.write("Click below to record your voice entry thoughts naturally:")
        audio_data = st_audrec()
        
        user_input = st.text_area("Alternatively, type a thought thread here:", placeholder="Talk about your day, lessons learned, or goals...")
        
        # If user captures voice, convert it into text using Gemini's audio pipeline
        if audio_data is not None:
            st.audio(audio_data, format="audio/wav")
            if st.button("🤖 Process Voice Input"):
                with st.spinner("Converting voice signals and analyzing content..."):
                    try:
                        response = ai_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[{"mime_type": "audio/wav", "data": audio_data}, "Transcribe this audio precisely. Clear out stutters, structure it like an intimate, meaningful diary statement block."]
                        )
                        user_input = response.text
                        st.success("Voice transcribed successfully! Check the text block below before saving.")
                    except Exception as ex:
                        st.error(f"Voice Analytics Error: {ex}")

        # Sync button to lock entry into calendar rows
        if st.button("💾 Sync Thoughts to Calendar Ledger", type="primary"):
            if not user_input.strip():
                st.warning("Please record audio or type text into your input console first.")
            else:
                with st.spinner("Structuring metadata and syncing timelines safely to cloud..."):
                    try:
                        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Command Gemini to serve as an advanced diary structuring agent
                        ai_structuring_prompt = f"""
                        You are an expert personal psychologist and operational diary editor. 
                        Analyze this raw daily stream of thoughts: "{user_input}"
                        Tasks:
                        1. Structure it into a beautiful chronological diary segment.
                        2. Extract a bulleted checklist summary named 'Core Takeaways & Insights'.
                        Timestamp Context: {current_timestamp}
                        """
                        
                        ai_response = ai_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=ai_structuring_prompt,
                        )
                        processed_diary_entry = ai_response.text
                        
                        # Save final payload string data straight down into your active table row ledger
                        payload = {"content": f"📅 Logged: {current_timestamp}\n\n{processed_diary_entry}"}
                        db_client.table("journal_logs").insert(payload).execute()
                        
                        st.success("Timeline entry successfully cataloged into database!")
                        st.balloons()
                        
                    except Exception as err:
                        st.error(f"Failed to synchronize state matrices: {err}")

    # --- RIGHT PANEL: THE DYNAMIC CHRONOLOGICAL CALENDAR VIEWER ---
    with right_panel:
        st.subheader("📅 Live Calendar Timeline Deck")
        selected_date = st.date_input("Filter your diary logs by choosing a specific calendar date:")
        
        try:
            # Query history ledger data metrics directly from Supabase
            response = db_client.table("journal_logs").select("id, created_at, content").order("id", descending=True).execute()
            data_rows = response.data
            
            if not data_rows:
                st.info("Your database diary folder ledger rows are currently empty.")
            else:
                for row in data_rows:
                    row_date = row['created_at'][:10] # Extract the YYYY-MM-DD string part
                    
                    # Filter matching rows dynamically matching our selector calendar date keys
                    if str(selected_date) == row_date:
                        with st.container():
                            st.markdown(f'<div class="diary-card"><b>📁 Memory Entry Block #{row["id"]}</b> | 🕒 {row["created_at"][11:16]}</div>', unsafe_allow_html=True)
                            st.markdown(row['content'])
                            st.divider()
        except Exception as error_logs:
            st.error(f"Could not load dynamic archive dashboard: {error_logs}")
