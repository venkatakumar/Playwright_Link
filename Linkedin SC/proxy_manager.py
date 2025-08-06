"""
Proxy Management Utilities for Anonymous LinkedIn Scraping
"""
import asyncio
import aiohttp
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class ProxyValidator:
    """Validate and test proxy servers"""
    
    def __init__(self):
        self.test_url = "https://httpbin.org/ip"
        self.timeout = 10
    
    async def test_proxy(self, proxy: str) -> Dict:
        """Test a single proxy"""
        result = {
            'proxy': proxy,
            'working': False,
            'response_time': None,
            'ip': None,
            'error': None
        }
        
        try:
            start_time = datetime.now()
            
            # Format proxy for aiohttp
            proxy_url = proxy if proxy.startswith('http') else f'http://{proxy}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.test_url,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result['working'] = True
                        result['ip'] = data.get('origin', 'Unknown')
                        result['response_time'] = (datetime.now() - start_time).total_seconds()
                    else:
                        result['error'] = f'HTTP {response.status}'
                        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def test_proxy_list(self, proxies: List[str]) -> List[Dict]:
        """Test multiple proxies concurrently"""
        print(f"🔍 Testing {len(proxies)} proxies...")
        
        tasks = [self.test_proxy(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        working_proxies = []
        for result in results:
            if isinstance(result, dict):
                if result['working']:
                    working_proxies.append(result)
                    print(f"✅ {result['proxy']} - {result['response_time']:.2f}s - IP: {result['ip']}")
                else:
                    print(f"❌ {result['proxy']} - {result['error']}")
        
        print(f"\n📊 {len(working_proxies)}/{len(proxies)} proxies are working")
        return working_proxies


class FreeProxyProvider:
    """Get free proxy lists from various sources"""
    
    FREE_PROXY_APIS = [
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]
    
    async def fetch_free_proxies(self) -> List[str]:
        """Fetch free proxies from various sources"""
        all_proxies = set()
        
        async with aiohttp.ClientSession() as session:
            for api_url in self.FREE_PROXY_APIS:
                try:
                    print(f"🔄 Fetching proxies from {api_url.split('/')[2]}...")
                    async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            text = await response.text()
                            
                            # Parse different formats
                            lines = text.strip().split('\n')
                            for line in lines:
                                line = line.strip()
                                if ':' in line and len(line.split(':')) == 2:
                                    try:
                                        ip, port = line.split(':')
                                        if self.is_valid_ip(ip) and port.isdigit():
                                            all_proxies.add(f"{ip}:{port}")
                                    except:
                                        continue
                                        
                except Exception as e:
                    print(f"⚠️ Failed to fetch from {api_url}: {e}")
        
        proxy_list = list(all_proxies)
        print(f"📥 Collected {len(proxy_list)} unique proxies")
        return proxy_list
    
    def is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False


async def setup_proxy_rotation():
    """Setup proxy rotation for anonymous scraping"""
    print("🔧 Setting up proxy rotation...")
    
    # Get free proxies
    provider = FreeProxyProvider()
    proxies = await provider.fetch_free_proxies()
    
    if not proxies:
        print("❌ No proxies found")
        return []
    
    # Test proxies
    validator = ProxyValidator()
    working_proxies = await validator.test_proxy_list(proxies[:50])  # Test first 50
    
    # Save working proxies
    if working_proxies:
        proxy_list = [p['proxy'] for p in working_proxies]
        
        # Save to file
        with open('working_proxies.txt', 'w') as f:
            f.write('\n'.join(proxy_list))
        
        print(f"💾 Saved {len(proxy_list)} working proxies to working_proxies.txt")
        
        # Update .env file
        env_line = f"PROXY_LIST={','.join(proxy_list[:10])}"  # Use top 10
        print(f"\n📝 Add this to your .env file:")
        print(env_line)
        
        return proxy_list
    else:
        print("❌ No working proxies found")
        return []


if __name__ == "__main__":
    asyncio.run(setup_proxy_rotation())
