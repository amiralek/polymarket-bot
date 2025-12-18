"""Market discovery helper for Polymarket."""

import json
import requests
from typing import Optional


GAMMA_API_URL = "https://gamma-api.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def parse_market_tokens(market: dict) -> list:
    """
    Parse token information from a market dictionary.

    The Gamma API returns outcomes, prices, and token IDs as JSON strings.
    This function parses them into a list of token dictionaries.

    Args:
        market: Market dictionary from the API

    Returns:
        List of token dictionaries with outcome, price, and token_id
    """
    tokens = []

    try:
        outcomes = json.loads(market.get("outcomes", "[]"))
        prices = json.loads(market.get("outcomePrices", "[]"))
        token_ids = json.loads(market.get("clobTokenIds", "[]"))

        for i, outcome in enumerate(outcomes):
            token = {
                "outcome": outcome,
                "price": float(prices[i]) if i < len(prices) else None,
                "token_id": token_ids[i] if i < len(token_ids) else None,
            }
            tokens.append(token)
    except (json.JSONDecodeError, ValueError, IndexError):
        pass

    return tokens


def search_markets(query: str = "", limit: int = 10, active: bool = True) -> list:
    """
    Search for markets using the Gamma API.

    Args:
        query: Search query string
        limit: Maximum number of results
        active: Only return active markets

    Returns:
        List of market dictionaries
    """
    url = f"{GAMMA_API_URL}/markets?_limit={limit}"
    if active:
        url += "&active=true&closed=false"

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            data = [m for m in data if query_lower in m.get("question", "").lower()]

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        return []


def get_market_info(condition_id: str) -> Optional[dict]:
    """
    Get detailed information about a specific market.

    Args:
        condition_id: The market's condition ID

    Returns:
        Market dictionary or None if not found
    """
    url = f"{GAMMA_API_URL}/markets/{condition_id}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Market not found: {condition_id}")
        else:
            print(f"HTTP error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market: {e}")
        return None


def display_market(market: dict) -> None:
    """
    Display market information in a readable format.

    Args:
        market: Market dictionary from the API
    """
    print("=" * 60)
    print(f"Question: {market.get('question', 'N/A')}")
    print(f"Condition ID: {market.get('conditionId', 'N/A')}")
    print()

    tokens = parse_market_tokens(market)
    if tokens:
        print("Outcomes:")
        for token in tokens:
            outcome = token.get("outcome", "Unknown")
            token_id = token.get("token_id", "N/A")
            price = token.get("price", "N/A")
            print(f"  {outcome}:")
            print(f"    Token ID: {token_id}")
            print(f"    Price: ${price}")

    print()
    print(f"Volume: ${market.get('volume', 'N/A')}")
    print(f"Liquidity: ${market.get('liquidity', 'N/A')}")
    print(f"End Date: {market.get('endDate', 'N/A')}")
    print("=" * 60)


def find_low_price_markets(max_price: float = 0.05, limit: int = 20) -> list:
    """
    Find markets with outcomes priced at or below a threshold.

    Args:
        max_price: Maximum price threshold
        limit: Maximum number of markets to fetch

    Returns:
        List of dictionaries with market/token info where token price <= max_price
    """
    markets = search_markets(limit=limit)
    results = []

    for market in markets:
        tokens = parse_market_tokens(market)
        for token in tokens:
            try:
                price = token.get("price")
                if price is not None and 0 < price <= max_price:
                    results.append({
                        "question": market.get("question"),
                        "outcome": token.get("outcome"),
                        "token_id": token.get("token_id"),
                        "price": price,
                        "condition_id": market.get("conditionId"),
                    })
            except (ValueError, TypeError):
                continue

    # Sort by price ascending
    results.sort(key=lambda x: x["price"])
    return results
