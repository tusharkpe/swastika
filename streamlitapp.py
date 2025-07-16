# app.py
import streamlit as st
import pandas as pd
from groq import Groq

# Setup
st.set_page_config(page_title="Review Insights", layout="centered")
st.title("Review Insight Assistant")

uploaded_file = st.file_uploader("Upload cleaned customer reviews CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload a cleaned CSV file to begin.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
country = st.sidebar.selectbox("Shipping Country", ["All"] + sorted(df['Shipping Country'].dropna().unique().tolist()))
min_rating, max_rating = st.sidebar.slider("Rating Range", 1, 5, (1, 5))
product = st.sidebar.selectbox("Product Category", ["All"] + sorted(df['Product Category Cleaned'].dropna().unique().tolist()))

# Apply filters
filtered_df = df.copy()
if country != "All":
    filtered_df = filtered_df[filtered_df["Shipping Country"] == country]
if product != "All":
    filtered_df = filtered_df[filtered_df["Product Category Cleaned"] == product]
filtered_df = filtered_df[(filtered_df["Rating"] >= min_rating) & (filtered_df["Rating"] <= max_rating)]

# Show filtered data preview
st.write("🔍 Filtered Data Sample", filtered_df.head())

# Input question
question = st.text_area("Ask a question about the reviews:")
system_prompt = (
    "You are a helpful data analyst assistant. Your answer is only from the provided data. Do not make assumptions or use external knowledge. "
    "Answer the user's question clearly and concisely based only on the provided all data.Do not use a None data for your answer. "
    "Use plain language and avoid technical details or code. "
    "Your responses should be no more than 2–3 short sentences unless asked for more detail."
)
# Ask button
if st.button("Ask"):
    if question:
        groq_client = Groq(api_key="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")

        prompt = f"""You are a data analyst. Use the following dataframe to answer the question.
Data sample:
{filtered_df[['Product Category Cleaned', 'Rating', 'Review Content', 'Fulfillment Status', 'Order Value', 'Shipping Country']].to_dict(orient='records')}

Question:
{question}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        st.success("Answer:")
        st.write(response.choices[0].message.content)
    else:
        st.warning("Please type a question.")
