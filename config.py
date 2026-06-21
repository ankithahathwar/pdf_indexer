from dotenv import load_dotenv
load_dotenv()

MODEL = "groq/llama-3.3-70b-versatile"
TOC_CHECK_PAGES = 20
MAX_PAGES_PER_NODE = 50
MAX_TOKEN_NUM_EACH_NODE = 100000