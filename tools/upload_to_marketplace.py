#!/usr/bin/env python3
"""
CLI Tool to Upload Agents to Arli Marketplace
Usage: python upload_to_marketplace.py <agent_file.json> --price 100
"""

import argparse
import json
import requests
import sys
from pathlib import Path
from typing import Optional


def upload_agent(
    file_path: str,
    price: float,
    description: Optional[str] = None,
    wallet: Optional[str] = None,
    tags: Optional[str] = None,
    api_url: str = "http://localhost:8000"
) -> dict:
    """Upload agent to marketplace"""
    
    # Validate file
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    # Load and validate JSON
    try:
        with open(file_path, 'r') as f:
            agent_data = json.load(f)
        print(f"✅ Loaded agent: {agent_data.get('name', 'Unknown')}")
        print(f"   Level: {agent_data.get('level', 1)} ({agent_data.get('tier', 'COMMON')})")
        print(f"   Estimated value: ${agent_data.get('estimated_market_value', 0)}")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON file")
        sys.exit(1)
    
    # Prepare upload
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'application/json')}
        data = {
            'price': price,
            'description': description or '',
            'seller_wallet': wallet or '',
            'tags': tags or ''
        }
        
        print(f"\n📤 Uploading to marketplace...")
        print(f"   Price: ${price}")
        
        try:
            response = requests.post(
                f"{api_url}/marketplace/upload",
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            print("❌ Error: Cannot connect to marketplace API")
            print(f"   Make sure API is running at {api_url}")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("❌ Error: Upload timeout")
            sys.exit(1)


def upload_bundle(
    file_path: str,
    price: float,
    wallet: Optional[str] = None,
    api_url: str = "http://localhost:8000"
) -> dict:
    """Upload agent bundle to marketplace"""
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    # Validate bundle
    try:
        with open(file_path, 'r') as f:
            bundle_data = json.load(f)
        
        if "agents" not in bundle_data:
            print("❌ Error: Invalid bundle format (missing 'agents' key)")
            sys.exit(1)
        
        agent_count = len(bundle_data["agents"])
        print(f"✅ Loaded bundle with {agent_count} agents")
        
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON file")
        sys.exit(1)
    
    # Upload
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'application/json')}
        data = {
            'bundle_price': price,
            'seller_wallet': wallet or ''
        }
        
        print(f"\n📤 Uploading bundle...")
        print(f"   Bundle price: ${price}")
        print(f"   Individual value: ${sum(a.get('estimated_market_value', 0) for a in bundle_data['agents']):.2f}")
        
        try:
            response = requests.post(
                f"{api_url}/marketplace/upload/bundle",
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            print("❌ Error: Cannot connect to marketplace API")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Upload agents to Arli Marketplace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload single agent
  python upload_to_marketplace.py arli_export_my_agent.json --price 150

  # Upload with description and wallet
  python upload_to_marketplace.py agent.json --price 200 \\
      --description "Elite trading bot" \\
      --wallet rdmx6-jaaaa-aaaaa-aaadq-cai

  # Upload bundle
  python upload_to_marketplace.py bundle.json --price 500 --bundle
        """
    )
    
    parser.add_argument(
        "file",
        help="Path to agent JSON file (from export)"
    )
    
    parser.add_argument(
        "--price",
        type=float,
        required=True,
        help="Sale price in USD"
    )
    
    parser.add_argument(
        "--description",
        "-d",
        help="Listing description"
    )
    
    parser.add_argument(
        "--wallet",
        "-w",
        help="Your ICP wallet address for receiving payments"
    )
    
    parser.add_argument(
        "--tags",
        "-t",
        help="Comma-separated tags (e.g., trading,crypto,api)"
    )
    
    parser.add_argument(
        "--bundle",
        action="store_true",
        help="Upload as a bundle (multiple agents)"
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Marketplace API URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Arli Marketplace Uploader\n")
    
    # Upload
    if args.bundle:
        result = upload_bundle(
            args.file,
            args.price,
            args.wallet,
            args.api_url
        )
    else:
        result = upload_agent(
            args.file,
            args.price,
            args.description,
            args.wallet,
            args.tags,
            args.api_url
        )
    
    # Display result
    if result.get("success"):
        print("\n" + "="*50)
        print("✅ Upload successful!")
        print("="*50)
        
        if "bundle_id" in result:
            print(f"Bundle ID: {result['bundle_id']}")
            print(f"Agents: {result.get('agent_count', 'N/A')}")
        else:
            print(f"Listing ID: {result['agent_id']}")
            
        print(f"Listing URL: {result.get('listing_url', 'N/A')}")
        
        if result.get('estimated_value'):
            print(f"Estimated value: ${result['estimated_value']:.2f}")
        
        print(f"\nPrice: ${args.price}")
        
        if args.wallet:
            print(f"Seller wallet: {args.wallet}")
        
        print("\n🎉 Your agent is now on the marketplace!")
        print(f"   View at: {args.api_url}{result.get('listing_url', '')}")
        
    else:
        print("\n❌ Upload failed")
        print(f"Error: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
