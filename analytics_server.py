import os
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv  # Import dotenv
from datetime import datetime, timedelta
from flask_cors import CORS
import openai
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS with explicit configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection using environment variables
DBNAME = os.getenv('dbname')  # Updated variable name
POSTGRES_USER = os.getenv('postgres_user')  # Updated variable name
POSTGRES_PASSWORD = os.getenv('postgres_password')  # Updated variable name
POSTGRES_HOST = os.getenv('postgres_host')  # Updated variable name
OPENAI_API_KEY = os.getenv('openai_api_key')  # Updated variable name

# Construct the database URI
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DBNAME}'
engine = create_engine(DATABASE_URI)

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY


@app.route('/api/analytics', methods=['POST'])
def analytics():
    data = request.json
    print('Data received at /api/analytics:', data)

    price_trends = data.get('priceTrends')
    volatility = data.get('volatility')
    support = data.get('support')
    resistance = data.get('resistance')

    prompt = f"""
    Given the following data:
    Price Trends: {price_trends}
    Volatility: {volatility}
    Support Level: {support}
    Resistance Level: {resistance}
    
    Provide an analytical insight that can help investors make informed decisions. Provide advise if this is risky, moderately risky or safe.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    insights = response['choices'][0]['message']['content']
    return jsonify({'insights': insights})

@app.route('/api/price_trends', methods=['GET'])
def price_trends():
    try:
        coin_id = request.args.get('coin_id')
        df = pd.read_sql(f"SELECT * FROM crypto_data WHERE coin_id = '{coin_id}'", engine)

        if df.empty:
            return jsonify({'error': f'No data found for coin_id: {coin_id}'}), 404

        # Calculate the moving average
        df['moving_average'] = df['close'].rolling(window=30).mean()

        # Explicitly replace NaN and Inf values
        df['moving_average'] = df['moving_average'].replace([np.nan, np.inf, -np.inf], None)

        # Convert DataFrame to JSON
        return jsonify(df[['timestamp', 'close', 'moving_average']].to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/volatility', methods=['GET'])
def volatility():
    coin_id = request.args.get('coin_id')
    df = pd.read_sql(f"SELECT * FROM crypto_data WHERE coin_id = '{coin_id}'", engine)
    volatility = np.std(df['close'])
    return jsonify({'volatility': volatility})

@app.route('/api/performance_comparison', methods=['GET'])
def performance_comparison():
    coin_ids = request.args.getlist('coin_ids')  # Expecting a list of coin IDs
    results = {}
    for coin_id in coin_ids:
        df = pd.read_sql(f"SELECT * FROM crypto_data WHERE coin_id = '{coin_id}'", engine)
        returns = df['close'].pct_change().sum()  # Total returns
        results[coin_id] = returns
    return jsonify(results)

## Support and Resistance data for an entire year
@app.route('/api/support_resistance', methods=['GET'])
def support_resistance():
    coin_id = request.args.get('coin_id')
    df = pd.read_sql(f"SELECT * FROM crypto_data WHERE coin_id = '{coin_id}'", engine)
    support = df['low'].min()
    resistance = df['high'].max()
    return jsonify({'support': support, 'resistance': resistance})

## Support and Resistance data for a specific timeframe
@app.route('/api/support_resistance_by_timeframe', methods=['GET'])
def support_resistance_by_timeframe():
    coin_id = request.args.get('coin_id')
    timeframe = request.args.get('timeframe')  # Accepts 'day', 'week', or 'month'
    
    if timeframe not in ['day', 'week', 'month']:
        return jsonify({'error': 'Invalid timeframe. Use "day", "week", or "month".'}), 400

    # Calculate the start date based on the timeframe
    if timeframe == 'day':
        start_date = datetime.now() - timedelta(days=1)
    elif timeframe == 'week':
        start_date = datetime.now() - timedelta(weeks=1)
    elif timeframe == 'month':
        start_date = datetime.now() - timedelta(days=30)

    # Query the database for the specified timeframe
    df = pd.read_sql(f"""
        SELECT * FROM crypto_data 
        WHERE coin_id = '{coin_id}' 
        AND timestamp >= '{start_date.strftime('%Y-%m-%d')}'
    """, engine)

    if df.empty:
        return jsonify({'error': 'No data available for the specified timeframe.'}), 404

    support = df['low'].min()
    resistance = df['high'].max()
    return jsonify({'support': support, 'resistance': resistance})


@app.route('/api/forecast', methods=['GET'])
def forecast():
    # Placeholder for forecasting logic
    return jsonify({'message': 'Forecasting endpoint not implemented yet.'})

if __name__ == '__main__':
    app.run(debug=True)