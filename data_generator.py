import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """
    Generate sample datasets for the dashboard demonstration.
    Returns a dictionary with different datasets.
    """
    
    # Set random seed for reproducible results
    np.random.seed(42)
    random.seed(42)
    
    datasets = {}
    
    # 1. Sales Data
    sales_data = []
    regions = ['North', 'South', 'East', 'West', 'Central']
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    
    for i in range(200):
        sales_data.append({
            'date': datetime.now() - timedelta(days=random.randint(0, 365)),
            'region': random.choice(regions),
            'product': random.choice(products),
            'sales_amount': np.random.normal(1000, 300),
            'units_sold': np.random.poisson(50),
            'profit_margin': np.random.uniform(0.1, 0.4)
        })
    
    datasets['sales_data'] = pd.DataFrame(sales_data)
    datasets['sales_data']['sales_amount'] = np.abs(datasets['sales_data']['sales_amount'])
    
    # 2. Stock Prices Data
    stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    stock_data = []
    
    base_date = datetime.now() - timedelta(days=365)
    
    for symbol in stock_symbols:
        base_price = np.random.uniform(100, 500)
        
        for i in range(252):  # Trading days in a year
            current_date = base_date + timedelta(days=i)
            
            # Simulate price movement
            daily_return = np.random.normal(0.001, 0.02)
            price = base_price * (1 + daily_return)
            base_price = price
            
            stock_data.append({
                'date': current_date,
                'symbol': symbol,
                'price': price,
                'volume': np.random.randint(1000000, 10000000),
                'market_cap': price * np.random.randint(1000000, 5000000)
            })
    
    datasets['stock_prices'] = pd.DataFrame(stock_data)
    
    # 3. Weather Data
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    weather_data = []
    
    for city in cities:
        base_temp = np.random.uniform(10, 25)  # Base temperature
        
        for i in range(365):
            current_date = datetime.now() - timedelta(days=i)
            
            # Seasonal variation
            day_of_year = current_date.timetuple().tm_yday
            seasonal_temp = base_temp + 15 * np.sin(2 * np.pi * day_of_year / 365)
            
            weather_data.append({
                'date': current_date,
                'city': city,
                'temperature': seasonal_temp + np.random.normal(0, 5),
                'humidity': np.random.uniform(30, 90),
                'precipitation': np.random.exponential(2),
                'wind_speed': np.random.gamma(2, 2)
            })
    
    datasets['weather_data'] = pd.DataFrame(weather_data)
    
    # Clean up negative values and format dates
    for dataset_name, dataset in datasets.items():
        if 'date' in dataset.columns:
            dataset['date'] = pd.to_datetime(dataset['date']).dt.date
        
        # Ensure no negative values in certain columns
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ['price', 'sales_amount', 'volume', 'market_cap', 'precipitation', 'wind_speed']:
                dataset[col] = np.abs(dataset[col])
    
    return datasets

def get_column_info(dataset):
    """
    Get information about columns in a dataset for better UI generation.
    """
    info = {}
    for col in dataset.columns:
        dtype = str(dataset[col].dtype)
        unique_values = dataset[col].nunique()
        
        info[col] = {
            'dtype': dtype,
            'unique_values': unique_values,
            'is_categorical': unique_values < 20 and dtype == 'object',
            'is_numeric': dtype in ['int64', 'float64'],
            'is_datetime': 'date' in col.lower() or dtype == 'datetime64[ns]'
        }
    
    return info
