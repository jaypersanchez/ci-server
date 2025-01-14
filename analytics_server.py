import os
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv  # Import dotenv
from datetime import datetime, timedelta
from flask_cors import CORS
import openai
from utils import calculate_lstm_predictions  # Import the function
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
    
    Provide an analytical insight that can help investors make informed decisions. Provide advice if this is risky, moderately risky, or safe.
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
        timeframe = request.args.get('timeframe', 'month')  # Default to 'month'
        predict = request.args.get('predict', 'false').lower() == 'true'

        # Validate the timeframe
        if timeframe not in ['hour', '4hours', 'day', 'week', 'month']:
            return jsonify({'error': 'Invalid timeframe. Use "hour", "4hours", "day", "week", or "month".'}), 400

        # Determine the start date based on the timeframe
        now = datetime.now()
        if timeframe == 'hour':
            start_date = now - timedelta(hours=1)
        elif timeframe == '4hours':
            start_date = now - timedelta(hours=4)
        elif timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)

        # Query the database for the specified timeframe
        query = text("""
            SELECT * FROM crypto_data
            WHERE coin_id = :coin_id
            AND timestamp >= :start_date
            ORDER BY timestamp ASC
        """)
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"coin_id": coin_id, "start_date": start_date})

        # Check if data is available
        if df.empty:
            return jsonify({'error': f'No data found for coin_id: {coin_id} and timeframe: {timeframe}'}), 404

        # Add moving average
        df['moving_average'] = df['close'].rolling(window=30).mean()
        df['moving_average'] = df['moving_average'].replace([np.nan, np.inf, -np.inf], None)

        # Response data
        response = {
            'historical_data': df[['timestamp', 'close', 'moving_average']].to_dict(orient='records')
        }

        # Add predictions if requested
        if predict:
            predictions = calculate_lstm_predictions(df['close'])
            response['predictions'] = predictions

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/volatility', methods=['GET'])
def volatility():
    try:
        coin_id = request.args.get('coin_id')
        timeframe = request.args.get('timeframe')  # Accept 'hour', '4hours', 'day', 'week', or 'month'

        if timeframe not in ['hour', '4hours', 'day', 'week', 'month']:
            return jsonify({'error': 'Invalid timeframe. Use "hour", "4hours", "day", "week", or "month".'}), 400

        # Define the start date based on the timeframe
        now = datetime.now()
        if timeframe == 'hour':
            start_date = now - timedelta(hours=1)
        elif timeframe == '4hours':
            start_date = now - timedelta(hours=4)
        elif timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)

        # Query the database for the specified timeframe
        query = text("""
            SELECT * FROM crypto_data
            WHERE coin_id = :coin_id
            AND timestamp >= :start_date
        """)
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"coin_id": coin_id, "start_date": start_date})

        if df.empty:
            return jsonify({'error': f'No data found for coin_id: {coin_id} and timeframe: {timeframe}'}), 404

        # Calculate volatility
        volatility = np.std(df['close'])
        return jsonify({'volatility': volatility})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/support_resistance', methods=['GET'])
def support_resistance():
    try:
        coin_id = request.args.get('coin_id')
        timeframe = request.args.get('timeframe', 'month')  # Default to 'month'

        # Validate the timeframe
        if timeframe not in ['hour', '4hours', 'day', 'week', 'month']:
            return jsonify({'error': 'Invalid timeframe. Use "hour", "4hours", "day", "week", or "month".'}), 400

        # Determine the start date based on the timeframe
        now = datetime.now()
        if timeframe == 'hour':
            start_date = now - timedelta(hours=1)
        elif timeframe == '4hours':
            start_date = now - timedelta(hours=4)
        elif timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)

        # Query the database for the specified timeframe
        query = text("""
            SELECT * FROM crypto_data
            WHERE coin_id = :coin_id
            AND timestamp >= :start_date
        """)
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"coin_id": coin_id, "start_date": start_date})

        # Check if data is available
        if df.empty:
            return jsonify({'error': f'No data found for coin_id: {coin_id} and timeframe: {timeframe}'}), 404

        # Calculate support and resistance
        support = df['low'].min()
        resistance = df['high'].max()

        return jsonify({'support': support, 'resistance': resistance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance_comparison', methods=['GET'])
def performance_comparison():
    try:
        coin_ids = request.args.getlist('coin_ids')  # Collect all coin_ids from query parameters
        timeframe = request.args.get('timeframe', 'month')  # Default to 'month'

        if not coin_ids:
            return jsonify({'error': 'No coin_ids provided. Provide at least one coin_id.'}), 400

        if timeframe not in ['hour', '4hours', 'day', 'week', 'month']:
            return jsonify({'error': 'Invalid timeframe. Use "hour", "4hours", "day", "week", or "month".'}), 400

        # Determine the start date based on the timeframe
        now = datetime.now()
        if timeframe == 'hour':
            start_date = now - timedelta(hours=1)
        elif timeframe == '4hours':
            start_date = now - timedelta(hours=4)
        elif timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)

        results = []
        for coin_id in coin_ids:
            # Fetch data for each coin_id
            query = text("""
                SELECT * FROM crypto_data
                WHERE coin_id = :coin_id
                AND timestamp >= :start_date
                ORDER BY timestamp ASC
            """)
            with engine.connect() as connection:
                df = pd.read_sql(query, connection, params={"coin_id": coin_id, "start_date": start_date})

            if df.empty:
                results.append({
                    'coin_id': coin_id,
                    'error': f'No data found for coin_id: {coin_id} and timeframe: {timeframe}'
                })
                continue

            # Calculate performance (e.g., percentage change over the timeframe)
            initial_price = df['close'].iloc[0]
            final_price = df['close'].iloc[-1]
            performance = ((final_price - initial_price) / initial_price) * 100

            results.append({
                'coin_id': coin_id,
                'initial_price': initial_price,
                'final_price': final_price,
                'performance_percentage': performance
            })

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
