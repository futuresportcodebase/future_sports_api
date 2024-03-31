from fastapi import APIRouter, Query, HTTPException

from ..config import HELIUS_URL
from ..functions.web3_functions import fetch_assets_by_owner, fetch_filtered_assets_images, mint_compressed_nft, fetch_all_assets_images
router = APIRouter(prefix='/web3', tags=["Web3"])

@router.get("/")
async def root():
    return {"message": "Welcome to the Web3 API. Use the endpoints to interact with Solana wallets and NFTs."}

# @router.get("/nft-ownership")
# async def check_nft_ownership_endpoint(sol_wallet: str = Query(..., description="Solana Wallet Address"),
#                                        nft_mint_address: str = Query(..., description="NFT Mint Address")):
#     """
#     Check if the specified Solana wallet owns the given NFT.
#     """
#     return check_nft_ownership(sol_wallet, nft_mint_address)

@router.get("/token-accounts")
async def get_all_token_accounts_endpoint(sol_wallet: str = Query(..., description="Solana Wallet Address")):
    """
    Retrieve all token accounts associated with the specified Solana wallet.
    """
    return fetch_assets_by_owner(sol_wallet)

# @router.get("/get_filtered_images")
# async def get_filtered_assets_images(wallet_address: str = Query(..., description="Solana Wallet Address"),
#                             interface_filter: str = Query('V1_NFT', description="Interface Filter")):
#     """
#     Get image links of assets by wallet address filtered by interface.
#     """
#     image_links = fetch_filtered_assets_images(wallet_address, interface_filter)
#     return {"image_links": image_links}

@router.get("/get_wallet_images")
async def get_wallets_images(wallet_address: str = Query(..., description="Solana Wallet Address"),
                            ):
    """
    Get image links of assets by wallet address filtered by interface.
    """
    image_links = fetch_all_assets_images(wallet_address)
    return image_links


@router.post("/mint_compressed_nft")
async def mint_compressed_nft_endpoint(name: str = "APOCALYPTIC_ACROPOLIS", symbol: str = "TESTBKGRD",
                                       owner: str = "3GgkadRc4rGht3EkUDZwRb4TSuFayKGPyyeCQCap9XLn",
                                       description: str = "The ultimate Backgrounds",
                                       attributes=None,
                                       image_url: str = "https://infinityforgetest.s3.amazonaws.com/cardbackgrounds/BallStars-Baseball-Edition-0_APOCALYPTIC_ACROPOLIS_base_t5.png",
                                       external_url: str = "https://infinityforgetest.s3.amazonaws.com/cardbackgrounds/BallStars-Baseball-Edition-0_APOCALYPTIC_ACROPOLIS_base_t5.png",
                                       seller_fee_basis_points: int = 6900,
                                       helius_url: str = HELIUS_URL):
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
    if attributes is None:
        attributes = [
            {"trait_type": "Type", "value": "Legendary"},
            # {"trait_type": "Power", "value": "Infinite"},
            # {"trait_type": "Element", "value": "Dark"},
            {"trait_type": "Rarity", "value": "Mythical"}
        ]
    try:
        nft_info = mint_compressed_nft(name, symbol, owner, description,
                                        attributes, image_url, external_url,
                                        seller_fee_basis_points, helius_url)
        return {"asset_info": nft_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Example usage
# SOL_WALLET = 'AZwvt68TJMVy2v9BEBob1LLkXurcVdxYLKaqpvTo2MYg'
# NFT_MINT_ADDRESS = 'qHCud2QNugFhwq5kFRgdDJAfAKT3ezD9pGmsbY5q2Gj'




