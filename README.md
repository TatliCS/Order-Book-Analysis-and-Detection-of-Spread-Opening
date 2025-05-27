Order Book Analysis and Detection of Spread Opening

You are about to develop a financial analytics platform and need to analyze real-time order book data. Your task is to use the Binance API to pull order book data for the BTC/USDT spot price, listen to it for a short period of time, and perform analysis based on it.

Pulling Order Book Data:
- Get order book data for the spot price of the BTC/USDT pair using the Binance API.
- For a short period of time (for example, 10 minutes), listen to the data in real-time.
- Choose how you want to pull and process the order book data.

Spread Analysis:
- Analyze the spread (ask price - bid price) in the data over time.
- Develop an algorithm that detects spread widening. For example:
    - Alert when the spread goes above a certain threshold.
    - Calculate the time it takes for the spread to return to normal levels.

Visualization
- Visualize the changes in order book data over time with a chart.
- Mark spread openings on the chart.

Reporting:
- Present your analysis and observations in a short report.
- Discuss the possible effects of spread widening on the market.

(Optional) Additional Analysis:
- Try to detect a fake wall. For example:
    - An abnormally high volume bid or a sudden
disappearance of the ask level.
    - Develop an algorithm that detects such events and analyze the results.

Delivery Expectations:
- Python code: Pulling order book data with Binance API, analyzing and visualizing.
- Visualization charts: charts showing spread opening and order book changes.
- Report: A short report with the results of your analysis and observations.