from whatsapp_api_client_python import API
from auth import config as app_config

gist = API.GreenAPI(app_config.Config.AUTH_WHATSUP_INSTANCE_ID, app_config.Config.AUTH_WHATSUP_INSTANCE_TOKEN)
