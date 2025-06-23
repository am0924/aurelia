import jwt
import datetime
import argparse
from dotenv import load_dotenv
import os


def generate(role: str) -> str:
  load_dotenv()
  SECRET_KEY = os.getenv("PROMPTQL_SECRET_KEY")
 
  # Data to include in the payload
  payload = {
     "iat": datetime.datetime.now(),  # issued at
     "exp": datetime.datetime.now() + datetime.timedelta(hours=1),  # expires in 1 hour
     "claims.jwt.hasura.io": {
        "x-hasura-default-role": role,
        "x-hasura-allowed-roles": [role],
        }
  }
  # Generate JWT
  token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
  print("JWT Token: " + str(token))
  return token

def main():
    parser = argparse.ArgumentParser(description="Generate a JWT for PromptQL")
    parser.add_argument("role", type=str, help="Role to embed in the JWT")
    args = parser.parse_args()
    generate(args.role)


if __name__ == "__main__":
    main()