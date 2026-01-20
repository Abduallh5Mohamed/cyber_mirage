#!/bin/bash
# ===========================================
# Threat Map Performance Fix Script
# Run this in EC2 Instance Connect or CloudShell
# ===========================================

echo "🔧 Fixing Threat Map Performance..."

# Navigate to project
cd /home/ubuntu/cyber_mirage

# Backup original file
cp src/dashboard/streamlit_app.py src/dashboard/streamlit_app.py.backup

# Download the fixed version from GitHub Gist or paste it directly
# For now, we'll use sed to make the key changes

# 1. Add caching function after GEO_CACHE = {}
sed -i '/^GEO_CACHE = {}$/a\
\
# Persistent geolocation cache using Redis\
def get_redis_geo_cache():\
    """Get Redis connection for geo caching."""\
    try:\
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, socket_timeout=1, decode_responses=True)\
        r.ping()\
        return r\
    except:\
        return None\
\
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour\
def get_cached_geolocation(ip):\
    """Get geolocation with multi-layer caching."""\
    global GEO_CACHE\
    if ip in GEO_CACHE:\
        return GEO_CACHE[ip]\
    redis_client = get_redis_geo_cache()\
    if redis_client:\
        try:\
            cached = redis_client.get(f"geo:{ip}")\
            if cached:\
                import json\
                geo = json.loads(cached)\
                GEO_CACHE[ip] = geo\
                return geo\
        except:\
            pass\
    geo = get_ip_geolocation(ip)\
    GEO_CACHE[ip] = geo\
    if redis_client and geo.get("lat", 0) != 0:\
        try:\
            import json\
            redis_client.setex(f"geo:{ip}", 86400, json.dumps(geo))\
        except:\
            pass\
    return geo' src/dashboard/streamlit_app.py

# 2. Change the limit from 1000 to 200
sed -i 's/fetch_real_attacks(1000)/fetch_real_attacks(200)/g' src/dashboard/streamlit_app.py

# 3. Change get_ip_geolocation to get_cached_geolocation in render_threat_map
sed -i 's/geo = get_ip_geolocation(ip)/geo = get_cached_geolocation(ip)/g' src/dashboard/streamlit_app.py

# Restart the dashboard
echo "🔄 Restarting Dashboard..."
docker compose restart dashboard || docker-compose restart dashboard

echo "✅ Done! Dashboard should be faster now."
echo "⏳ Wait 30 seconds for the container to fully restart..."
