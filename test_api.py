"""Test CDISC API connection."""

import asyncio
import os

# Get API key from environment variable
api_key = os.environ.get("CDISC_API_KEY")
if not api_key:
    raise ValueError(
        "请设置环境变量 CDISC_API_KEY\n"
        "Windows: set CDISC_API_KEY=your-api-key\n"
        "Linux/Mac: export CDISC_API_KEY=your-api-key"
    )

from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.client import CDISCClient
from cdisc_mcp.cache import CacheManager


async def test_connection():
    config = CDISCConfig.from_env()
    cache = CacheManager(config.cache_dir, config.cache_ttl)
    client = CDISCClient(config, cache)

    print(f"API Key: {config.api_key[:8]}...")
    print(f"Base URL: {config.base_url}")
    print()

    # Test get_products
    print("Testing get_products()...")
    try:
        products = await client.get_products()
        print(f"✅ Success! Found {len(products)} products")
        if isinstance(products, list):
            for p in products[:5]:
                print(f"   - {p.get('name', 'Unknown')}")
        else:
            print(f"   Response type: {type(products)}")
            print(f"   Content: {products}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\nTesting get_about()...")
    try:
        about = await client.get_about()
        print(f"✅ Success!")
        print(f"   API Info: {about}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())