"""Token allowance helper for Polymarket trading."""

from py_clob_client.client import ClobClient


# Contract addresses on Polygon
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
CONDITIONAL_TOKENS_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

# Exchange contracts that need approval
EXCHANGE_CONTRACTS = {
    "Main Exchange": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "Neg Risk Exchange": "0xC5d563A36AE78145C45a50134d48A1215220f80a",
    "Neg Risk Adapter": "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",
}


def check_allowances(client: ClobClient) -> dict:
    """
    Check if token allowances are set for trading.

    Note: This is a placeholder - the py-clob-client doesn't expose
    allowance checking directly. Users should verify via PolygonScan.

    Args:
        client: Initialized ClobClient

    Returns:
        Dictionary with allowance status
    """
    print("=== Token Allowances ===")
    print("To trade on Polymarket, you need to approve the following contracts:")
    print()
    print("USDC Token:", USDC_ADDRESS)
    print("Conditional Tokens:", CONDITIONAL_TOKENS_ADDRESS)
    print()
    print("Contracts to approve:")
    for name, address in EXCHANGE_CONTRACTS.items():
        print(f"  {name}: {address}")
    print()
    print("Check your allowances on PolygonScan:")
    print(f"  https://polygonscan.com/token/{USDC_ADDRESS}#readContract")
    print()

    return {
        "usdc": USDC_ADDRESS,
        "conditional_tokens": CONDITIONAL_TOKENS_ADDRESS,
        "exchanges": EXCHANGE_CONTRACTS,
    }


def set_allowances(client: ClobClient) -> bool:
    """
    Set token allowances for trading.

    Note: The py-clob-client handles allowances automatically when using
    browser wallet proxy authentication. This function is provided for
    reference and manual setup scenarios.

    Args:
        client: Initialized ClobClient

    Returns:
        True if successful
    """
    print("=== Setting Token Allowances ===")
    print()
    print("When using browser wallet proxy authentication (signature_type=2),")
    print("the py-clob-client typically handles allowances automatically.")
    print()
    print("If you need to set allowances manually:")
    print("1. Go to PolygonScan")
    print("2. Connect your wallet")
    print("3. Approve each exchange contract for USDC and Conditional Tokens")
    print()
    print("Alternatively, use the Polymarket web interface to make a small trade,")
    print("which will prompt you to approve the necessary contracts.")

    return True
