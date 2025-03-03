from tkinter.ttk import Progressbar
import customtkinter as ctk
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
updating = False

def get_price(url):
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        return float(response.text.split('<span data-col="info.last_trade.PDrCotVal">')[1].split('</span>')[0].replace(',', ''))
    except:
        return None

def animate_progress():
    if updating:
        current = progress_bar.get()
        new_val = current + 0.00083
        if new_val > 1:
            new_val = 0
        progress_bar.set(new_val)
        root.after(10, animate_progress)


def update_all_prices():
    global updating
    updating = True
    animate_progress()
    def fetch_prices():
        new_prices = {}
        with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
            futures = {executor.submit(get_price, endpoints[key]["url"]): key for key in endpoints}
            for future in as_completed(futures):
                key = futures[future]
                new_prices[key] = future.result()
        root.after(0, lambda: finish_update(new_prices))
    threading.Thread(target=fetch_prices, daemon=True).start()

def finish_update(new_prices):
    global updating
    updating = False
    progress_bar.set(0)
    for key, data in endpoints.items():
        price = new_prices.get(key)
        if price is not None:
            prev_price = data["prev_price"]
            if prev_price is None:
                color_bg = "#6c757d"
                color_text = "#ffffff" 
            else:
                if price > prev_price:
                    color_bg = "#28a745"
                    color_text = "#ffffff"
                elif price < prev_price:
                    color_bg = "#dc3545"
                    color_text = "#ffffff"
                else:
                    color_bg = "#6c757d"
                    color_text = "#ffffff"
                
            data["label"].configure(text=f"{data['prefix']}: {price:,.2f}", text_color=color_text, fg_color=color_bg)
            data["prev_price"] = price
    root.after(60000, update_all_prices)


def on_label_double_click(key):
    # Update price for the clicked label
    endpoints[key]["label"].configure(text="Loading...", text_color="#ff4500")
    update_all_prices()

root = ctk.CTk()
root.title("Currency and Gold Prices")
root.geometry("500x750")
frame = ctk.CTkFrame(master=root, corner_radius=15, fg_color="#333333")
frame.pack(padx=20, pady=20, fill="both", expand=True)

endpoints = {
    "gold": {"url": "https://www.tgju.org/profile/geram18", "prefix": "Gold Price", "label": None, "prev_price": None},
    "dollar": {"url": "https://www.tgju.org/profile/price_dollar_rl", "prefix": "Dollar Price", "label": None, "prev_price": None},
    "euro": {"url": "https://www.tgju.org/profile/price_eur", "prefix": "Euro Price", "label": None, "prev_price": None},
    "api1": {"url": "https://www.tgju.org/profile/sekeb", "prefix": "Coin Price", "label": None, "prev_price": None},
    "api2": {"url": "https://www.tgju.org/profile/price_try", "prefix": "TRY Price", "label": None, "prev_price": None},
    "api3": {"url": "https://www.tgju.org/profile/price_kwd", "prefix": "KWD Price", "label": None, "prev_price": None},
    "api4": {"url": "https://www.tgju.org/profile/price_iqd", "prefix": "IQD Price", "label": None, "prev_price": None},
    "api5": {"url": "https://www.tgju.org/profile/crypto-tether", "prefix": "Tether Price", "label": None, "prev_price": None},
    "api6": {"url": "https://www.tgju.org/profile/crypto-bitcoin", "prefix": "Bitcoin Price", "label": None, "prev_price": None},
    "api7": {"url": "https://www.tgju.org/profile/crypto-ethereum", "prefix": "Ethereum Price", "label": None, "prev_price": None}
}

row = 0
for key, data in endpoints.items():
    lbl = ctk.CTkLabel(master=frame, text=f"{data['prefix']}: -", text_color="#ffffff", font=("Arial", 18, "bold"), fg_color="#ff4500", corner_radius=8, padx=10, pady=10)
    lbl.grid(row=row, column=0, pady=8, padx=8, sticky="ew")
    lbl.bind("<Double-1>", lambda event, key=key: on_label_double_click(key))
    endpoints[key]["label"] = lbl
    row += 1

progress_bar = ctk.CTkProgressBar(master=root, width=400, height=20, fg_color="#ff4500", progress_color="#00ff00")
progress_bar.set(0)
progress_bar.pack(pady=15)

update_all_prices()
root.mainloop()
