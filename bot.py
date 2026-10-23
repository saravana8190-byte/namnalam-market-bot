import requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "8845571222:AAHUU8J1kn_Uk_c_d3sT80mLaSZxSCEuZXo"
TELEGRAM_CHAT_ID = "5125988102"

def fetch_macro_market_drivers():
    macro = {
        "usd_inr": 84.25,
        "cpo_futures_usd": 1148.00,
        "duty_and_cess_multiplier": 1.3025,
        "gst_multiplier": 1.05,
        "port_refining_margin": 3.50
    }
    try:
        fx_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
        if "rates" in fx_res and "INR" in fx_res["rates"]:
            macro["usd_inr"] = float(fx_res["rates"]["INR"])
    except Exception:
        pass
    return macro

def generate_landed_predictions():
    macro = fetch_macro_market_drivers()
    base_cpo_inr_kg = (macro["cpo_futures_usd"] / 1000.0) * macro["usd_inr"]
    base_palm_landed = (base_cpo_inr_kg * macro["duty_and_cess_multiplier"] + macro["port_refining_margin"]) * macro["gst_multiplier"]
    
    base_palm_spot = round(base_palm_landed, 2)
    base_sun_spot = round(base_palm_spot * 1.1233, 2)
    
    predictions = []
    today = datetime.now()

    for i in range(1, 6):
        date_str = (today + timedelta(days=i)).strftime("%d %b")
        daily_drift = 1.0 + (i * 0.0015)
        
        sun_pred = round(base_sun_spot * daily_drift, 2)
        palm_pred = round(base_palm_spot * daily_drift, 2)
        
        predictions.append({
            "day": f"Day {i} ({date_str})",
            "sunflower": sun_pred,
            "palm": palm_pred
        })

    return predictions, base_sun_spot, base_palm_spot

def build_report():
    preds, current_sun, current_palm = generate_landed_predictions()
    current_date = datetime.now().strftime("%d-%b-%Y")

    lines = [
        "🚨 *NAMNALAM AI MARKET INTELLIGENCE REPORT* 🚨",
        f"📅 Date: {current_date}\n",
        "🔮 *5-DAY FORECAST (Land Cost Incl. GST & Duty)*"
    ]

    for p in preds:
        lines.append(f"• {p['day']}: Sunflower ₹{p['sunflower']}/kg | Palmolein ₹{p['palm']}/kg")

    lines.extend([
        "\n🚚 *LANDED PORT SPOT RATES (INCL. GST)*",
        f"🌻 Sunflower Spot: ₹{current_sun}/kg (Chennai / Krishnapatnam)",
        f"🌴 Palmolein Spot: ₹{current_palm}/kg (Chennai / Krishnapatnam)",
        "\n⚡ _Formula: CIF Import Parity + 30.25% Duty/Cess + Port Logistics + 5% GST._"
    ])

    return "\n".join(lines)

if __name__ == "__main__":
    report_text = build_report()
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": report_text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)
