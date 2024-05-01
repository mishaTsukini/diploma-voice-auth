import time
import jwt

service_account_id = "ajen0sn2koecfbv1jd8v"
key_id = "aje4refq6ho8lrl2nbo0" # ID of the Key resource belonging to the service account.

with open("private.key", 'r') as private:
  private_key = private.read() # Reading the private key from the file.

now = int(time.time())
payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360}

# JWT generation.
encoded_token = jwt.encode(
    payload,
    private_key,
    algorithm='PS256',
    headers={'kid': key_id})
print(encoded_token)
