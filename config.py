from dotenv import load_dotenv
import os

load_dotenv(".env")


load_dotenv(".env.requirements")

# load server requirements
SERVER = os.getenv("SERVER")
PORT = os.getenv("PORT")
ADDRESS = os.getenv("ADDRESS")
PASSWORD = os.getenv("PASSWORD")

