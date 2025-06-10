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

# Add memory optimization
@st.cache_data
def get_filtered_data(readout, compounds, measurements):
    """Cache filtered data to improve performance."""
    readout_data = data[data['read-out'] == readout]
    compound_data = readout_data[readout_data['compound'].isin(compounds)]
    filtered_data = compound_data[compound_data['measurement_name'].isin(measurements)]
    return filtered_data

@st.cache_data
def load_data():
    """Load and prepare the experimental data."""
    df = pd.read_csv('data/pivot_table_of_results.csv')
    # Drop the unnamed index column
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    # Optimize data types to reduce memory usage
    for col in ['SEM', 'STDEV', 'average', 'concentration']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
    
    for col in ['screen']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # Convert string columns to category to save memory
    for col in ['read-out', 'compound', 'measurement_name']:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df

# Load data
data = load_data()

# Main title
st.title("Compound Analysis Dashboard")
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
    default=["Levosimendan"] if "Levosimendan" in compound_options else compound_options[:1],
    help="Select one or more compounds to analyze"
)

if not selected_compounds:
    st.warning("Please select at least one compound to display data.")
    st.stop()

# Filter data by compounds
compound_data = readout_data[readout_data['compound'].isin(selected_compounds)]

# 3. Measurement selection
st.sidebar.subheader("Measurements")

# Define measurement filters based on read-out type
calcium_measurements = {'Rising Slope', 'Falling Slope', 'Pulse Width 50%', 'Area Under the Curve'}
voltage_measurements = {'Pulse Width 10%', 'Pulse Width 50%', 'Pulse Width 90%', 'Rising Slope', 'Falling Slope', 'Triangulation', 'Amplitude'}

# Get available measurements for the current read-out type
all_measurement_options = set(compound_data['measurement_name'].unique())

if selected_readout == 'calcium':
    allowed_measurements = calcium_measurements
elif selected_readout == 'voltage':
    allowed_measurements = voltage_measurements
else:
    allowed_measurements = all_measurement_options

# Filter to only show measurements that exist in data AND are allowed for this read-out
measurement_options = sorted(all_measurement_options.intersection(allowed_measurements))

selected_measurements = []
for measurement in measurement_options:
    if st.sidebar.checkbox(measurement, value=(measurement in measurement_options[:3])):
        selected_measurements.append(measurement)

if not selected_measurements:
    st.warning("Please select at least one measurement to display.")
    st.stop()

# Use cached filtering function
filtered_data = get_filtered_data(selected_readout, selected_compounds, selected_measurements)

# Get unique screens for this read-out and compound combination
available_screens = sorted(filtered_data['screen'].unique())

# Add pooled screening option
st.sidebar.subheader("Screening Display")
pool_screens = st.sidebar.checkbox("Pool all screenings", value=False, help="Combine data from all screens and show individual points with mean lines")

# Get all unique concentrations across the filtered data and sort them
all_concentrations = sorted(filtered_data['concentration'].unique())
concentration_labels = [str(c) for c in all_concentrations]

# Create color mapping for compounds (each compound gets its own color)
colors = px.colors.qualitative.Set1[:len(selected_compounds)]
compound_colors = dict(zip(selected_compounds, colors))

if pool_screens:
    # Pooled screening mode: combine all screens, show individual points and means
    num_measurements = len(selected_measurements)
    
    # Create subplots: one column, rows for measurements
    fig = make_subplots(
        rows=num_measurements,
        cols=1,
        vertical_spacing=0.08,
        shared_xaxes=True,
        shared_yaxes=False
    )
    
    # Track which compounds have been added to legend
    legend_compounds = set()
    
    for measurement_idx, measurement in enumerate(selected_measurements):
        measurement_data = filtered_data[filtered_data['measurement_name'] == measurement]
        
        for compound in selected_compounds:
            compound_measurement_data = measurement_data[measurement_data['compound'] == compound]
            
            if not compound_measurement_data.empty:
                # Show legend only for the first occurrence of each compound
                show_in_legend = compound not in legend_compounds
                if show_in_legend:
                    legend_compounds.add(compound)
                
                # Plot individual data points from all screens
                for concentration in all_concentrations:
                    conc_data = compound_measurement_data[compound_measurement_data['concentration'] == concentration]
                    if not conc_data.empty:
                        x_pos = all_concentrations.index(concentration)
                        
                        # Add individual points (scatter)
                        fig.add_trace(
                            go.Scatter(
                                x=[x_pos] * len(conc_data),
                                y=conc_data['average'],
                                mode='markers',
                                name=compound if show_in_legend else None,
                                marker=dict(
                                    color=compound_colors[compound],
                                    size=4,
                                    opacity=0.6
                                ),
                                legendgroup=compound,
                                showlegend=show_in_legend,
                                hovertemplate=f'<b>{compound}</b><br>' +
                                            f'Concentration: {concentration}<br>' +
                                            '% Change: %{y:.2f}<br>' +
                                            '<extra></extra>'
                            ),
                            row=measurement_idx + 1,
                            col=1
                        )
                        
                        # Add mean line
                        mean_value = conc_data['average'].mean()
                        fig.add_trace(
                            go.Scatter(
                                x=[x_pos - 0.2, x_pos + 0.2],
                                y=[mean_value, mean_value],
                                mode='lines',
                                line=dict(
                                    color=compound_colors[compound],
                                    width=3
                                ),
                                showlegend=False,
                                hovertemplate=f'<b>{compound} Mean</b><br>' +
                                            f'Concentration: {concentration}<br>' +
                                            f'Mean % Change: {mean_value:.2f}<br>' +
                                            '<extra></extra>'
                            ),
                            row=measurement_idx + 1,
                            col=1
                        )
                        
                        show_in_legend = False  # Only show legend for first trace
    
    # Calculate appropriate height
    plot_height = max(400, 250 * num_measurements)
    
    # Update layout
    fig.update_layout(
        height=plot_height,
        title_text=f"{selected_readout.title()} Read-out Analysis (Pooled Screens)",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # Update axes
    for measurement_idx, measurement in enumerate(selected_measurements):
        fig.update_yaxes(
            title_text=f"{measurement}<br>% Change",
            row=measurement_idx + 1,
            col=1
        )
    
    # Update x-axis for all rows
    for measurement_idx in range(num_measurements):
        fig.update_xaxes(
            title_text="Concentration",
            tickmode='array',
            tickvals=list(range(len(all_concentrations))),
            ticktext=concentration_labels,
            row=measurement_idx + 1,
            col=1
        )

else:
    # Original mode: separate plots for each measurement, separate columns for screens
    num_measurements = len(selected_measurements)
    num_screens = len(available_screens)
    
    # Create subplots: rows for measurements, columns for screens
    fig = make_subplots(
        rows=num_measurements,
        cols=num_screens,
        subplot_titles=[f"Screen {screen}" for screen in available_screens] if num_screens > 1 else None,
        vertical_spacing=0.08,
        horizontal_spacing=0.05,
        shared_xaxes=True,
        shared_yaxes=False
    )
    
    # Track which compounds have been added to legend (only show once)
    legend_compounds = set()
    
    for measurement_idx, measurement in enumerate(selected_measurements):
        for screen_idx, screen in enumerate(available_screens):
            screen_data = filtered_data[filtered_data['screen'] == screen]
            measurement_data = screen_data[screen_data['measurement_name'] == measurement]
            
            for compound in selected_compounds:
                compound_measurement_data = measurement_data[measurement_data['compound'] == compound]
                
                if not compound_measurement_data.empty:
                    # Sort by concentration for proper line plotting
                    compound_measurement_data = compound_measurement_data.sort_values('concentration')
                    
                    # Map concentrations to x-axis positions
                    concentrations = compound_measurement_data['concentration'].values
                    x_positions = [all_concentrations.index(c) for c in concentrations]
                    conc_labels = [str(c) for c in concentrations]
                    
                    # Show legend only for the first occurrence of each compound
                    show_in_legend = compound not in legend_compounds
                    if show_in_legend:
                        legend_compounds.add(compound)
                    
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
                            name=compound,
                            line=dict(
                                color=compound_colors[compound],
                                width=2
                            ),
                            marker=dict(
                                size=6
                            ),
                            legendgroup=compound,
                            showlegend=show_in_legend,
                            customdata=conc_labels,
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                        'Concentration: %{customdata}<br>' +
                                        '% Change: %{y:.2f}<br>' +
                                        'SEM: %{error_y.array:.2f}<br>' +
                                        '<extra></extra>'
                        ),
                        row=measurement_idx + 1,
                        col=screen_idx + 1
                    )
    
    # Calculate appropriate height based on number of measurements
    plot_height = max(400, 250 * num_measurements)
    
    # Update layout
    fig.update_layout(
        height=plot_height,
        title_text=f"{selected_readout.title()} Read-out Analysis",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # Add measurement labels on the left side and update axes
    for measurement_idx, measurement in enumerate(selected_measurements):
        # Add measurement label as y-axis title for the leftmost subplot
        fig.update_yaxes(
            title_text=f"{measurement}<br>% Change",
            row=measurement_idx + 1,
            col=1
        )
        
        # Update other y-axes in the same row (if multiple screens)
        for screen_idx in range(1, num_screens):
            fig.update_yaxes(
                title_text="% Change",
                row=measurement_idx + 1,
                col=screen_idx + 1
            )
    
    # Update x-axes for all rows
    for measurement_idx in range(num_measurements):
        for screen_idx in range(num_screens):
            fig.update_xaxes(
                title_text="Concentration",
                tickmode='array',
                tickvals=list(range(len(all_concentrations))),
                ticktext=concentration_labels,
                row=measurement_idx + 1,
                col=screen_idx + 1
            )

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# Display compound color guide
if len(selected_compounds) > 1:
    st.markdown("---")
    st.subheader("Compound Colors")
    
    cols = st.columns(min(len(selected_compounds), 4))
    for i, compound in enumerate(selected_compounds):
        with cols[i % 4]:
            color = compound_colors[compound]
            st.markdown(f"<span style='color: {color}; font-weight: bold; font-size: 16px;'>●</span> {compound}", unsafe_allow_html=True)

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
st.markdown("*Compound Analysis Dashboard - Built by Ehsan Razaghi with Streamlit, Plotly, and Replit*")