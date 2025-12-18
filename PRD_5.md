# PRD: Polymarket Best Bid Bot

## Overview

A simple Python bot that places the highest bid on a specified Polymarket prediction market. The bot targets low-probability outcomes (≤5 cents) and always bids one tick above the current best bid, using the minimum order size.

**Version:** 1.0  
**Status:** Draft  
**Author:** [Your Name]  
**Date:** December 2025

---

## Problem Statement

Manually monitoring Polymarket orderbooks and placing competitive bids is time-consuming. This bot automates the process of placing the best bid on low-probability markets where you want to acquire cheap shares.

---

## Goals

### In Scope (v1)
- Place a single limit order on a specified market
- Bid one tick above the current best bid
- Respect a maximum price threshold (5 cents)
- Use minimum order size (5 shares)
- Support dry-run mode for safe testing
- Run once per execution (no continuous monitoring)

### Out of Scope (v2+)
- Continuous monitoring via WebSocket
- Multiple markets in a single run
- Automatic outbid detection and re-bidding
- Position management after fills
- Profit/loss tracking

---

## Technical Architecture

### Technology Stack
- **Language:** Python 3.11
- **Primary Library:** `py-clob-client` (official Polymarket Python client)
- **Network:** Polygon Mainnet (Chain ID: 137)
- **API Endpoint:** `https://clob.polymarket.com`

### System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         BOT EXECUTION FLOW                       │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   START      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────┐
    │  Load Configuration  │
    │  (env vars, args)    │
    └──────────┬───────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Initialize Client   │
    │  (authenticate)      │
    └──────────┬───────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Fetch Order Book    │
    │  for token_id        │
    └──────────┬───────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Get Best Bid Price  │
    └──────────┬───────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │  Is best_bid >= MAX_PRICE?   │
    └──────────┬───────────────────┘
           │
       ┌───┴───┐
       │       │
      YES      NO
       │       │
       ▼       ▼
    ┌──────┐  ┌─────────────────────────┐
    │ EXIT │  │ Calculate new bid:      │
    │(skip)│  │ new_bid = best_bid +    │
    └──────┘  │          tick_size      │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │  Is new_bid > MAX_PRICE?  │
              └───────────┬───────────────┘
                          │
                      ┌───┴───┐
                      │       │
                     YES      NO
                      │       │
                      ▼       ▼
                   ┌──────┐  ┌─────────────────────┐
                   │ EXIT │  │  DRY_RUN mode?      │
                   │(skip)│  └──────────┬──────────┘
                   └──────┘             │
                                    ┌───┴───┐
                                    │       │
                                   YES      NO
                                    │       │
                                    ▼       ▼
                          ┌────────────┐  ┌────────────────┐
                          │ Log what   │  │ Place Order    │
                          │ would be   │  │ (GTC limit)    │
                          │ placed     │  └───────┬────────┘
                          └────────────┘          │
                                                  ▼
                                         ┌────────────────┐
                                         │ Log result     │
                                         └────────────────┘
                                                  │
                                                  ▼
                                              ┌───────┐
                                              │  END  │
                                              └───────┘
```

---

## Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
# Polymarket API Configuration
POLYMARKET_HOST=https://clob.polymarket.com
POLYMARKET_CHAIN_ID=137

# Authentication (KEEP THESE SECRET!)
POLYMARKET_PRIVATE_KEY=your_private_key_here
POLYMARKET_FUNDER_ADDRESS=your_funder_address_here

# Bot Configuration
MAX_BID_PRICE=0.05          # Maximum price willing to bid (in dollars)
ORDER_SIZE=5.0              # Number of shares to buy
DRY_RUN=true                # Set to false to place real orders
```

### Command Line Arguments

```bash
python bot.py --token-id <TOKEN_ID> [--dry-run] [--max-price 0.05] [--size 5]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--token-id` | Yes | - | The token ID of the market outcome to bid on |
| `--dry-run` | No | true | If set, only logs what would happen |
| `--max-price` | No | 0.05 | Maximum bid price in dollars |
| `--size` | No | 5.0 | Number of shares to order |

---

## Setup Instructions

### Prerequisites

1. **Python 3.11** installed
2. **Polymarket account** with funds deposited
3. **MetaMask** or browser wallet connected to Polymarket

### Step 1: Get Your Private Key

Since you connected via a browser wallet (MetaMask):

1. Open MetaMask
2. Click the three dots menu → Account Details → Export Private Key
3. Enter your password and copy the private key
4. **Never share this key with anyone**

### Step 2: Get Your Funder Address

1. Go to [polymarket.com](https://polymarket.com)
2. Click on your profile / wallet
3. Look for "Deposit" or "Deposit Address"
4. This address (starting with `0x...`) is your **funder address**
5. Note: This is different from your MetaMask address — it's your Polymarket proxy wallet

### Step 3: Set Token Allowances (One-Time)

Before placing orders with an EOA/MetaMask wallet, you must approve the exchange contracts to access your USDC and tokens. This is a one-time setup.

**Required Approvals:**

| Token | Contract Address | Approve For |
|-------|-----------------|-------------|
| USDC | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | See contracts below |
| Conditional Tokens | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | See contracts below |

**Contracts to Approve:**
- Main Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- Neg Risk Exchange: `0xC5d563A36AE78145C45a50134d48A1215220f80a`
- Neg Risk Adapter: `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296`

The bot will include a helper script to set these allowances, or you can do it manually via PolygonScan.

### Step 4: Find a Market Token ID

1. Go to [Polymarket](https://polymarket.com) and find a market you want to bid on
2. Use the Gamma API to get the token ID:
   ```
   https://gamma-api.polymarket.com/markets
   ```
3. Or use the CLOB client to search markets (we'll add a helper for this)

The `token_id` is a long numeric string like:
```
71321045679252212594626385532706912750332728571942532289631379312455583992563
```

---

## Bot Logic (Detailed)

### 1. Initialization

```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key=PRIVATE_KEY,
    chain_id=137,
    signature_type=2,  # Browser wallet proxy
    funder=FUNDER_ADDRESS
)
client.set_api_creds(client.create_or_derive_api_creds())
```

### 2. Fetch Order Book

```python
order_book = client.get_order_book(token_id)
```

The order book contains:
- `bids`: List of {price, size} for buy orders
- `asks`: List of {price, size} for sell orders

### 3. Determine Best Bid

```python
best_bid = max(float(bid['price']) for bid in order_book.bids) if order_book.bids else 0
```

### 4. Get Tick Size

```python
tick_size = client.get_tick_size(token_id)
# Usually "0.01", but "0.001" when price > 0.96 or < 0.04
```

### 5. Calculate New Bid

```python
new_bid_price = best_bid + float(tick_size)

# Safety check
if new_bid_price > MAX_BID_PRICE:
    print(f"New bid {new_bid_price} exceeds max {MAX_BID_PRICE}. Skipping.")
    exit()
```

### 6. Place Order

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

order = OrderArgs(
    token_id=token_id,
    price=new_bid_price,
    size=ORDER_SIZE,  # 5 shares
    side=BUY
)

if DRY_RUN:
    print(f"[DRY RUN] Would place order: {ORDER_SIZE} shares @ ${new_bid_price}")
else:
    signed_order = client.create_order(order)
    response = client.post_order(signed_order, OrderType.GTC)
    print(f"Order placed: {response}")
```

---

## Safety Features

### 1. Dry Run Mode (Default)
- Bot runs in dry-run mode by default
- Logs exactly what it would do without placing real orders
- Must explicitly set `DRY_RUN=false` to place real orders

### 2. Maximum Price Threshold
- Configurable max price (default: $0.05)
- Bot refuses to bid above this amount
- Prevents accidental expensive purchases

### 3. Input Validation
- Validates token_id format
- Validates price and size are positive numbers
- Checks that funder address and private key are set

### 4. Error Handling
- Graceful handling of API errors
- Clear error messages for common issues
- No silent failures

---

## File Structure

```
polymarket-bot/
├── .env.example          # Example environment variables
├── .gitignore            # Ignore .env and other sensitive files
├── README.md             # Setup and usage instructions
├── requirements.txt      # Python dependencies
├── bot.py                # Main bot script
├── config.py             # Configuration loading
├── helpers/
│   ├── __init__.py
│   ├── allowances.py     # Token allowance helper
│   └── markets.py        # Market discovery helper
└── PRD.md                # This document
```

---

## Dependencies

```
# Python 3.11 required
py-clob-client>=0.28.0
python-dotenv>=1.0.0
```

---

## Success Criteria

The bot is considered successful when it can:

1. ✅ Connect to Polymarket API with browser wallet auth
2. ✅ Fetch order book for a given token
3. ✅ Calculate the correct new bid price (best bid + tick)
4. ✅ Respect the max price threshold
5. ✅ Log intended action in dry-run mode
6. ✅ Place a real GTC limit order when dry-run is disabled
7. ✅ Handle errors gracefully

---

## Future Enhancements (v2+)

| Feature | Priority | Description |
|---------|----------|-------------|
| Continuous monitoring | High | Use WebSocket to watch for outbids |
| Auto re-bid | High | Automatically place new bid when outbid |
| Multi-market support | Medium | Process a list of markets |
| Order tracking | Medium | Track open orders and fills |
| Cancel stale orders | Medium | Cancel orders that haven't filled after X time |
| Market discovery | Low | Find markets matching criteria (low price, high volume) |
| Notifications | Low | Send alerts on fills via Telegram/Discord |

---

## Appendix

### A. Useful API Endpoints

| Purpose | Endpoint |
|---------|----------|
| CLOB API | `https://clob.polymarket.com` |
| Markets API | `https://gamma-api.polymarket.com/markets` |
| Events API | `https://gamma-api.polymarket.com/events` |
| WebSocket | `wss://ws-subscriptions-clob.polymarket.com/ws/` |

### B. Key Concepts

- **Token ID**: Unique identifier for a specific outcome (YES or NO) in a market
- **Condition ID**: Identifier for the market itself (contains both YES and NO tokens)
- **Tick Size**: Minimum price increment (usually $0.01)
- **GTC**: Good Till Cancelled — order stays on book until filled or cancelled
- **Funder Address**: The Polymarket proxy wallet that holds your funds

### C. References

- [Polymarket CLOB Documentation](https://docs.polymarket.com/developers/CLOB/introduction)
- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client)
- [Gamma Markets API](https://docs.polymarket.com/developers/gamma-markets-api/overview)
- [WebSocket Market Channel](https://docs.polymarket.com/developers/CLOB/websocket/market-channel)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial PRD |
