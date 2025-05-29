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
```

## 3. Repo Layout

├─ order_book_analysis.py   ← orchestration / WebSocket loop
├─ utils.py                 ← math helpers & detection logic
├─ visualization.py         ← Styled charts
├─ requirements.txt
├─ .env.example             ← rename & fill with your keys
└─ docs/assets/             ← sample PNGs for this README

## 4. Data Visualization and Report

![spread_analysis](https://github.com/user-attachments/assets/801a3880-5374-4843-86aa-febd954762b5)
![order_book_depth](https://github.com/user-attachments/assets/e09ae82d-d319-4538-81e6-c486ac58ab1a)
![fake_wall_detection](https://github.com/user-attachments/assets/727d7813-4dfa-4b52-ad7e-dabc2e510bff)

*Example analysis_report.txt file:*
Order Book Analysis Report
==================================================

Spread Analysis:
Average Spread:   -56.245 USDT
Maximum Spread:     0.010 USDT
Minimum Spread:  -122.420 USDT
Widening Events: 403

Recovery-time Analysis:
Average recovery: 39.68 s  across 13 events

