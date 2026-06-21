import os
from dotenv import load_dotenv
load_dotenv()

MODEL = "gemini/gemini-1.5-flash"        
TOC_CHECK_PAGES = 20           # how many pages to scan for TOC
MAX_PAGES_PER_NODE = 50        # when to split a node further