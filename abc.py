import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
from dotenv import load_dotenv

import os

load_dotenv()
api_key = st.secrets["gemini"]["api_key"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

csv_path = "Bulk_Order_Data_v2.csv"  # Update if needed
df = pd.read_csv(csv_path)

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Gemini Data Assistant", layout="wide")
st.title("🤖 Gemini-Powered CSV Data Assistant")
# st.markdown("Upload a CSV file and ask questions about the data using natural language.")



st.success("✅ File uploaded successfully!")
st.write("### 📊 Data Preview", df.head())
st.write("### 📋 Column Names", df.columns.tolist())

    # --- User Query ---
query = st.text_input("🔍 Enter your natural language query")

if query:
    with st.spinner("🧠 Generating Python code using Gemini..."):
        # --- Prepare Gemini Prompt ---
        prompt = f"""
            You are a data assistant. The user has a pandas DataFrame called 'df' with the following columns:
            {df.columns.tolist()}

            Write Python code (using pandas) that answers the following query:
            "{query.strip()}"

                Requirements:
                1. Use the DataFrame 'df' that is already loaded
                2. Write direct executable code, not function definitions
                3. Always print the final result with descriptive text
                4. Only return the Python code inside a code block (no explanation)

                Example format:
                ```python
                result = df.groupby('column').sum()
                print("Results:")
                print(result)
            """
                # --- Call Gemini ---
    try:
        response = model.generate_content(prompt)
        generated_code = response.text
    except Exception as e:
        st.error(f"❌ Error calling Gemini API: {e}")
        st.stop()

    # --- Extract Python Code ---
    code_match = re.search(r"```(?:python)?\n(.*?)```", generated_code, re.DOTALL)
    code_to_run = code_match.group(1) if code_match else generated_code

    # --- Show the Generated Code ---
    st.markdown("### 🧾 Generated Python Code")
    st.code(code_to_run, language="python")
    
        # --- Execute Code ---
    with st.spinner("🚀 Executing the code..."):
        try:
            local_vars = {'df': df.copy(), 'pd': pd, 'print': st.write}
            exec(code_to_run, {'__builtins__': __builtins__, 'pd': pd}, local_vars)
    
            # --- Display result variables ---
            result_vars = {}
            for var_name, var_value in local_vars.items():
                if (var_name not in ['df', 'pd', 'print']
                    and not var_name.startswith('__')
                    and not callable(var_value)):
                    result_vars[var_name] = var_value
    
            if result_vars:
                st.markdown("### 📊 Result Variables:")
                for var_name, var_value in result_vars.items():
                    st.write(f"**{var_name}:**")
                    st.write(var_value)
    
        except Exception as e:
            st.error("❌ Error executing generated code:")
            st.exception(e)
            st.markdown("### 🔧 Debug Code:")
            st.code(code_to_run, language="python")
        else:
            st.info("👆 Please upload a CSV file to begin.")
