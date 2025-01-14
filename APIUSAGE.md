# API Documentation

## Overview
This document provides details about the available endpoints in the analytics server, their usage, query parameters, and example requests and responses.

---

## **1. `/api/price_trends`**
### Description
Fetch historical price trends for a specific coin within a defined timeframe.

### URL
```
GET /api/price_trends
```

### Query Parameters
| Parameter  | Type    | Description                                            |
|------------|---------|--------------------------------------------------------|
| `coin_id`  | string  | The coin ID (e.g., `BTC`, `ETH`, `SOL`).               |
| `timeframe`| string  | The timeframe (`hour`, `4hours`, `day`, `week`, `month`). |
| `predict`  | boolean | Optional. Set to `true` to include LSTM-based price predictions. Default is `false`. |

### Example Request
```
GET http://localhost:5000/api/price_trends?coin_id=BTC&timeframe=day&predict=false
```

### Example Response
```json
{
  "historical_data": [
    {
      "timestamp": "2025-01-14 00:00:00",
      "close": 42123.45,
      "moving_average": 42056.78
    },
    {
      "timestamp": "2025-01-14 01:00:00",
      "close": 42234.67,
      "moving_average": 42112.34
    }
  ],
  "predictions": null
}
```

---

## **2. `/api/volatility`**
### Description
Calculate the volatility of a specific coin's price within a defined timeframe.

### URL
```
GET /api/volatility
```

### Query Parameters
| Parameter  | Type    | Description                                            |
|------------|---------|--------------------------------------------------------|
| `coin_id`  | string  | The coin ID (e.g., `BTC`, `ETH`, `SOL`).               |
| `timeframe`| string  | The timeframe (`hour`, `4hours`, `day`, `week`, `month`). |

### Example Request
```
GET http://localhost:5000/api/volatility?coin_id=BTC&timeframe=week
```

### Example Response
```json
{
  "volatility": 234.56
}
```

---

## **3. `/api/support_resistance`**
### Description
Retrieve the support and resistance levels for a specific coin within a defined timeframe.

### URL
```
GET /api/support_resistance
```

### Query Parameters
| Parameter  | Type    | Description                                            |
|------------|---------|--------------------------------------------------------|
| `coin_id`  | string  | The coin ID (e.g., `BTC`, `ETH`, `SOL`).               |
| `timeframe`| string  | The timeframe (`hour`, `4hours`, `day`, `week`, `month`). |

### Example Request
```
GET http://localhost:5000/api/support_resistance?coin_id=BTC&timeframe=4hours
```

### Example Response
```json
{
  "support": 40000.00,
  "resistance": 43000.00
}
```

---

## **4. `/api/analytics`**
### Description
Send aggregated data (price trends, volatility, support, and resistance levels) to receive actionable insights.

### URL
```
POST /api/analytics
```

### Request Body
| Parameter      | Type    | Description                                           |
|----------------|---------|-------------------------------------------------------|
| `priceTrends`  | array   | Historical price trends.                              |
| `volatility`   | number  | Calculated volatility.                                |
| `support`      | number  | Support level.                                        |
| `resistance`   | number  | Resistance level.                                     |

### Example Request
```
POST http://localhost:5000/api/analytics
Content-Type: application/json
```

#### Request Body
```json
{
  "priceTrends": [
    {"timestamp": "2025-01-14 00:00:00", "close": 42123.45, "moving_average": 42056.78},
    {"timestamp": "2025-01-14 01:00:00", "close": 42234.67, "moving_average": 42112.34}
  ],
  "volatility": 234.56,
  "support": 40000.00,
  "resistance": 43000.00
}
```

### Example Response
```json
{
  "insights": "Based on the provided data, the market seems moderately risky due to high volatility. Consider setting stop-loss levels near the support price of $40000."
}
```

---

## Testing in Postman
1. **Set Base URL**:  
   ```
   http://localhost:5000
   ```

2. **Endpoints**:  
   Use the examples provided above to test each endpoint.

3. **Headers**:  
   For `/api/analytics`, ensure the following header is set:  
   ```
   Content-Type: application/json
   ```

4. **Verify Responses**:  
   Ensure you receive the expected JSON responses.

---

