from cc import writeCcs

from configuration import apiKey
from configuration import apiRedirectUri
from api import Api

# todo
# infinite loop, check written contracts if we need to sell them

# writeCcs()


api = Api(apiKey,apiRedirectUri)

api.connect()
