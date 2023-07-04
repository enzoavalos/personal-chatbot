import yaml
import requests
import pathlib

path = pathlib.Path().resolve()

# Primero se debe poner el nuevo link de ngrok, cuando se ejecute el actions se va a reiniciar el hook, junto con sus updates
def resetUpdates():
    with open((f"{path}/credentials.yml")) as f:
        all_info = yaml.safe_load(f)
        url_ngrok = all_info["telegram"]["webhook_url"]
        bot_token = all_info["telegram"]["access_token"]
    
    getUrl = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    params_webhook = {
        "url": url_ngrok,
        "drop_pending_updates": True
    }
    r = requests.get(url = getUrl, params = params_webhook)

resetUpdates()