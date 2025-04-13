import streamlit as st
import pandas as pd

# Load the CSV file
df = pd.read_csv("output_files/google_sheet_data.csv")  # Replace with your actual file path

# Show the data
st.write("### Interview Schedule", df)

# Convert to CSV
csv_data = df.to_csv(index=False).encode('utf-8')

# Download button
st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name='interview_schedule.csv',
    mime='text/csv'
)