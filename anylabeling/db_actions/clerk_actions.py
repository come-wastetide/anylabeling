# I want to connect with my identification provider : clerk
import os
import dotenv

dotenv.load_dotenv()

CLERK_SECRET = os.getenv("CLERK_SECRET")
CLERK_PUBLISHABLE = os.getenv("CLERK_PUBLISHABLE")

import requests

'''def verify_token(token):
    api_key = "your_clerk_api_key"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.clerk.dev/v1/tokens/verify",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()  # Verified token data
    else:
        print(response.json())
        raise ValueError("Invalid token")
    
import asyncio
from clerk_backend_api import Clerk

async def main():
    sdk = Clerk(
        bearer_auth=CLERK_SECRET,
    )
    res = await sdk.email_addresses.get_async(
        email_address_id="email_address_id_example"
    )
    if res is not None:
        # handle response
        pass

asyncio.run(main())
'''
# Synchronous Example
from clerk_backend_api import Clerk

with Clerk(
    bearer_auth="CLERK_SECRET",
) as s:
    res = s.organizations.get(
        organization_id="org_2jLn0za5IpTINBIcnkCpmlyzlIi"
    )

    if res is not None:
        # handle response
        pass