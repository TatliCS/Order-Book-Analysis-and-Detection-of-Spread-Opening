Order Book Analysis and Detection of Spread Opening
*A 10-minute real-time study of **BTC / USDT** on Binance*

## 1. Why I built it

As part of the technical assignment for **TRK-Technology**, I was asked to design an analytics pipeline that;

* Streams the BTC/USDT spot order book in real-time,  
* Detects meaningful “spread-opening” events,  
* Visualises and reports the results, and  
* (optionally) Flags suspicious fake-wall liquidity.

## 2. Quick-start

```bash
git clone https://github.com/TatliCS/Order-Book-Analysis-and-Detection-of-Spread-Opening.git
cd Order-Book-Analysis-and-Detection-of-Spread-Opening
BINANCE_API_KEY=XXX
BINANCE_API_SECRET=YYY

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python order_book_analysis.py          #~10 min capture