import requests

SOLANA_ENDPOINT = 'https://api.devnet.solana.com'
SOL_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'

def send_solana_request(payload):
    """
    Sends a request to the Solana JSON-RPC API with the given payload.
    """
    response = requests.post(SOLANA_ENDPOINT, json=payload)
    return response.json()

def check_wallet_owns_nft(wallet_address, nft_mint_address):
    """
    Checks if the specified wallet owns the NFT with the given mint address.
    """
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getTokenAccountsByOwner',
        'params': [
            wallet_address,
            {'mint': nft_mint_address},
            {'encoding': 'jsonParsed'}
        ]
    }
    response_json = send_solana_request(payload)

    # Check if the wallet owns the NFT
    if response_json['result']['value']:
        print("The wallet owns the NFT.")
        return True
    else:
        print("The wallet does not own the NFT.")
        return False

def get_all_token_accounts(wallet_address):
    """
    Retrieves all token accounts associated with the specified wallet.
    """
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getTokenAccountsByOwner',
        'params': [
            wallet_address,
            {'programId': SOL_PROGRAM_ID},
            {'encoding': 'jsonParsed'}
        ]
    }
    response_json = send_solana_request(payload)
    print(response_json)
    return response_json

# Example usage
SOL_WALLET = 'AZwvt68TJMVy2v9BEBob1LLkXurcVdxYLKaqpvTo2MYg'
NFT_MINT_ADDRESS = 'qHCud2QNugFhwq5kFRgdDJAfAKT3ezD9pGmsbY5q2Gj'

# Check if the wallet owns a specific NFT
check_wallet_owns_nft(SOL_WALLET, NFT_MINT_ADDRESS)

# Get all token accounts associated with the wallet
get_all_token_accounts(SOL_WALLET)
