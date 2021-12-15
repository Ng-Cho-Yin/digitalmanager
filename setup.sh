mkdir -p ~/.streamlit/
echo "[general]  
email = \"cyngba@connect.ust.hk\""  > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false"  >> ~/.streamlit/config.toml
