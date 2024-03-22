import json

import requests
from ..config import SOLANA_ENDPOINT, SOL_PROGRAM_ID, HELIUS_URL


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


def fetch_asset(mint_address, id):
    url = HELIUS_URL  # Replace YOUR_URL_HERE with the actual URL you are making the request to.
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'jsonrpc': '2.0',
        'id': id,
        'method': 'getAsset',
        'params': {
            'id': mint_address  # Mint address of the NFT
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json().get('result')
    # print("Asset: ", result)
    return result


def fetch_assets_by_owner(wallet_address):
    url = HELIUS_URL
    headers = {
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        'jsonrpc': '2.0',
        'id': 'my-id',
        'method': 'getAssetsByOwner',
        'params': {
            'ownerAddress': wallet_address,
            'page': 1,  # Starts at 1
            'limit': 1000,
        },
    })

    response = requests.post(url, headers=headers, data=payload)
    result = response.json().get('result', {})
    items = result.get('items', [])

    # print("Assets by Owner: ", items)
    return items


def filter_assets_by_interface(wallet_address, interface_filter='V1_NFT'):
    assets = fetch_assets_by_owner(wallet_address)
    filtered_assets = [asset for asset in assets if asset.get('interface') == interface_filter]

    # # Print or process the filtered assets as needed
    # for asset in filtered_assets:
    #     print("Filtered Asset: ", asset)

    return filtered_assets


def extract_image_links(filtered_assets):
    image_links = []

    for asset in filtered_assets:
        # Extracting from the 'files' list if it exists
        if 'content' in asset and 'files' in asset['content']:
            files = asset['content']['files']
            for file in files:
                if 'uri' in file:  # Check if the 'uri' key exists
                    image_links.append(file['uri'])

        # Alternatively, extracting from a direct 'image' link if it exists
        if 'content' in asset and 'links' in asset['content'] and 'image' in asset['content']['links']:
            image_link = asset['content']['links']['image']
            if image_link not in image_links:  # Avoid duplicates
                image_links.append(image_link)

    return image_links


def fetch_assets_images_by_wallet_address(wallet_address, interface_filter='V1_NFT'):
    filtered_assets = filter_assets_by_interface(wallet_address, interface_filter)
    image_links = extract_image_links(filtered_assets)
    for link in image_links:
        print("Image URL:", link)
    return image_links

