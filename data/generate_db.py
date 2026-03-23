"""
Database Generator for NL-to-SQL Brokerage Query Agent

Generates a SQLite database with 5 tables:
  - instruments: ~500 real NASDAQ/NYSE tickers
  - prices: ~500K rows of realistic OHLCV data
  - accounts: ~1,000 synthetic brokerage accounts
  - orders: ~50,000 synthetic orders seeded from price data
  - positions: ~10,000 derived positions from filled orders

Usage:
    python data/generate_db.py
"""

import os
import sys
import sqlite3
import random
import math
from datetime import datetime, timedelta
from faker import Faker

# ── Configuration ──────────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "brokerage.db")
SEED = 42
NUM_ACCOUNTS = 1000
NUM_ORDERS = 50000
PRICE_DAYS = 504  # ~2 years of trading days

# Real NASDAQ/NYSE tickers with company names and asset class
TICKERS = [
    ("AAPL", "Apple Inc.", "equity", "NASDAQ"),
    ("MSFT", "Microsoft Corporation", "equity", "NASDAQ"),
    ("AMZN", "Amazon.com Inc.", "equity", "NASDAQ"),
    ("GOOGL", "Alphabet Inc. Class A", "equity", "NASDAQ"),
    ("GOOG", "Alphabet Inc. Class C", "equity", "NASDAQ"),
    ("META", "Meta Platforms Inc.", "equity", "NASDAQ"),
    ("TSLA", "Tesla Inc.", "equity", "NASDAQ"),
    ("NVDA", "NVIDIA Corporation", "equity", "NASDAQ"),
    ("BRK.B", "Berkshire Hathaway Inc. Class B", "equity", "NYSE"),
    ("JPM", "JPMorgan Chase & Co.", "equity", "NYSE"),
    ("V", "Visa Inc.", "equity", "NYSE"),
    ("JNJ", "Johnson & Johnson", "equity", "NYSE"),
    ("WMT", "Walmart Inc.", "equity", "NYSE"),
    ("PG", "Procter & Gamble Co.", "equity", "NYSE"),
    ("MA", "Mastercard Inc.", "equity", "NYSE"),
    ("UNH", "UnitedHealth Group Inc.", "equity", "NYSE"),
    ("HD", "The Home Depot Inc.", "equity", "NYSE"),
    ("DIS", "The Walt Disney Company", "equity", "NYSE"),
    ("BAC", "Bank of America Corp.", "equity", "NYSE"),
    ("XOM", "Exxon Mobil Corporation", "equity", "NYSE"),
    ("PFE", "Pfizer Inc.", "equity", "NYSE"),
    ("CSCO", "Cisco Systems Inc.", "equity", "NASDAQ"),
    ("ADBE", "Adobe Inc.", "equity", "NASDAQ"),
    ("CRM", "Salesforce Inc.", "equity", "NYSE"),
    ("NFLX", "Netflix Inc.", "equity", "NASDAQ"),
    ("INTC", "Intel Corporation", "equity", "NASDAQ"),
    ("AMD", "Advanced Micro Devices Inc.", "equity", "NASDAQ"),
    ("CMCSA", "Comcast Corporation", "equity", "NASDAQ"),
    ("PEP", "PepsiCo Inc.", "equity", "NASDAQ"),
    ("COST", "Costco Wholesale Corporation", "equity", "NASDAQ"),
    ("ABT", "Abbott Laboratories", "equity", "NYSE"),
    ("TMO", "Thermo Fisher Scientific Inc.", "equity", "NYSE"),
    ("AVGO", "Broadcom Inc.", "equity", "NASDAQ"),
    ("NKE", "NIKE Inc.", "equity", "NYSE"),
    ("MRK", "Merck & Co. Inc.", "equity", "NYSE"),
    ("LLY", "Eli Lilly and Company", "equity", "NYSE"),
    ("CVX", "Chevron Corporation", "equity", "NYSE"),
    ("ABBV", "AbbVie Inc.", "equity", "NYSE"),
    ("DHR", "Danaher Corporation", "equity", "NYSE"),
    ("ORCL", "Oracle Corporation", "equity", "NYSE"),
    ("ACN", "Accenture plc", "equity", "NYSE"),
    ("TXN", "Texas Instruments Inc.", "equity", "NASDAQ"),
    ("QCOM", "QUALCOMM Inc.", "equity", "NASDAQ"),
    ("MDT", "Medtronic plc", "equity", "NYSE"),
    ("UPS", "United Parcel Service Inc.", "equity", "NYSE"),
    ("LOW", "Lowe's Companies Inc.", "equity", "NYSE"),
    ("PM", "Philip Morris International Inc.", "equity", "NYSE"),
    ("MS", "Morgan Stanley", "equity", "NYSE"),
    ("NEE", "NextEra Energy Inc.", "equity", "NYSE"),
    ("UNP", "Union Pacific Corporation", "equity", "NYSE"),
    ("RTX", "RTX Corporation", "equity", "NYSE"),
    ("HON", "Honeywell International Inc.", "equity", "NASDAQ"),
    ("IBM", "International Business Machines Corp.", "equity", "NYSE"),
    ("BMY", "Bristol-Myers Squibb Company", "equity", "NYSE"),
    ("AMGN", "Amgen Inc.", "equity", "NASDAQ"),
    ("GE", "General Electric Company", "equity", "NYSE"),
    ("CAT", "Caterpillar Inc.", "equity", "NYSE"),
    ("LMT", "Lockheed Martin Corporation", "equity", "NYSE"),
    ("SBUX", "Starbucks Corporation", "equity", "NASDAQ"),
    ("GS", "The Goldman Sachs Group Inc.", "equity", "NYSE"),
    ("BLK", "BlackRock Inc.", "equity", "NYSE"),
    ("ISRG", "Intuitive Surgical Inc.", "equity", "NASDAQ"),
    ("GILD", "Gilead Sciences Inc.", "equity", "NASDAQ"),
    ("AXP", "American Express Company", "equity", "NYSE"),
    ("MDLZ", "Mondelez International Inc.", "equity", "NASDAQ"),
    ("SYK", "Stryker Corporation", "equity", "NYSE"),
    ("ADI", "Analog Devices Inc.", "equity", "NASDAQ"),
    ("BKNG", "Booking Holdings Inc.", "equity", "NASDAQ"),
    ("MMC", "Marsh & McLennan Companies Inc.", "equity", "NYSE"),
    ("CB", "Chubb Limited", "equity", "NYSE"),
    ("TMUS", "T-Mobile US Inc.", "equity", "NASDAQ"),
    ("VRTX", "Vertex Pharmaceuticals Inc.", "equity", "NASDAQ"),
    ("CVS", "CVS Health Corporation", "equity", "NYSE"),
    ("AMT", "American Tower Corporation", "equity", "NYSE"),
    ("CI", "The Cigna Group", "equity", "NYSE"),
    ("LRCX", "Lam Research Corporation", "equity", "NASDAQ"),
    ("SCHW", "The Charles Schwab Corporation", "equity", "NYSE"),
    ("MO", "Altria Group Inc.", "equity", "NYSE"),
    ("ZTS", "Zoetis Inc.", "equity", "NYSE"),
    ("REGN", "Regeneron Pharmaceuticals Inc.", "equity", "NASDAQ"),
    ("BDX", "Becton Dickinson and Company", "equity", "NYSE"),
    ("SO", "The Southern Company", "equity", "NYSE"),
    ("DUK", "Duke Energy Corporation", "equity", "NYSE"),
    ("CL", "Colgate-Palmolive Company", "equity", "NYSE"),
    ("EQIX", "Equinix Inc.", "equity", "NASDAQ"),
    ("BSX", "Boston Scientific Corporation", "equity", "NYSE"),
    ("ITW", "Illinois Tool Works Inc.", "equity", "NYSE"),
    ("AON", "Aon plc", "equity", "NYSE"),
    ("ATVI", "Activision Blizzard Inc.", "equity", "NASDAQ"),
    ("CSX", "CSX Corporation", "equity", "NASDAQ"),
    ("CME", "CME Group Inc.", "equity", "NASDAQ"),
    ("SNPS", "Synopsys Inc.", "equity", "NASDAQ"),
    ("CDNS", "Cadence Design Systems Inc.", "equity", "NASDAQ"),
    ("ICE", "Intercontinental Exchange Inc.", "equity", "NYSE"),
    ("SHW", "The Sherwin-Williams Company", "equity", "NYSE"),
    ("KLAC", "KLA Corporation", "equity", "NASDAQ"),
    ("FIS", "Fidelity National Information Services", "equity", "NYSE"),
    ("NSC", "Norfolk Southern Corporation", "equity", "NYSE"),
    ("PLD", "Prologis Inc.", "equity", "NYSE"),
    ("MCO", "Moody's Corporation", "equity", "NYSE"),
    # ETFs
    ("SPY", "SPDR S&P 500 ETF Trust", "etf", "NYSE"),
    ("QQQ", "Invesco QQQ Trust", "etf", "NASDAQ"),
    ("IWM", "iShares Russell 2000 ETF", "etf", "NYSE"),
    ("VTI", "Vanguard Total Stock Market ETF", "etf", "NYSE"),
    ("VOO", "Vanguard S&P 500 ETF", "etf", "NYSE"),
    ("EFA", "iShares MSCI EAFE ETF", "etf", "NYSE"),
    ("EEM", "iShares MSCI Emerging Markets ETF", "etf", "NYSE"),
    ("GLD", "SPDR Gold Shares", "etf", "NYSE"),
    ("SLV", "iShares Silver Trust", "etf", "NYSE"),
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "etf", "NASDAQ"),
    ("HYG", "iShares iBoxx $ High Yield Corporate Bond ETF", "etf", "NYSE"),
    ("LQD", "iShares iBoxx $ Investment Grade Corporate Bond ETF", "etf", "NYSE"),
    ("VNQ", "Vanguard Real Estate ETF", "etf", "NYSE"),
    ("XLF", "Financial Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLK", "Technology Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLE", "Energy Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLV", "Health Care Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLI", "Industrial Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLP", "Consumer Staples Select Sector SPDR Fund", "etf", "NYSE"),
    ("XLY", "Consumer Discretionary Select Sector SPDR Fund", "etf", "NYSE"),
    ("ARKK", "ARK Innovation ETF", "etf", "NYSE"),
    ("DIA", "SPDR Dow Jones Industrial Average ETF", "etf", "NYSE"),
    ("VEA", "Vanguard FTSE Developed Markets ETF", "etf", "NYSE"),
    ("VWO", "Vanguard FTSE Emerging Markets ETF", "etf", "NYSE"),
    ("BND", "Vanguard Total Bond Market ETF", "etf", "NASDAQ"),
    ("AGG", "iShares Core U.S. Aggregate Bond ETF", "etf", "NYSE"),
    ("IEMG", "iShares Core MSCI Emerging Markets ETF", "etf", "NYSE"),
    ("VIG", "Vanguard Dividend Appreciation ETF", "etf", "NYSE"),
    ("VUG", "Vanguard Growth ETF", "etf", "NYSE"),
    ("VTV", "Vanguard Value ETF", "etf", "NYSE"),
    ("SCHD", "Schwab U.S. Dividend Equity ETF", "etf", "NYSE"),
    # Additional equities to reach ~500
    ("PYPL", "PayPal Holdings Inc.", "equity", "NASDAQ"),
    ("NOW", "ServiceNow Inc.", "equity", "NYSE"),
    ("T", "AT&T Inc.", "equity", "NYSE"),
    ("VZ", "Verizon Communications Inc.", "equity", "NYSE"),
    ("INTU", "Intuit Inc.", "equity", "NASDAQ"),
    ("ADP", "Automatic Data Processing Inc.", "equity", "NASDAQ"),
    ("SPGI", "S&P Global Inc.", "equity", "NYSE"),
    ("AMAT", "Applied Materials Inc.", "equity", "NASDAQ"),
    ("DE", "Deere & Company", "equity", "NYSE"),
    ("MMM", "3M Company", "equity", "NYSE"),
    ("PNC", "The PNC Financial Services Group", "equity", "NYSE"),
    ("TJX", "The TJX Companies Inc.", "equity", "NYSE"),
    ("USB", "U.S. Bancorp", "equity", "NYSE"),
    ("COP", "ConocoPhillips", "equity", "NYSE"),
    ("EOG", "EOG Resources Inc.", "equity", "NYSE"),
    ("AIG", "American International Group Inc.", "equity", "NYSE"),
    ("MET", "MetLife Inc.", "equity", "NYSE"),
    ("TGT", "Target Corporation", "equity", "NYSE"),
    ("F", "Ford Motor Company", "equity", "NYSE"),
    ("GM", "General Motors Company", "equity", "NYSE"),
    ("RIVN", "Rivian Automotive Inc.", "equity", "NASDAQ"),
    ("LCID", "Lucid Group Inc.", "equity", "NASDAQ"),
    ("SQ", "Block Inc.", "equity", "NYSE"),
    ("SHOP", "Shopify Inc.", "equity", "NYSE"),
    ("SNOW", "Snowflake Inc.", "equity", "NYSE"),
    ("PLTR", "Palantir Technologies Inc.", "equity", "NYSE"),
    ("UBER", "Uber Technologies Inc.", "equity", "NYSE"),
    ("LYFT", "Lyft Inc.", "equity", "NASDAQ"),
    ("ABNB", "Airbnb Inc.", "equity", "NASDAQ"),
    ("DDOG", "Datadog Inc.", "equity", "NASDAQ"),
    ("ZM", "Zoom Video Communications Inc.", "equity", "NASDAQ"),
    ("DOCU", "DocuSign Inc.", "equity", "NASDAQ"),
    ("CRWD", "CrowdStrike Holdings Inc.", "equity", "NASDAQ"),
    ("NET", "Cloudflare Inc.", "equity", "NYSE"),
    ("OKTA", "Okta Inc.", "equity", "NASDAQ"),
    ("TWLO", "Twilio Inc.", "equity", "NYSE"),
    ("PANW", "Palo Alto Networks Inc.", "equity", "NASDAQ"),
    ("ZS", "Zscaler Inc.", "equity", "NASDAQ"),
    ("FTNT", "Fortinet Inc.", "equity", "NASDAQ"),
    ("TEAM", "Atlassian Corporation", "equity", "NASDAQ"),
    ("MDB", "MongoDB Inc.", "equity", "NASDAQ"),
    ("COIN", "Coinbase Global Inc.", "equity", "NASDAQ"),
    ("HOOD", "Robinhood Markets Inc.", "equity", "NASDAQ"),
    ("SOFI", "SoFi Technologies Inc.", "equity", "NASDAQ"),
    ("WFC", "Wells Fargo & Company", "equity", "NYSE"),
    ("C", "Citigroup Inc.", "equity", "NYSE"),
    ("COF", "Capital One Financial Corp.", "equity", "NYSE"),
    ("ALLY", "Ally Financial Inc.", "equity", "NYSE"),
    ("KO", "The Coca-Cola Company", "equity", "NYSE"),
    ("MCD", "McDonald's Corporation", "equity", "NYSE"),
    ("YUM", "Yum! Brands Inc.", "equity", "NYSE"),
    ("CMG", "Chipotle Mexican Grill Inc.", "equity", "NYSE"),
    ("DKNG", "DraftKings Inc.", "equity", "NASDAQ"),
    ("WYNN", "Wynn Resorts Limited", "equity", "NASDAQ"),
    ("MAR", "Marriott International Inc.", "equity", "NASDAQ"),
    ("HLT", "Hilton Worldwide Holdings Inc.", "equity", "NYSE"),
    ("DAL", "Delta Air Lines Inc.", "equity", "NYSE"),
    ("UAL", "United Airlines Holdings Inc.", "equity", "NASDAQ"),
    ("AAL", "American Airlines Group Inc.", "equity", "NASDAQ"),
    ("LUV", "Southwest Airlines Co.", "equity", "NYSE"),
    ("BA", "The Boeing Company", "equity", "NYSE"),
    ("GD", "General Dynamics Corporation", "equity", "NYSE"),
    ("NOC", "Northrop Grumman Corporation", "equity", "NYSE"),
    ("MRNA", "Moderna Inc.", "equity", "NASDAQ"),
    ("BIIB", "Biogen Inc.", "equity", "NASDAQ"),
    ("ILMN", "Illumina Inc.", "equity", "NASDAQ"),
    ("DXCM", "DexCom Inc.", "equity", "NASDAQ"),
    ("EW", "Edwards Lifesciences Corp.", "equity", "NYSE"),
    ("A", "Agilent Technologies Inc.", "equity", "NYSE"),
    ("WAT", "Waters Corporation", "equity", "NYSE"),
    ("WM", "Waste Management Inc.", "equity", "NYSE"),
    ("RSG", "Republic Services Inc.", "equity", "NYSE"),
    ("DOW", "Dow Inc.", "equity", "NYSE"),
    ("DD", "DuPont de Nemours Inc.", "equity", "NYSE"),
    ("APD", "Air Products and Chemicals Inc.", "equity", "NYSE"),
    ("ECL", "Ecolab Inc.", "equity", "NYSE"),
    ("EMR", "Emerson Electric Co.", "equity", "NYSE"),
    ("ROK", "Rockwell Automation Inc.", "equity", "NYSE"),
    ("CTAS", "Cintas Corporation", "equity", "NASDAQ"),
    ("FAST", "Fastenal Company", "equity", "NASDAQ"),
    ("PAYX", "Paychex Inc.", "equity", "NASDAQ"),
    ("WDC", "Western Digital Corp.", "equity", "NASDAQ"),
    ("STX", "Seagate Technology Holdings", "equity", "NASDAQ"),
    ("MRVL", "Marvell Technology Inc.", "equity", "NASDAQ"),
    ("ON", "ON Semiconductor Corp.", "equity", "NASDAQ"),
    ("SWKS", "Skyworks Solutions Inc.", "equity", "NASDAQ"),
    ("MPWR", "Monolithic Power Systems Inc.", "equity", "NASDAQ"),
    ("ENPH", "Enphase Energy Inc.", "equity", "NASDAQ"),
    ("SEDG", "SolarEdge Technologies Inc.", "equity", "NASDAQ"),
    ("FSLR", "First Solar Inc.", "equity", "NASDAQ"),
    ("RUN", "Sunrun Inc.", "equity", "NASDAQ"),
    ("PLUG", "Plug Power Inc.", "equity", "NASDAQ"),
    ("CHPT", "ChargePoint Holdings Inc.", "equity", "NYSE"),
    ("RIVN", "Rivian Automotive Inc.", "equity", "NASDAQ"),
    ("NIO", "NIO Inc.", "equity", "NYSE"),
    ("XPEV", "XPeng Inc.", "equity", "NYSE"),
    ("LI", "Li Auto Inc.", "equity", "NASDAQ"),
    ("BABA", "Alibaba Group Holding Limited", "equity", "NYSE"),
    ("JD", "JD.com Inc.", "equity", "NASDAQ"),
    ("PDD", "PDD Holdings Inc.", "equity", "NASDAQ"),
    ("BIDU", "Baidu Inc.", "equity", "NASDAQ"),
    ("TSM", "Taiwan Semiconductor Manufacturing", "equity", "NYSE"),
    ("SONY", "Sony Group Corporation", "equity", "NYSE"),
    ("TM", "Toyota Motor Corporation", "equity", "NYSE"),
    ("MELI", "MercadoLibre Inc.", "equity", "NASDAQ"),
    ("SE", "Sea Limited", "equity", "NYSE"),
    ("GRAB", "Grab Holdings Limited", "equity", "NASDAQ"),
    ("NU", "Nu Holdings Ltd.", "equity", "NYSE"),
    ("SPOT", "Spotify Technology S.A.", "equity", "NYSE"),
    ("SNAP", "Snap Inc.", "equity", "NYSE"),
    ("PINS", "Pinterest Inc.", "equity", "NYSE"),
    ("RBLX", "Roblox Corporation", "equity", "NYSE"),
    ("U", "Unity Technologies Inc.", "equity", "NYSE"),
    ("PATH", "UiPath Inc.", "equity", "NYSE"),
    ("AI", "C3.ai Inc.", "equity", "NYSE"),
    ("UPST", "Upstart Holdings Inc.", "equity", "NASDAQ"),
    ("AFRM", "Affirm Holdings Inc.", "equity", "NASDAQ"),
    ("BILL", "BILL Holdings Inc.", "equity", "NYSE"),
    ("HUBS", "HubSpot Inc.", "equity", "NYSE"),
    ("VEEV", "Veeva Systems Inc.", "equity", "NYSE"),
    ("WDAY", "Workday Inc.", "equity", "NASDAQ"),
    ("SPLK", "Splunk Inc.", "equity", "NASDAQ"),
    ("ESTC", "Elastic N.V.", "equity", "NYSE"),
    ("CFLT", "Confluent Inc.", "equity", "NASDAQ"),
    ("DDOG", "Datadog Inc.", "equity", "NASDAQ"),
    ("MNDY", "Monday.com Ltd.", "equity", "NASDAQ"),
    ("TTD", "The Trade Desk Inc.", "equity", "NASDAQ"),
    ("ROKU", "Roku Inc.", "equity", "NASDAQ"),
    ("PARA", "Paramount Global", "equity", "NASDAQ"),
    ("WBD", "Warner Bros. Discovery Inc.", "equity", "NASDAQ"),
    ("NCLH", "Norwegian Cruise Line Holdings", "equity", "NYSE"),
    ("CCL", "Carnival Corporation", "equity", "NYSE"),
    ("RCL", "Royal Caribbean Cruises Ltd.", "equity", "NYSE"),
    ("EXPE", "Expedia Group Inc.", "equity", "NASDAQ"),
    ("BKNG", "Booking Holdings Inc.", "equity", "NASDAQ"),
    ("TRIP", "TripAdvisor Inc.", "equity", "NASDAQ"),
    ("ETSY", "Etsy Inc.", "equity", "NASDAQ"),
    ("W", "Wayfair Inc.", "equity", "NYSE"),
    ("CHWY", "Chewy Inc.", "equity", "NYSE"),
    ("DG", "Dollar General Corporation", "equity", "NYSE"),
    ("DLTR", "Dollar Tree Inc.", "equity", "NASDAQ"),
    ("ROST", "Ross Stores Inc.", "equity", "NASDAQ"),
    ("GPS", "The Gap Inc.", "equity", "NYSE"),
    ("ANF", "Abercrombie & Fitch Co.", "equity", "NYSE"),
    ("LULU", "Lululemon Athletica Inc.", "equity", "NASDAQ"),
    ("DECK", "Deckers Outdoor Corporation", "equity", "NYSE"),
    ("CROX", "Crocs Inc.", "equity", "NASDAQ"),
    ("HAS", "Hasbro Inc.", "equity", "NASDAQ"),
    ("MAT", "Mattel Inc.", "equity", "NASDAQ"),
    ("EA", "Electronic Arts Inc.", "equity", "NASDAQ"),
    ("TTWO", "Take-Two Interactive Software", "equity", "NASDAQ"),
    ("NTES", "NetEase Inc.", "equity", "NASDAQ"),
    ("MSCI", "MSCI Inc.", "equity", "NYSE"),
    ("MKTX", "MarketAxess Holdings Inc.", "equity", "NASDAQ"),
    ("CBOE", "Cboe Global Markets Inc.", "equity", "NASDAQ"),
    ("NDAQ", "Nasdaq Inc.", "equity", "NASDAQ"),
    ("FLT", "FLEETCOR Technologies Inc.", "equity", "NYSE"),
    ("GPN", "Global Payments Inc.", "equity", "NYSE"),
    ("FISV", "Fiserv Inc.", "equity", "NYSE"),
    ("VRSK", "Verisk Analytics Inc.", "equity", "NASDAQ"),
    ("FTV", "Fortive Corporation", "equity", "NYSE"),
    ("BR", "Broadridge Financial Solutions", "equity", "NYSE"),
    ("TRMB", "Trimble Inc.", "equity", "NASDAQ"),
    ("KEYS", "Keysight Technologies Inc.", "equity", "NYSE"),
    ("TER", "Teradyne Inc.", "equity", "NASDAQ"),
    ("ZBRA", "Zebra Technologies Corp.", "equity", "NASDAQ"),
    ("POOL", "Pool Corporation", "equity", "NASDAQ"),
    ("IDXX", "IDEXX Laboratories Inc.", "equity", "NASDAQ"),
    ("ALGN", "Align Technology Inc.", "equity", "NASDAQ"),
    ("HOLX", "Hologic Inc.", "equity", "NASDAQ"),
    ("MTD", "Mettler-Toledo International", "equity", "NYSE"),
    ("RMD", "ResMed Inc.", "equity", "NYSE"),
    ("IQV", "IQVIA Holdings Inc.", "equity", "NYSE"),
    ("CNC", "Centene Corporation", "equity", "NYSE"),
    ("HCA", "HCA Healthcare Inc.", "equity", "NYSE"),
    ("ELV", "Elevance Health Inc.", "equity", "NYSE"),
    ("HUM", "Humana Inc.", "equity", "NYSE"),
    ("MCK", "McKesson Corporation", "equity", "NYSE"),
    ("CAH", "Cardinal Health Inc.", "equity", "NYSE"),
    ("ABC", "AmerisourceBergen Corp.", "equity", "NYSE"),
    ("GEHC", "GE HealthCare Technologies", "equity", "NASDAQ"),
    ("PODD", "Insulet Corporation", "equity", "NASDAQ"),
    ("TFX", "Teleflex Inc.", "equity", "NYSE"),
    ("BAX", "Baxter International Inc.", "equity", "NYSE"),
    ("ZBH", "Zimmer Biomet Holdings Inc.", "equity", "NYSE"),
    ("STE", "STERIS plc", "equity", "NYSE"),
    ("TECH", "Bio-Techne Corporation", "equity", "NASDAQ"),
    ("BIO", "Bio-Rad Laboratories Inc.", "equity", "NYSE"),
    ("PKI", "PerkinElmer Inc.", "equity", "NYSE"),
    ("CSGP", "CoStar Group Inc.", "equity", "NASDAQ"),
    ("ANSS", "ANSYS Inc.", "equity", "NASDAQ"),
    ("CPRT", "Copart Inc.", "equity", "NASDAQ"),
    ("ODFL", "Old Dominion Freight Line Inc.", "equity", "NASDAQ"),
    ("JBHT", "J.B. Hunt Transport Services", "equity", "NASDAQ"),
    ("CHRW", "C.H. Robinson Worldwide Inc.", "equity", "NASDAQ"),
    ("EXPD", "Expeditors International", "equity", "NASDAQ"),
    ("XPO", "XPO Inc.", "equity", "NYSE"),
    ("FDX", "FedEx Corporation", "equity", "NYSE"),
    ("CARR", "Carrier Global Corporation", "equity", "NYSE"),
    ("OTIS", "Otis Worldwide Corporation", "equity", "NYSE"),
    ("JCI", "Johnson Controls International", "equity", "NYSE"),
    ("TT", "Trane Technologies plc", "equity", "NYSE"),
    ("IR", "Ingersoll Rand Inc.", "equity", "NYSE"),
    ("AME", "AMETEK Inc.", "equity", "NYSE"),
    ("GNRC", "Generac Holdings Inc.", "equity", "NYSE"),
    ("PWR", "Quanta Services Inc.", "equity", "NYSE"),
    ("LIN", "Linde plc", "equity", "NYSE"),
    ("SHW", "Sherwin-Williams Company", "equity", "NYSE"),
    ("FCX", "Freeport-McMoRan Inc.", "equity", "NYSE"),
    ("NEM", "Newmont Corporation", "equity", "NYSE"),
    ("GOLD", "Barrick Gold Corporation", "equity", "NYSE"),
    ("AEM", "Agnico Eagle Mines Limited", "equity", "NYSE"),
    ("KMI", "Kinder Morgan Inc.", "equity", "NYSE"),
    ("WMB", "The Williams Companies Inc.", "equity", "NYSE"),
    ("OKE", "ONEOK Inc.", "equity", "NYSE"),
    ("ET", "Energy Transfer LP", "equity", "NYSE"),
    ("SLB", "Schlumberger Limited", "equity", "NYSE"),
    ("HAL", "Halliburton Company", "equity", "NYSE"),
    ("BKR", "Baker Hughes Company", "equity", "NASDAQ"),
    ("PSX", "Phillips 66", "equity", "NYSE"),
    ("VLO", "Valero Energy Corporation", "equity", "NYSE"),
    ("MPC", "Marathon Petroleum Corporation", "equity", "NYSE"),
    ("OXY", "Occidental Petroleum Corp.", "equity", "NYSE"),
    ("DVN", "Devon Energy Corporation", "equity", "NYSE"),
    ("PXD", "Pioneer Natural Resources Co.", "equity", "NYSE"),
    ("FANG", "Diamondback Energy Inc.", "equity", "NASDAQ"),
    ("APA", "APA Corporation", "equity", "NASDAQ"),
    ("CTRA", "Coterra Energy Inc.", "equity", "NYSE"),
    ("EQT", "EQT Corporation", "equity", "NYSE"),
    ("AR", "Antero Resources Corp.", "equity", "NYSE"),
    ("RRC", "Range Resources Corporation", "equity", "NYSE"),
    ("SWN", "Southwestern Energy Co.", "equity", "NYSE"),
    ("CNP", "CenterPoint Energy Inc.", "equity", "NYSE"),
    ("AEE", "Ameren Corporation", "equity", "NYSE"),
    ("ES", "Eversource Energy", "equity", "NYSE"),
    ("WEC", "WEC Energy Group Inc.", "equity", "NYSE"),
    ("AEP", "American Electric Power Co.", "equity", "NASDAQ"),
    ("D", "Dominion Energy Inc.", "equity", "NYSE"),
    ("EXC", "Exelon Corporation", "equity", "NASDAQ"),
    ("XEL", "Xcel Energy Inc.", "equity", "NASDAQ"),
    ("AWK", "American Water Works Co.", "equity", "NYSE"),
    ("ED", "Consolidated Edison Inc.", "equity", "NYSE"),
    ("PEG", "Public Service Enterprise Group", "equity", "NYSE"),
    ("FE", "FirstEnergy Corp.", "equity", "NYSE"),
    ("PPL", "PPL Corporation", "equity", "NYSE"),
    ("CMS", "CMS Energy Corporation", "equity", "NYSE"),
    ("ATO", "Atmos Energy Corporation", "equity", "NYSE"),
    ("NI", "NiSource Inc.", "equity", "NYSE"),
    ("EVRG", "Evergy Inc.", "equity", "NYSE"),
    ("DTE", "DTE Energy Company", "equity", "NYSE"),
    ("ETR", "Entergy Corporation", "equity", "NYSE"),
    ("LNT", "Alliant Energy Corp.", "equity", "NASDAQ"),
    ("WTRG", "Essential Utilities Inc.", "equity", "NYSE"),
    ("O", "Realty Income Corporation", "equity", "NYSE"),
    ("PSA", "Public Storage", "equity", "NYSE"),
    ("EQR", "Equity Residential", "equity", "NYSE"),
    ("AVB", "AvalonBay Communities Inc.", "equity", "NYSE"),
    ("DLR", "Digital Realty Trust Inc.", "equity", "NYSE"),
    ("SBAC", "SBA Communications Corp.", "equity", "NASDAQ"),
    ("CCI", "Crown Castle Inc.", "equity", "NYSE"),
    ("WELL", "Welltower Inc.", "equity", "NYSE"),
    ("ARE", "Alexandria Real Estate Equities", "equity", "NYSE"),
    ("MAA", "Mid-America Apartment Communities", "equity", "NYSE"),
    ("UDR", "UDR Inc.", "equity", "NYSE"),
    ("ESS", "Essex Property Trust Inc.", "equity", "NYSE"),
    ("CPT", "Camden Property Trust", "equity", "NYSE"),
    ("SPG", "Simon Property Group Inc.", "equity", "NYSE"),
    ("REG", "Regency Centers Corporation", "equity", "NASDAQ"),
    ("KIM", "Kimco Realty Corporation", "equity", "NYSE"),
    ("HST", "Host Hotels & Resorts Inc.", "equity", "NASDAQ"),
    ("PEAK", "Healthpeak Properties Inc.", "equity", "NYSE"),
    ("VTR", "Ventas Inc.", "equity", "NYSE"),
    ("IRM", "Iron Mountain Inc.", "equity", "NYSE"),
    ("CBRE", "CBRE Group Inc.", "equity", "NYSE"),
    ("JLL", "Jones Lang LaSalle Inc.", "equity", "NYSE"),
    ("RKT", "Rocket Companies Inc.", "equity", "NYSE"),
    ("OPEN", "Opendoor Technologies Inc.", "equity", "NASDAQ"),
    ("Z", "Zillow Group Inc.", "equity", "NASDAQ"),
    ("RDFN", "Redfin Corporation", "equity", "NASDAQ"),
    ("FIGS", "FIGS Inc.", "equity", "NYSE"),
    ("HIMS", "Hims & Hers Health Inc.", "equity", "NYSE"),
    ("DOCS", "Doximity Inc.", "equity", "NYSE"),
    ("AMWL", "American Well Corporation", "equity", "NYSE"),
    ("EDIT", "Editas Medicine Inc.", "equity", "NASDAQ"),
    ("CRSP", "CRISPR Therapeutics AG", "equity", "NASDAQ"),
    ("NTLA", "Intellia Therapeutics Inc.", "equity", "NASDAQ"),
    ("BEAM", "Beam Therapeutics Inc.", "equity", "NASDAQ"),
    ("ARKG", "ARK Genomic Revolution ETF", "etf", "NYSE"),
    ("ARKW", "ARK Next Generation Internet ETF", "etf", "NYSE"),
    ("ARKF", "ARK Fintech Innovation ETF", "etf", "NYSE"),
    ("ARKQ", "ARK Autonomous Technology & Robotics ETF", "etf", "NYSE"),
    ("SOXX", "iShares Semiconductor ETF", "etf", "NASDAQ"),
    ("SMH", "VanEck Semiconductor ETF", "etf", "NASDAQ"),
    ("XBI", "SPDR S&P Biotech ETF", "etf", "NYSE"),
    ("IBB", "iShares Biotechnology ETF", "etf", "NASDAQ"),
    ("KWEB", "KraneShares CSI China Internet ETF", "etf", "NYSE"),
    ("FXI", "iShares China Large-Cap ETF", "etf", "NYSE"),
    ("INDA", "iShares MSCI India ETF", "etf", "NYSE"),
    ("EWZ", "iShares MSCI Brazil ETF", "etf", "NYSE"),
    ("EWJ", "iShares MSCI Japan ETF", "etf", "NYSE"),
    ("URA", "Global X Uranium ETF", "etf", "NYSE"),
    ("ICLN", "iShares Global Clean Energy ETF", "etf", "NASDAQ"),
    ("TAN", "Invesco Solar ETF", "etf", "NYSE"),
    ("BOTZ", "Global X Robotics & AI ETF", "etf", "NASDAQ"),
    ("HACK", "ETFMG Prime Cyber Security ETF", "etf", "NYSE"),
    ("SKYY", "First Trust Cloud Computing ETF", "etf", "NASDAQ"),
    ("FINX", "Global X FinTech ETF", "etf", "NASDAQ"),
]

# Remove duplicates (keeping first occurrence)
seen = set()
unique_tickers = []
for t in TICKERS:
    if t[0] not in seen:
        seen.add(t[0])
        unique_tickers.append(t)
TICKERS = unique_tickers


# ── Helpers ────────────────────────────────────────────────────────────────────

def generate_price_series(
    rng: random.Random,
    start_price: float,
    num_days: int,
    volatility: float = 0.02,
) -> list[dict]:
    """Generate realistic OHLCV data using geometric Brownian motion."""
    prices = []
    price = start_price
    for _ in range(num_days):
        # Daily return with drift and volatility
        daily_return = rng.gauss(0.0003, volatility)
        price *= math.exp(daily_return)
        price = max(price, 0.50)  # Floor at $0.50

        open_price = price * (1 + rng.gauss(0, 0.005))
        high = max(open_price, price) * (1 + abs(rng.gauss(0, 0.01)))
        low = min(open_price, price) * (1 - abs(rng.gauss(0, 0.01)))
        volume = int(abs(rng.gauss(5_000_000, 3_000_000))) + 100_000

        prices.append({
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(price, 2),
            "volume": volume,
        })
    return prices


def get_trading_days(start_date: datetime, num_days: int) -> list[str]:
    """Generate a list of trading days (skip weekends)."""
    days = []
    current = start_date
    while len(days) < num_days:
        if current.weekday() < 5:  # Monday=0, Friday=4
            days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return days


# ── Main Generation ───────────────────────────────────────────────────────────

def generate_database():
    """Build the full SQLite database."""
    rng = random.Random(SEED)
    fake = Faker()
    Faker.seed(SEED)

    # Remove existing DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("🏗️  Creating tables...")

    # ── 1. instruments ─────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE instruments (
            ticker      TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            asset_class TEXT NOT NULL,  -- 'equity' or 'etf'
            exchange    TEXT NOT NULL   -- 'NASDAQ' or 'NYSE'
        )
    """)
    cur.executemany(
        "INSERT INTO instruments (ticker, name, asset_class, exchange) VALUES (?, ?, ?, ?)",
        TICKERS,
    )
    print(f"   ✅ instruments: {len(TICKERS)} tickers")

    # ── 2. prices ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE prices (
            ticker  TEXT NOT NULL,
            date    TEXT NOT NULL,
            open    REAL NOT NULL,
            high    REAL NOT NULL,
            low     REAL NOT NULL,
            close   REAL NOT NULL,
            volume  INTEGER NOT NULL,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES instruments(ticker)
        )
    """)

    start_date = datetime(2024, 1, 2)
    trading_days = get_trading_days(start_date, PRICE_DAYS)

    price_rows = []
    # Map ticker → list of (date, close) for order generation
    ticker_prices = {}

    for ticker, name, asset_class, exchange in TICKERS:
        # Realistic starting prices based on asset class
        if asset_class == "etf":
            start_price = rng.uniform(20, 500)
            vol = 0.012
        else:
            start_price = rng.uniform(5, 800)
            vol = rng.uniform(0.015, 0.04)

        series = generate_price_series(rng, start_price, PRICE_DAYS, vol)
        daily_data = []
        for day, px in zip(trading_days, series):
            price_rows.append((ticker, day, px["open"], px["high"], px["low"], px["close"], px["volume"]))
            daily_data.append((day, px["close"]))
        ticker_prices[ticker] = daily_data

    cur.executemany(
        "INSERT INTO prices (ticker, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
        price_rows,
    )
    print(f"   ✅ prices: {len(price_rows):,} rows")

    # ── 3. accounts ────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE accounts (
            account_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            country      TEXT NOT NULL,
            account_type TEXT NOT NULL,  -- 'individual', 'institutional', 'retirement'
            created_at   TEXT NOT NULL
        )
    """)

    account_types = ["individual", "institutional", "retirement"]
    accounts = []
    for i in range(NUM_ACCOUNTS):
        name = fake.name()
        country = rng.choice(["US", "US", "US", "US", "CA", "UK", "DE", "JP", "AU", "SG"])
        acct_type = rng.choice(account_types)
        created_at = fake.date_time_between(
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2024, 6, 1),
        ).strftime("%Y-%m-%d %H:%M:%S")
        accounts.append((name, country, acct_type, created_at))

    cur.executemany(
        "INSERT INTO accounts (name, country, account_type, created_at) VALUES (?, ?, ?, ?)",
        accounts,
    )
    print(f"   ✅ accounts: {NUM_ACCOUNTS:,} rows")

    # ── 4. orders ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE orders (
            order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER NOT NULL,
            ticker      TEXT NOT NULL,
            side        TEXT NOT NULL,    -- 'buy' or 'sell'
            qty         INTEGER NOT NULL,
            price       REAL NOT NULL,
            status      TEXT NOT NULL,    -- 'filled', 'cancelled', 'pending'
            created_at  TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id),
            FOREIGN KEY (ticker) REFERENCES instruments(ticker)
        )
    """)

    ticker_list = [t[0] for t in TICKERS]
    statuses = ["filled", "filled", "filled", "filled", "cancelled", "pending"]  # 67% filled
    orders = []

    for _ in range(NUM_ORDERS):
        account_id = rng.randint(1, NUM_ACCOUNTS)
        ticker = rng.choice(ticker_list)
        side = rng.choice(["buy", "buy", "sell"])  # More buys than sells
        qty = rng.choice([1, 5, 10, 10, 25, 50, 100, 100, 200, 500])
        status = rng.choice(statuses)

        # Pick a random date from the price data and use that day's close
        day_idx = rng.randint(0, len(ticker_prices[ticker]) - 1)
        date_str, close_price = ticker_prices[ticker][day_idx]
        # Slight variation from close price
        fill_price = round(close_price * rng.uniform(0.995, 1.005), 2)
        # Add random time
        hour = rng.randint(9, 15)
        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)
        created_at = f"{date_str} {hour:02d}:{minute:02d}:{second:02d}"

        orders.append((account_id, ticker, side, qty, fill_price, status, created_at))

    cur.executemany(
        "INSERT INTO orders (account_id, ticker, side, qty, price, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        orders,
    )
    print(f"   ✅ orders: {NUM_ORDERS:,} rows")

    # ── 5. positions (derived from filled orders) ──────────────────────────────
    cur.execute("""
        CREATE TABLE positions (
            account_id   INTEGER NOT NULL,
            ticker       TEXT NOT NULL,
            shares_held  INTEGER NOT NULL,
            avg_cost     REAL NOT NULL,
            last_updated TEXT NOT NULL,
            PRIMARY KEY (account_id, ticker),
            FOREIGN KEY (account_id) REFERENCES accounts(account_id),
            FOREIGN KEY (ticker) REFERENCES instruments(ticker)
        )
    """)

    # Aggregate filled orders to derive positions
    cur.execute("""
        INSERT INTO positions (account_id, ticker, shares_held, avg_cost, last_updated)
        SELECT
            account_id,
            ticker,
            SUM(CASE WHEN side = 'buy' THEN qty ELSE -qty END) AS shares_held,
            ROUND(
                SUM(CASE WHEN side = 'buy' THEN qty * price ELSE 0 END) * 1.0 /
                MAX(SUM(CASE WHEN side = 'buy' THEN qty ELSE 0 END), 1),
                2
            ) AS avg_cost,
            MAX(created_at) AS last_updated
        FROM orders
        WHERE status = 'filled'
        GROUP BY account_id, ticker
        HAVING SUM(CASE WHEN side = 'buy' THEN qty ELSE -qty END) > 0
    """)
    position_count = cur.execute("SELECT COUNT(*) FROM positions").fetchone()[0]
    print(f"   ✅ positions: {position_count:,} rows")

    # ── Indexes ────────────────────────────────────────────────────────────────
    print("📇 Creating indexes...")
    cur.execute("CREATE INDEX idx_prices_ticker_date ON prices(ticker, date)")
    cur.execute("CREATE INDEX idx_orders_account_id ON orders(account_id, created_at)")
    cur.execute("CREATE INDEX idx_orders_ticker ON orders(ticker)")
    cur.execute("CREATE INDEX idx_orders_created_at ON orders(created_at)")
    cur.execute("CREATE INDEX idx_orders_status ON orders(status)")
    cur.execute("CREATE INDEX idx_positions_account_id ON positions(account_id)")

    conn.commit()
    conn.close()

    db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n🎉 Database generated at: {DB_PATH}")
    print(f"   Size: {db_size:.1f} MB")


if __name__ == "__main__":
    generate_database()
