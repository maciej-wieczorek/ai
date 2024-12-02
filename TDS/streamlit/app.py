import streamlit as st
import requests
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

NOTION_API_KEY = "Bearer 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"
DATABASE_ID = "14f70355651a808995b5e41455c3bdf5"

def fetch_feedback():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Błąd podczas pobierania danych: {response.status_code}")
        return None

def extract_text(rich_text_array):
    return ''.join([text_obj.get('plain_text', '') for text_obj in rich_text_array])

def parse_feedback(data):
    feedback_list = []
    
    for page in data.get('results', []):
        properties = page.get('properties', {})
        
        situation = extract_text(properties.get('Situation', {}).get('title', []))
        action = extract_text(properties.get('Action', {}).get('rich_text', []))
        outcome = extract_text(properties.get('Outcome', {}).get('rich_text', []))
        
        feedback_list.append({
            'situation': situation,
            'action': action,
            'outcome': outcome
        })
    
    return pd.DataFrame(feedback_list)

def filter_feedback(df, term):
    filtered_df = df[df["situation"].str.contains(term, case=False, na=False)]
    return filtered_df

def word_frequency(dataframe):
    text = " ".join(dataframe["situation"].dropna() + ' ' + dataframe["action"].dropna() + ' ' + dataframe["outcome"].dropna()).strip()
    word_counts = Counter(text.split())
    return word_counts.most_common(20)

st.title("MyFeedback Streamlit App")

search_term = st.text_input("Wpisz wyszukiwaną frazę", "")

if st.button("Pobierz dane"):
    raw_data = fetch_feedback()
    if raw_data:
        df = parse_feedback(raw_data)
        st.write("### Oryginalne dane:")
        st.dataframe(df)
        
        filtered = filter_feedback(df, search_term)
        st.write(f"### Wyniki filtrowania ({len(filtered)}):")
        st.dataframe(filtered)

        st.metric("Liczba wszystkich feedbacków", len(df))
        st.metric("Liczba znalezionych feedbacków", len(filtered))

        word_freq = word_frequency(df)
        words, counts = zip(*word_freq)
        plt.barh(words, counts)
        plt.xlabel("Częstotliwość")
        plt.ylabel("Słowa")
        plt.title("20 najczęściej występujących słów")
        st.pyplot(plt)
