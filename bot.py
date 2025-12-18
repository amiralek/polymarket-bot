#!/usr/bin/env python3
"""
Polymarket Best Bid Bot

A simple bot that places the highest bid on a specified Polymarket prediction market.
Targets low-probability outcomes (<=5 cents) and bids one tick above the current best bid.
"""

import argparse
import sys
from decimal import Decimal, ROUND_DOWN

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

from config import Config


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Place the best bid on a Polymarket market",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - just show what would happen
  python bot.py --token-id 12345...

  # Place a real order
  python bot.py --token-id 12345... --no-dry-run

  # Custom max price and size
  python bot.py --token-id 12345... --max-price 0.03 --size 10
        """,
    )

    parser.add_argument(
        "--token-id",
        required=True,
        help="The token ID of the market outcome to bid on",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Run in dry-run mode (only log, don't place orders)",
    )

    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry-run mode and place real orders",
    )

    parser.add_argument(
        "--max-price",
        type=float,
        default=None,
        help=f"Maximum bid price in dollars (default: {Config.MAX_BID_PRICE})",
    )

    parser.add_argument(
        "--size",
        type=float,
        default=None,
        help=f"Number of shares to order (default: {Config.ORDER_SIZE})",
    )

    return parser.parse_args()


def initialize_client() -> ClobClient:
    """Initialize and authenticate the CLOB client."""
    print("Initializing Polymarket client...")

    client = ClobClient(
        host=Config.HOST,
        key=Config.PRIVATE_KEY,
        chain_id=Config.CHAIN_ID,
        signature_type=2,  # Browser wallet proxy
        funder=Config.FUNDER_ADDRESS,
    )

    # Derive or create API credentials
    print("Authenticating...")
    client.set_api_creds(client.create_or_derive_api_creds())
    print("Authentication successful!")

    return client


def get_best_bid(client: ClobClient, token_id: str) -> float:
    """
    Fetch the order book and return the best bid price.

    Args:
        client: Initialized ClobClient
        token_id: The token ID to get order book for

    Returns:
        Best bid price, or 0 if no bids exist
    """
    print(f"Fetching order book for token: {token_id[:20]}...")

    order_book = client.get_order_book(token_id)

    if not order_book.bids:
        print("No existing bids on this market")
        return 0.0

    best_bid = max(float(bid.price) for bid in order_book.bids)
    print(f"Current best bid: ${best_bid:.4f}")

    return best_bid


def get_tick_size(client: ClobClient, token_id: str) -> Decimal:
    """
    Get the tick size for a token.

    Args:
        client: Initialized ClobClient
        token_id: The token ID

    Returns:
        Tick size as Decimal
    """
    tick_size_str = client.get_tick_size(token_id)
    tick_size = Decimal(tick_size_str)
    print(f"Tick size: ${tick_size}")
    return tick_size


def calculate_new_bid(best_bid: float, tick_size: Decimal, max_price: float) -> float | None:
    """
    Calculate the new bid price (one tick above best bid).

    Args:
        best_bid: Current best bid price
        tick_size: Minimum price increment
        max_price: Maximum allowed bid price

    Returns:
        New bid price, or None if it would exceed max price
    """
    # Convert to Decimal for precise arithmetic
    best_bid_decimal = Decimal(str(best_bid))
    max_price_decimal = Decimal(str(max_price))

    # Calculate new bid (one tick above)
    new_bid = best_bid_decimal + tick_size

    # Round down to tick size precision
    precision = tick_size.as_tuple().exponent
    new_bid = new_bid.quantize(tick_size, rounding=ROUND_DOWN)

    print(f"Calculated new bid: ${new_bid}")

    # Check if new bid exceeds max price
    if new_bid > max_price_decimal:
        print(f"New bid ${new_bid} exceeds max price ${max_price}. Skipping.")
        return None

    # Check if best bid already at or above max
    if best_bid_decimal >= max_price_decimal:
        print(f"Best bid ${best_bid} already at or above max price ${max_price}. Skipping.")
        return None

    return float(new_bid)


def place_order(
    client: ClobClient,
    token_id: str,
    price: float,
    size: float,
    dry_run: bool,
) -> dict | None:
    """
    Place a GTC limit buy order.

    Args:
        client: Initialized ClobClient
        token_id: Token ID to buy
        price: Bid price
        size: Number of shares
        dry_run: If True, only log what would happen

    Returns:
        Order response dict, or None if dry run
    """
    print()
    print("=" * 50)

    if dry_run:
        print("[DRY RUN] Would place order:")
        print(f"  Token ID: {token_id[:30]}...")
        print(f"  Side: BUY")
        print(f"  Price: ${price:.4f}")
        print(f"  Size: {size} shares")
        print(f"  Type: GTC (Good Till Cancelled)")
        print("=" * 50)
        return None

    print("Placing REAL order:")
    print(f"  Token ID: {token_id[:30]}...")
    print(f"  Side: BUY")
    print(f"  Price: ${price:.4f}")
    print(f"  Size: {size} shares")
    print(f"  Type: GTC (Good Till Cancelled)")
    print("=" * 50)

    # Create the order
    order_args = OrderArgs(
        token_id=token_id,
        price=price,
        size=size,
        side=BUY,
    )

    # Sign and submit
    print("Signing order...")
    signed_order = client.create_order(order_args)

    print("Submitting order...")
    response = client.post_order(signed_order, OrderType.GTC)

    print()
    print("Order submitted successfully!")
    print(f"Response: {response}")

    return response


def main() -> int:
    """Main entry point."""
    print()
    print("=" * 50)
    print("  POLYMARKET BEST BID BOT")
    print("=" * 50)
    print()

    # Parse arguments
    args = parse_args()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1

    # Determine settings (CLI args override env vars)
    max_price = args.max_price if args.max_price is not None else Config.MAX_BID_PRICE
    order_size = args.size if args.size is not None else Config.ORDER_SIZE

    # Determine dry run mode
    if args.no_dry_run:
        dry_run = False
    elif args.dry_run:
        dry_run = True
    else:
        dry_run = Config.DRY_RUN

    # Display settings
    print("Settings:")
    print(f"  Token ID: {args.token_id[:30]}...")
    print(f"  Max Price: ${max_price}")
    print(f"  Order Size: {order_size} shares")
    print(f"  Dry Run: {dry_run}")
    print()

    if not dry_run:
        print("*** WARNING: DRY RUN IS DISABLED - REAL ORDERS WILL BE PLACED ***")
        print()

    try:
        # Initialize client
        client = initialize_client()
        print()

        # Get current best bid
        best_bid = get_best_bid(client, args.token_id)

        # Get tick size
        tick_size = get_tick_size(client, args.token_id)
        print()

        # Calculate new bid
        new_bid = calculate_new_bid(best_bid, tick_size, max_price)

        if new_bid is None:
            print()
            print("No order placed.")
            return 0

        # Place the order
        place_order(
            client=client,
            token_id=args.token_id,
            price=new_bid,
            size=order_size,
            dry_run=dry_run,
        )

        print()
        print("Bot execution complete.")
        return 0

    except Exception as e:
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
