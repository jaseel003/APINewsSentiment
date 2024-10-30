import streamlit as st
import pg8000
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Function to connect to the PostgreSQL database using pg8000

def get_connection():
    try:
        conn = pg8000.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Function to fetch sentiment analysis data from the database
def fetch_data():
    query = """
    SELECT id, title, description, url, published_at, sentiment->>'compound' AS sentiment_score
    FROM news_articles;
    """
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error
        finally:
            conn.close()
    return pd.DataFrame()

# Function to apply color formatting based on sentiment score
def sentiment_color(score):
    if score > 0.1:
        color = 'background-color: #c6efce; color: #006100;'  # Green for positive sentiment
    elif score < -0.1:
        color = 'background-color: #ffc7ce; color: #9c0006;'  # Red for negative sentiment
    else:
        color = 'background-color: #ffffff; color: #9c5700;'  # Yellow for neutral sentiment
    return color

# Streamlit app layout
st.title('Sentiment Analysis Dashboard')

# Fetching the data
st.write("Fetching data from the database...")
data = fetch_data()

# Display data in a table with sentiment colors
if not data.empty:
    st.write("Data loaded successfully!")
    
    # Convert sentiment score to float
    data['sentiment_score'] = data['sentiment_score'].astype(float)
    
    # Apply color formatting
    styled_data = data.style.applymap(sentiment_color, subset=['sentiment_score'])
    
    st.write("Sentiment Analysis Data:")
    st.dataframe(styled_data)

    # Display basic statistics
    st.write("Sentiment Score Statistics:")
    st.write(data['sentiment_score'].describe())

    # Plot sentiment scores
    st.write("Sentiment Score Distribution:")
    st.bar_chart(data['sentiment_score'])

    # Option to filter by sentiment score
    st.write("Filter by Sentiment Score")
    sentiment_threshold = st.slider("Sentiment Score Threshold", min_value=-1.0, max_value=1.0, value=0.0)
    filtered_data = data[data['sentiment_score'] >= sentiment_threshold]
    
    # Apply color formatting to filtered data
    styled_filtered_data = filtered_data.style.applymap(sentiment_color, subset=['sentiment_score'])
    
    st.write(f"Articles with Sentiment Score >= {sentiment_threshold}")
    st.dataframe(styled_filtered_data)
else:
    st.write("No data available.")
