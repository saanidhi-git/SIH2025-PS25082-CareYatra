import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ================= Functions =================
def load_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx") or uploaded_file.name.endswith(".xls"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Please upload only CSV or Excel files!")
            return None
        return df
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

def plot_graphs(df, column):
    plots = {}
    
    # Pie Chart
    fig1, ax1 = plt.subplots()
    df[column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax1)
    ax1.set_title(f"Pie Chart of {column}")
    plots["pie"] = fig1
    
    # Bar Graph
    fig2, ax2 = plt.subplots()
    df[column].value_counts().plot.bar(ax=ax2)
    ax2.set_title(f"Bar Graph of {column}")
    ax2.set_ylabel("Count")
    plots["bar"] = fig2
    
    return plots

def save_graphs(plots, save_path, file_name, user_id):
    folder = os.path.join(save_path, str(user_id))
    os.makedirs(folder, exist_ok=True)
    
    plots["pie"].savefig(os.path.join(folder, f"{file_name}_pie.png"))
    plots["bar"].savefig(os.path.join(folder, f"{file_name}_bar.png"))
    return folder

# ================= Streamlit App =================
st.title(" File Upload & Plotter (Streamlit Version)")
st.title("📊 File Upload & Plotter (Streamlit Version)")

# File uploader
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    df = load_file(uploaded_file)
    if df is not None:
        st.success(f"File `{uploaded_file.name}` uploaded successfully!")
        
        # Column selection
        numeric_columns = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
        if numeric_columns:
            column = st.selectbox("Select a numeric column to plot:", numeric_columns)
            
            if column:
                plots = plot_graphs(df, column)
                
                # Show Plots
                st.pyplot(plots["pie"])
                st.pyplot(plots["bar"])
                
                # Save option
                st.subheader("💾 Save Graphs")
                save_path = st.text_input("Enter the base save path (folder must exist)", "./graphs")
                user_id = st.text_input("Enter User ID (folder will be created with this ID)")
                
                if st.button("Save Graphs"):
                    if save_path and user_id:
                        folder = save_graphs(plots, save_path, os.path.splitext(uploaded_file.name)[0], user_id)
                        st.success(f"✅ Graphs saved in: {folder}")
                    else:
                        st.error("Please provide both Save Path and User ID!")
        else:
            st.error("No numeric columns found in the uploaded file.")