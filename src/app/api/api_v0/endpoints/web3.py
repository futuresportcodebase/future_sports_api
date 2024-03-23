from fastapi import APIRouter, Query
from ..functions.web3_functions import fetch_assets_by_owner, fetch_filtered_assets_images
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

@router.get("/get_filtered_images")
async def get_filtered_assets_images(wallet_address: str = Query(..., description="Solana Wallet Address"),
                            interface_filter: str = Query('V1_NFT', description="Interface Filter")):
    """
    Get image links of assets by wallet address filtered by interface.
    """
    image_links = fetch_filtered_assets_images(wallet_address, interface_filter)
    return {"image_links": image_links}



# Example usage
SOL_WALLET = 'AZwvt68TJMVy2v9BEBob1LLkXurcVdxYLKaqpvTo2MYg'
NFT_MINT_ADDRESS = 'qHCud2QNugFhwq5kFRgdDJAfAKT3ezD9pGmsbY5q2Gj'




