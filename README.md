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

### Quick Deploy Steps:
1. Fork or clone this repository
2. Connect your GitHub repository to Streamlit Community Cloud
3. Set the main file path to `app.py`
4. Deploy

### Troubleshooting Common Issues:

**Error: "dial tcp 127.0.0.1:8501: connect: connection refused"**

This error occurs when the platform detects multiple dependency files. To fix:

1. In your Streamlit Community Cloud dashboard, go to "Advanced settings"
2. Set Python version to 3.9 or 3.10
3. If the error persists, temporarily rename `uv.lock` to `uv.lock.bak` in your repository
4. Create a simple `requirements.txt` file with:
   ```
   streamlit
   pandas
   plotly
   numpy
   ```
5. Commit and push the changes
6. Redeploy the app

The platform will automatically detect and use the standard requirements.txt format.

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