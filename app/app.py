from flask import Flask, render_template, redirect, request, session
import requests
import csv
import gspread
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

credential = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(credential)
spreadsheet_id = "1RrqmicJq8WiZ5oVDFxzBt8A-nRwwrmTauDJbVnKfBHk"
workbook = client.open_by_key(spreadsheet_id)
worksheet = workbook.worksheet("TrialForPOS")

print(worksheet.col_values(2))

app = Flask(__name__)
app.secret_key = 'skibidi'
def process_order(keychainAmount, stickerAmount, bookmarkAmount):
    priceList = {
            "stickers": {0:0, 1: 15, 2: 25, 3: 40, 4:50},
            "keychains": 35,
            "bookmarks": 25
        }
    stickerTotal = 0
    keychainTotal = priceList['keychains'] * int(keychainAmount)
    bookmarkTotal = priceList['bookmarks'] * int(bookmarkAmount)
    
    
    if int(stickerAmount) == 0:
        stickerTotal = 0
    elif int(stickerAmount) < 4:
        stickerTotal = priceList["stickers"][int(stickerAmount)]
        print(f'{stickerTotal} for {stickerAmount} stickers')
    elif int(stickerAmount):
        stickerTotal = priceList["stickers"][int(stickerAmount)%4] + priceList["stickers"][4] * (int(stickerAmount)//4)
        print(f'{stickerTotal} for {stickerAmount} stickers')
    elif int(stickerAmount) % 4 == 0 and int(stickerAmount) != 0:
        stickerTotal = priceList["stickers"][4] * (int(stickerAmount)//4) 
        print(f'{stickerTotal} for {stickerAmount} stickers')

    totalPurchase = stickerTotal + keychainTotal + bookmarkTotal
    return totalPurchase, stickerTotal, keychainTotal, bookmarkTotal

@app.route("/process", methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        keychainAmount = request.form['keychainAmount']
        stickerAmount = request.form['stickerAmount']
        bookmarkAmount = request.form['bookmarkAmount']
        totalPrice, stickerTotal, keychainTotal, bookmarkTotal = process_order(keychainAmount, stickerAmount, bookmarkAmount)
        session['totalPrice'] = totalPrice
        session['stickerTotal'] = stickerTotal
        session['keychainTotal'] = keychainTotal
        session['bookmarkTotal'] = bookmarkTotal
        return render_template('customerTotal.html', totalPrice=totalPrice, stickerTotal=stickerTotal, keychainTotal=keychainTotal, bookmarkTotal=bookmarkTotal)
    else:
        return "Send POST data please."


@app.route('/checkout', methods=['POST'])
def checkout(): 
    if request.method == 'POST':
        empty_row = len(worksheet.col_values(2)) + 1
        worksheet.update_cell(empty_row, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.update_cell(empty_row, 2, session['totalPrice'])
        worksheet.update_cell(empty_row, 3, session['stickerTotal'])
        worksheet.update_cell(empty_row, 4, session['keychainTotal'])
        worksheet.update_cell(empty_row, 5, session['bookmarkTotal'])
        return redirect('/home')
    
@app.route("/home")
def home():    
        return render_template("index.html")
    
# if __name__ == "__main__":
#     app.run(debug=True)