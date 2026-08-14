import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.environ["ALPHA_VANTAGE_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

WATCHLIST = [
    "AAPL",  
    "MSFT",   
    "GOOGL", 
    "AMZN",   
    "NVDA",   
    "META",   
    "TSLA",   
    "AMD",    
    "NFLX",   
    "DIS",    
    "JPM",    
    "V",      
    "JNJ",    
    "PFE",   
    "WMT",   
    "KO",     
    "XOM",    
    "BA",     
    "COIN",
    "INTC",
]
