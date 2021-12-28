from configuration import apiKey, apiRedirectUri
from api import Api

api = Api(apiKey, apiRedirectUri)

# Manual OAuth setup
api.setup()
