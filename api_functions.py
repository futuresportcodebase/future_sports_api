import requests

SOLANA_ENDPOINT = 'https://api.devnet.solana.com'
SOL_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
SOL_WALLET = 'AZwvt68TJMVy2v9BEBob1LLkXurcVdxYLKaqpvTo2MYg'

payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'getTokenAccountsByOwner',
    'params': [
        SOL_WALLET,
        {
            'programId': SOL_PROGRAM_ID
        },
        {
            'encoding': 'jsonParsed'
        }
    ]
}

response = requests.post(SOLANA_ENDPOINT, json=payload)
response_json = response.json()

print(response_json)
