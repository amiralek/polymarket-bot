# Polymarket Best Bid Bot

A Python bot that places the highest bid on Polymarket prediction markets. Targets low-probability outcomes and bids one tick above the current best bid.

## Features

- Places GTC (Good Till Cancelled) limit buy orders
- Automatically calculates optimal bid (best bid + tick size)
- Respects configurable maximum price threshold
- Dry-run mode for safe testing
- Market discovery helpers to find low-price opportunities

## Requirements

- Python 3.11+
- Polymarket account with funds deposited
- Private key and funder address from your Polymarket wallet

## Installation

```bash
# Clone or navigate to the project
cd polymarket-bot

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
POLYMARKET_PRIVATE_KEY=0xyour_private_key_here
POLYMARKET_FUNDER_ADDRESS=0xyour_funder_address_here
MAX_BID_PRICE=0.05
ORDER_SIZE=5.0
DRY_RUN=true
```

### Getting Your Credentials

**Private Key:**
1. Open MetaMask
2. Click three dots menu > Account Details > Export Private Key
3. Enter password and copy the key

**Funder Address:**
1. Go to [polymarket.com](https://polymarket.com)
2. Click your profile/wallet
3. Find your deposit address (this is your Polymarket proxy wallet)

## Usage

### Basic Usage (Dry Run)

```bash
python bot.py --token-id <TOKEN_ID>
```

### Place Real Order

```bash
python bot.py --token-id <TOKEN_ID> --no-dry-run
```

### Custom Settings

```bash
python bot.py --token-id <TOKEN_ID> --max-price 0.03 --size 100 --no-dry-run
```

### Command Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--token-id` | Yes | - | Token ID of the market outcome |
| `--dry-run` | No | true | Only log, don't place orders |
| `--no-dry-run` | No | - | Place real orders |
| `--max-price` | No | 0.05 | Maximum bid price in dollars |
| `--size` | No | 5.0 | Number of shares to order |

## Finding Markets

### Using the Helper

```python
from helpers.markets import find_low_price_markets, display_market

# Find outcomes priced at 5 cents or less
results = find_low_price_markets(max_price=0.05, limit=50)

for r in results:
    print(f"{r['question']}")
    print(f"  Outcome: {r['outcome']}")
    print(f"  Price: ${r['price']}")
    print(f"  Token ID: {r['token_id']}")
```

### Search Markets

```python
from helpers.markets import search_markets, parse_market_tokens

markets = search_markets(query="recession", limit=20)
for m in markets:
    tokens = parse_market_tokens(m)
    print(m['question'])
    for t in tokens:
        print(f"  {t['outcome']}: ${t['price']}")
```

## Project Structure

```
polymarket-bot/
├── .env                 # Your credentials (gitignored)
├── .env.example         # Example configuration
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── config.py            # Configuration loading
├── bot.py               # Main bot script
├── helpers/
│   ├── __init__.py
│   ├── allowances.py    # Token allowance utilities
│   └── markets.py       # Market discovery helpers
└── README.md            # This file
```

## Important Notes

- **Minimum Order Value:** Polymarket requires orders to be at least $1 total value
- **Dry Run Default:** The bot runs in dry-run mode by default for safety
- **Token Allowances:** First-time users may need to approve token allowances via the Polymarket web interface

## API Reference

- **CLOB API:** `https://clob.polymarket.com`
- **Markets API:** `https://gamma-api.polymarket.com/markets`
- **Documentation:** [docs.polymarket.com](https://docs.polymarket.com)

## License

MIT
