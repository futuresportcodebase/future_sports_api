import json
import os
from pprint import pprint
from dotenv import load_dotenv
import requests


load_dotenv()


SOLANA_ENDPOINT = os.getenv("SOLANA_ENDPOINT")
SOL_PROGRAM_ID = os.getenv("SOL_PROGRAM_ID")
HELIUS_URL = os.getenv("HELIUS_URL")


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



def extract_image_links(filtered_assets):
    """
    Extracts image links from a list of filtered assets.

    Each asset is expected to have a 'content' key, which can contain either:
    - A 'files' list, with each file containing a 'uri' key for the image link.
    - A 'links' dictionary directly containing an 'image' key with the image URL.

    Parameters:
    - filtered_assets (list): A list of asset dictionaries to extract image links from.

    Returns:
    - list: A list of unique image URLs extracted from the assets.
    """
    image_links = []

    for asset in filtered_assets:
        # Extracting from the 'files' list if it exists
        if 'content' in asset and 'files' in asset['content']:
            files = asset['content']['files']
            for file in files:
                if 'uri' in file:  # Check if the 'uri' key exists
                    uri = file['uri']
                    if uri not in image_links:  # Avoid duplicates
                        image_links.append(uri)

        # Alternatively, extracting from a direct 'image' link if it exists
        elif 'content' in asset and 'links' in asset['content'] and 'image' in asset['content']['links']:
            image_link = asset['content']['links']['image']
            if image_link not in image_links:  # Avoid duplicates
                image_links.append(image_link)

    return image_links


def extract_image_links_by_symbol(nft_data):
    """
    Extracts image links from a list of NFT metadata and groups them by 'symbol'.

    Parameters:
    - nft_data (list): A list of dictionaries containing NFT metadata.

    Returns:
    - dict: A dictionary with 'symbol' as keys and lists of image URLs as values.
    """
    grouped_image_links = {}

    for nft in nft_data:
        # Extract the symbol from the NFT metadata
        symbol = nft['content'].get('metadata', {}).get('symbol', 'default')

        # Initialize the list for this symbol if it does not exist
        if symbol not in grouped_image_links:
            grouped_image_links[symbol] = []

        # Extract image link from 'links' -> 'image'
        if 'content' in nft and 'links' in nft['content'] and 'image' in nft['content']['links']:
            image_link = nft['content']['links']['image']
            if image_link not in grouped_image_links[symbol]:  # Avoid duplicates within the same symbol
                grouped_image_links[symbol].append(image_link)

        # Alternatively, extract image links from 'files' -> 'uri'
        elif 'content' in nft and 'files' in nft['content']:
            files = nft['content']['files']
            for file in files:
                if 'uri' in file:  # Check if the 'uri' key exists
                    uri = file['uri']
                    if uri not in grouped_image_links[symbol]:  # Avoid duplicates within the same symbol
                        grouped_image_links[symbol].append(uri)

    return grouped_image_links




def filter_assets_by_interface(wallet_address, interface_filter='V1_NFT'):
    assets = fetch_assets_by_owner(wallet_address)
    filtered_assets = [asset for asset in assets if asset.get('interface') == interface_filter]

    # # Print or process the filtered assets as needed
    # for asset in filtered_assets:
    #     print("Filtered Asset: ", asset)

    return filtered_assets


def fetch_filtered_assets_images(wallet_address, interface_filter='V1_NFT'):
    # Assuming filter_assets_by_interface is a function that filters assets based on the wallet address and interface
    filtered_assets = filter_assets_by_interface(wallet_address, interface_filter)
    image_links = extract_image_links(filtered_assets)

    # Print image URLs for debugging/logging purposes
    for link in image_links:
        print("Image URL:", link)

    # Returning a dictionary with the interface_filter as the key and the image links as its value
    return {interface_filter: image_links}


def fetch_all_assets_images(wallet_address):
    # Retrieves all assets associated with the wallet address
    all_assets = fetch_assets_by_owner(wallet_address)
    image_links_grouped = extract_image_links_by_symbol(all_assets)

    print(image_links_grouped)

    # Debugging: Print each image URL, grouped by 'group_value'
    for group_value, image_links in image_links_grouped.items():
        print(f"Group: {group_value}")
        for link in image_links:
            print("  Image URL:", link)

    # Returns a dictionary containing grouped image links
    return {"grouped_images": image_links_grouped}



def mint_compressed_nft(name: str, symbol: str, owner: str, description: str,
                        attributes: list, image_url: str, external_url: str,
                        seller_fee_basis_points: int, helius_url: str):
    """
    Mint a compressed NFT using the Helius protocol.

    Args:
        name (str): The name of the NFT.
        symbol (str): The symbol of the NFT.
        owner (str): The owner address of the NFT.
        description (str): The description of the NFT.
        attributes (list): List of dictionaries containing NFT attributes.
        image_url (str): The URL of the image associated with the NFT.
        external_url (str): The external URL associated with the NFT.
        seller_fee_basis_points (int): The seller fee basis points.
        helius_url (str): The URL of the Helius API.

    Returns:
        dict: The response JSON containing information about the minted NFT.
    """
    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        "jsonrpc": "2.0",
        "id": "helius-test",
        "method": "mintCompressedNft",
        "params": {
            "name": name,
            "symbol": symbol,
            "owner": owner,
            "description": description,
            "attributes": attributes,
            "imageUrl": image_url,
            "externalUrl": external_url,
            "sellerFeeBasisPoints": seller_fee_basis_points,
        }
    }

    response = requests.post(helius_url, headers=headers, data=json.dumps(payload))
    result = response.json()
    print('Minted asset: ', result['result']['assetId'])
    return result




