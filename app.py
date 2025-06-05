import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_generator import generate_sample_data

# Configure the page
st.set_page_config(
    page_title="Interactive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data persistence
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()

# Main title
st.title("Interactive Dashboard")
st.markdown("---")

# Sidebar controls
st.sidebar.header("Dashboard Controls")

# Dataset selection
dataset_option = st.sidebar.selectbox(
    "Select Dataset:",
    ["Sales Data", "Stock Prices", "Weather Data"],
    help="Choose which dataset to visualize"
)

# Plot type selection
plot_type = st.sidebar.selectbox(
    "Select Plot Type:",
    ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot"],
    help="Choose the type of visualization"
)

# Get the selected dataset
current_data = st.session_state.data[dataset_option.lower().replace(' ', '_')]

# Dynamic controls based on dataset
st.sidebar.subheader("Plot Parameters")

# Initialize default values
x_axis = current_data.columns.tolist()[0] if len(current_data.columns) > 0 else None
y_axis = current_data.columns.tolist()[1] if len(current_data.columns) > 1 else current_data.columns.tolist()[0]
color_by = "None"
stock_filter = []
city_filter = []

if dataset_option == "Sales Data":
    x_axis = st.sidebar.selectbox("X-Axis:", current_data.columns.tolist(), index=0)
    y_axis = st.sidebar.selectbox("Y-Axis:", current_data.columns.tolist(), index=1)
    color_by = st.sidebar.selectbox("Color By:", ["None"] + current_data.columns.tolist())
    
elif dataset_option == "Stock Prices":
    x_axis = st.sidebar.selectbox("X-Axis:", current_data.columns.tolist(), index=0)
    y_axis = st.sidebar.selectbox("Y-Axis:", current_data.columns.tolist(), index=1)
    stock_filter = st.sidebar.multiselect(
        "Select Stocks:", 
        current_data['symbol'].unique().tolist(),
        default=current_data['symbol'].unique().tolist()[:3]
    )
    color_by = "symbol"
    
elif dataset_option == "Weather Data":
    x_axis = st.sidebar.selectbox("X-Axis:", current_data.columns.tolist(), index=0)
    y_axis = st.sidebar.selectbox("Y-Axis:", current_data.columns.tolist(), index=1)
    city_filter = st.sidebar.multiselect(
        "Select Cities:",
        current_data['city'].unique().tolist(),
        default=current_data['city'].unique().tolist()[:3]
    )
    color_by = "city"

# Additional plot customization
st.sidebar.subheader("Appearance")
plot_title = st.sidebar.text_input("Plot Title:", value=f"{dataset_option} - {plot_type}")
plot_height = st.sidebar.slider("Plot Height:", 400, 800, 600)
show_grid = st.sidebar.checkbox("Show Grid", value=True)

# Filter data based on selections
filtered_data = current_data.copy()

if dataset_option == "Stock Prices" and len(stock_filter) > 0:
    filtered_data = filtered_data[filtered_data['symbol'].isin(stock_filter)]
elif dataset_option == "Weather Data" and len(city_filter) > 0:
    filtered_data = filtered_data[filtered_data['city'].isin(city_filter)]

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"{plot_title}")
    
    # Create the plot based on selection
    fig = None
    
    try:
        if plot_type == "Scatter Plot":
            if color_by != "None" and color_by in filtered_data.columns:
                fig = px.scatter(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_by,
                    title=plot_title,
                    height=plot_height
                )
            else:
                fig = px.scatter(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis,
                    title=plot_title,
                    height=plot_height
                )
                
        elif plot_type == "Line Chart":
            if color_by != "None" and color_by in filtered_data.columns:
                fig = px.line(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_by,
                    title=plot_title,
                    height=plot_height
                )
            else:
                fig = px.line(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis,
                    title=plot_title,
                    height=plot_height
                )
                
        elif plot_type == "Bar Chart":
            if color_by != "None" and color_by in filtered_data.columns:
                fig = px.bar(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_by,
                    title=plot_title,
                    height=plot_height
                )
            else:
                fig = px.bar(
                    filtered_data, 
                    x=x_axis, 
                    y=y_axis,
                    title=plot_title,
                    height=plot_height
                )
                
        elif plot_type == "Histogram":
            fig = px.histogram(
                filtered_data, 
                x=x_axis,
                title=plot_title,
                height=plot_height
            )
            
        elif plot_type == "Box Plot":
            if color_by != "None" and color_by in filtered_data.columns:
                fig = px.box(
                    filtered_data, 
                    x=color_by, 
                    y=y_axis,
                    title=plot_title,
                    height=plot_height
                )
            else:
                fig = px.box(
                    filtered_data, 
                    y=y_axis,
                    title=plot_title,
                    height=plot_height
                )
        
        # Update layout
        if fig:
            fig.update_layout(
                showlegend=True,
                xaxis_showgrid=show_grid,
                yaxis_showgrid=show_grid
            )
            
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating plot: {str(e)}")
        st.info("Please check your parameter selections and try again.")

with col2:
    st.subheader("Data Summary")
    
    # Display data summary
    st.write(f"**Dataset:** {dataset_option}")
    st.write(f"**Rows:** {len(filtered_data):,}")
    st.write(f"**Columns:** {len(filtered_data.columns)}")
    
    # Show basic statistics for numeric columns
    numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.write("**Numeric Summary:**")
        summary_stats = filtered_data[numeric_cols].describe()
        st.dataframe(summary_stats, use_container_width=True)

# Data preview section
st.markdown("---")
st.subheader("Data Preview")

# Show/hide data preview
show_data = st.checkbox("Show raw data", value=False)

if show_data:
    # Add search functionality
    search_term = st.text_input("Search in data:", "")
    
    display_data = filtered_data
    if search_term:
        # Search across all string columns
        string_cols = filtered_data.select_dtypes(include=['object']).columns
        mask = pd.Series([False] * len(filtered_data))
        for col in string_cols:
            mask |= filtered_data[col].astype(str).str.contains(search_term, case=False, na=False)
        display_data = filtered_data[mask]
    
    # Pagination
    rows_per_page = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)
    
    if len(display_data) > 0:
        total_pages = (len(display_data) - 1) // rows_per_page + 1
        page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        st.dataframe(
            display_data.iloc[start_idx:end_idx], 
            use_container_width=True,
            hide_index=True
        )
        
        st.write(f"Showing {start_idx + 1}-{min(end_idx, len(display_data))} of {len(display_data)} rows")
    else:
        st.info("No data matches your search criteria.")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and Plotly*")

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.session_state.data = generate_sample_data()
    st.rerun()
