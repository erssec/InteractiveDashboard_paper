# Compound Analysis Dashboard

An interactive scientific data visualization dashboard built with Streamlit for exploring experimental compound data.

## Features

- Interactive compound selection with Levosimendan as default
- Multi-screen data visualization with synchronized legends
- Real-time filtering by read-out type, compounds, and measurements
- Memory-optimized for Streamlit Community Cloud deployment

## Requirements

The application uses minimal dependencies optimized for cloud deployment:

- streamlit>=1.28.0,<2.0.0
- pandas>=1.5.0,<3.0.0
- plotly>=5.15.0,<6.0.0
- numpy>=1.21.0,<2.0.0

## Deployment to Streamlit Community Cloud

1. Fork or clone this repository
2. Connect your GitHub repository to Streamlit Community Cloud
3. Set the main file path to `app.py`
4. Deploy directly - no additional configuration needed

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Data Structure

The dashboard expects CSV data with the following columns:
- screen: Screen identifier
- read-out: Type of measurement (calcium/voltage)
- compound: Compound name
- concentration: Concentration value
- measurement_name: Type of measurement
- SEM: Standard error of mean
- STDEV: Standard deviation
- average: Average value

## Memory Optimizations

- Cached data loading and filtering functions
- Optimized data types (category for strings, downcast for numerics)
- Efficient legend management for multi-screen displays
- Minimal dependency versions for reduced memory footprint