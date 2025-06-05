import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

# Configure the page
st.set_page_config(
    page_title="Compound Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and prepare the experimental data."""
    df = pd.read_csv('data/pivot_table_of_results.csv')
    # Drop the unnamed index column
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    return df

# Load data
data = load_data()

# Header with title and theme toggle
col1, col2 = st.columns([4, 1])

with col1:
    st.title("Compound Analysis Dashboard")

with col2:
    # Theme toggle switch
    st.write("")  # Add some spacing
    dark_mode = st.toggle("Dark Mode", value=False, key="theme_toggle")

# Apply custom CSS based on theme selection
if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stSelectbox > div > div {
        background-color: #262730;
        color: #fafafa;
    }
    .stMultiSelect > div > div {
        background-color: #262730;
        color: #fafafa;
    }
    .stCheckbox > label {
        color: #fafafa;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #fafafa;
    }
    .stSlider > div > div > div {
        color: #fafafa;
    }
    .stDataFrame {
        background-color: #262730;
    }
    div[data-testid="stSidebar"] {
        background-color: #262730;
    }
    div[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #0e1117;
    }
    div[data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: #0e1117;
    }
    div[data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #262730;
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
        color: #262730;
    }
    .stMultiSelect > div > div {
        background-color: #ffffff;
        color: #262730;
    }
    .stCheckbox > label {
        color: #262730;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #262730;
    }
    .stSlider > div > div > div {
        color: #262730;
    }
    .stDataFrame {
        background-color: #ffffff;
    }
    div[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
st.sidebar.header("Analysis Parameters")

# 1. Read-out selection
readout_options = sorted(data['read-out'].unique())
selected_readout = st.sidebar.selectbox(
    "Read-out Type:",
    readout_options,
    help="Select calcium or voltage read-out"
)

# Filter data by read-out
readout_data = data[data['read-out'] == selected_readout]

# 2. Compound selection
compound_options = sorted(readout_data['compound'].unique())
st.sidebar.subheader("Compound Selection")

selected_compounds = st.sidebar.multiselect(
    "Select Compounds:",
    compound_options,
    default=compound_options[:3] if len(compound_options) >= 3 else compound_options,
    help="Select one or more compounds to analyze"
)

if not selected_compounds:
    st.warning("Please select at least one compound to display data.")
    st.stop()

# Filter data by compounds
compound_data = readout_data[readout_data['compound'].isin(selected_compounds)]

# 3. Measurement selection
st.sidebar.subheader("Measurements")
measurement_options = sorted(compound_data['measurement_name'].unique())

selected_measurements = []
for measurement in measurement_options:
    if st.sidebar.checkbox(measurement, value=(measurement in measurement_options[:3])):
        selected_measurements.append(measurement)

if not selected_measurements:
    st.warning("Please select at least one measurement to display.")
    st.stop()

# Filter data by measurements
filtered_data = compound_data[compound_data['measurement_name'].isin(selected_measurements)]

# Get unique screens for this read-out and compound combination
available_screens = sorted(filtered_data['screen'].unique())

# Get all unique concentrations across the filtered data and sort them
all_concentrations = sorted(filtered_data['concentration'].unique())
concentration_labels = [str(c) for c in all_concentrations]

# Create color mapping for measurements
colors = px.colors.qualitative.Set1[:len(selected_measurements)]
measurement_colors = dict(zip(selected_measurements, colors))

# Main content area
if len(available_screens) > 1:
    # Multiple screens - create subplots
    fig = make_subplots(
        rows=1, 
        cols=len(available_screens),
        subplot_titles=[f"Screen {screen}" for screen in available_screens],
        shared_yaxes=False
    )
    
    for col_idx, screen in enumerate(available_screens):
        screen_data = filtered_data[filtered_data['screen'] == screen]
        
        for measurement in selected_measurements:
            measurement_data = screen_data[screen_data['measurement_name'] == measurement]
            
            for compound in selected_compounds:
                compound_measurement_data = measurement_data[measurement_data['compound'] == compound]
                
                if not compound_measurement_data.empty:
                    # Sort by concentration for proper line plotting
                    compound_measurement_data = compound_measurement_data.sort_values('concentration')
                    
                    # Create trace name
                    trace_name = f"{compound} - {measurement}"
                    
                    # Map concentrations to x-axis positions
                    concentrations = compound_measurement_data['concentration'].values
                    x_positions = [all_concentrations.index(c) for c in concentrations]
                    conc_labels = [str(c) for c in concentrations]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_positions,
                            y=compound_measurement_data['average'],
                            error_y=dict(
                                type='data',
                                array=compound_measurement_data['SEM'],
                                visible=True
                            ),
                            mode='lines+markers',
                            name=trace_name,
                            line=dict(color=measurement_colors[measurement]),
                            legendgroup=measurement,
                            showlegend=(col_idx == 0),  # Only show legend for first subplot
                            customdata=conc_labels,
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                        'Concentration: %{customdata}<br>' +
                                        '% Change: %{y:.2f}<br>' +
                                        'SEM: %{error_y.array:.2f}<br>' +
                                        '<extra></extra>'
                        ),
                        row=1, 
                        col=col_idx + 1
                    )
    
    # Update layout with theme colors
    plot_bgcolor = '#0e1117' if dark_mode else '#ffffff'
    paper_bgcolor = '#0e1117' if dark_mode else '#ffffff'
    font_color = '#fafafa' if dark_mode else '#262730'
    
    fig.update_layout(
        height=600,
        title_text=f"{selected_readout.title()} Read-out Analysis",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        font=dict(color=font_color)
    )
    
    # Update x and y axis labels
    for i in range(1, len(available_screens) + 1):
        fig.update_xaxes(
            title_text="Concentration", 
            tickmode='array',
            tickvals=list(range(len(all_concentrations))),
            ticktext=concentration_labels,
            row=1, 
            col=i
        )
        fig.update_yaxes(title_text="% Change", row=1, col=i)

else:
    # Single screen - create regular plot
    screen = available_screens[0]
    screen_data = filtered_data[filtered_data['screen'] == screen]
    
    fig = go.Figure()
    
    for measurement in selected_measurements:
        measurement_data = screen_data[screen_data['measurement_name'] == measurement]
        
        for compound in selected_compounds:
            compound_measurement_data = measurement_data[measurement_data['compound'] == compound]
            
            if not compound_measurement_data.empty:
                # Sort by concentration for proper line plotting
                compound_measurement_data = compound_measurement_data.sort_values('concentration')
                
                # Create trace name
                trace_name = f"{compound} - {measurement}"
                
                fig.add_trace(
                    go.Scatter(
                        x=compound_measurement_data['concentration'].astype(str),
                        y=compound_measurement_data['average'],
                        error_y=dict(
                            type='data',
                            array=compound_measurement_data['SEM'],
                            visible=True
                        ),
                        mode='lines+markers',
                        name=trace_name,
                        line=dict(color=measurement_colors[measurement])
                    )
                )
    
    # Update layout with theme colors
    plot_bgcolor = '#0e1117' if dark_mode else '#ffffff'
    paper_bgcolor = '#0e1117' if dark_mode else '#ffffff'
    font_color = '#fafafa' if dark_mode else '#262730'
    
    fig.update_layout(
        height=600,
        title=f"{selected_readout.title()} Read-out Analysis - Screen {screen}",
        xaxis=dict(
            title="Concentration",
            tickmode='array',
            tickvals=list(range(len(all_concentrations))),
            ticktext=concentration_labels
        ),
        yaxis_title="% Change",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        font=dict(color=font_color)
    )

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# Summary information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Selection Summary")
    st.write(f"**Read-out:** {selected_readout}")
    st.write(f"**Compounds:** {len(selected_compounds)}")
    st.write(f"**Measurements:** {len(selected_measurements)}")
    st.write(f"**Screens:** {len(available_screens)}")

with col2:
    st.subheader("Data Points")
    st.write(f"**Total rows:** {len(filtered_data):,}")
    concentration_range = filtered_data['concentration'].agg(['min', 'max'])
    st.write(f"**Concentration range:** {concentration_range['min']:.3f} - {concentration_range['max']:.1f}")

with col3:
    st.subheader("Selected Compounds")
    for compound in selected_compounds:
        compound_rows = len(filtered_data[filtered_data['compound'] == compound])
        st.write(f"**{compound}:** {compound_rows} data points")

# Data preview section
st.markdown("---")
st.subheader("Data Preview")

show_data = st.checkbox("Show filtered data", value=False)

if show_data:
    # Display options
    col1, col2 = st.columns(2)
    with col1:
        rows_per_page = st.selectbox("Rows per page:", [25, 50, 100, 200], index=1)
    with col2:
        sort_by = st.selectbox(
            "Sort by:", 
            ['compound', 'concentration', 'measurement_name', 'average', 'screen'],
            index=1
        )
    
    # Sort and paginate data
    display_data = filtered_data.sort_values(sort_by)
    
    if len(display_data) > 0:
        total_pages = (len(display_data) - 1) // rows_per_page + 1
        page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        # Format the data for display
        display_columns = ['screen', 'compound', 'concentration', 'measurement_name', 'average', 'SEM', 'STDEV']
        page_data = display_data[display_columns].iloc[start_idx:end_idx].copy()
        
        # Round numerical columns for better display
        for col in ['concentration', 'average', 'SEM', 'STDEV']:
            if col in page_data.columns:
                page_data[col] = page_data[col].round(3)
        
        st.dataframe(
            page_data, 
            use_container_width=True,
            hide_index=True
        )
        
        st.write(f"Showing {start_idx + 1}-{min(end_idx, len(display_data))} of {len(display_data)} rows")
    else:
        st.info("No data matches your current selection.")

# Footer
st.markdown("---")
st.markdown("*Compound Analysis Dashboard - Built with Streamlit and Plotly*")