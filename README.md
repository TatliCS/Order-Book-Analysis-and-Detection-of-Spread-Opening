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

```text
├─ order_book_analysis.py   ← orchestration / WebSocket loop
├─ utils.py                 ← math helpers & detection logic
├─ visualization.py         ← Styled charts
├─ requirements.txt
├─ .env.example             ← rename & fill with your keys
└─ docs/assets/             ← sample PNGs for this README
```

## 4. Data Visualization and Report

*spread_analysis.png: BTC/USDT Spread – 10-minute capture*
![spread_analysis](https://github.com/user-attachments/assets/801a3880-5374-4843-86aa-febd954762b5)

*Example order_book_depth.png: Order-Book Depth*
![order_book_depth](https://github.com/user-attachments/assets/e09ae82d-d319-4538-81e6-c486ac58ab1a)

*Example fake_wall_detection.png: Detected Fake Walls*
![fake_wall_detection](https://github.com/user-attachments/assets/727d7813-4dfa-4b52-ad7e-dabc2e510bff)

<figure>
  <img src="docs/assets/analysis_report.png" width="750" alt="analysis_report txt output">
  <figcaption align="center"><em>Example <code>analysis_report.txt</code> output</em></figcaption>
</figure>

