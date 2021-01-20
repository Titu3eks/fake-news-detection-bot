# fake-news-detector-bot

## Create a config:
``config.txt``
```bash
[TELEGRAM]
token = <token>
```
## Get started
```python
pip install -r requirements.txt
python bot.py
```
## example docker-compose
```bash
version: '3.8'
    
services:
    bot:
        build: .
        container_name: bot
        hostname: bot
        environment:
            - token=<token>
            - threshold=0.9
```