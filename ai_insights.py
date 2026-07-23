import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os
import sys

# Windows' default console can't print emoji/some symbols — force UTF-8 so it can
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

# --- Load the secret key from .env (never hard-coded in the file) ---
load_dotenv()                          # reads the .env file sitting next to this script
api_key = os.getenv("GROQ_API_KEY")    # pulls the GROQ_API_KEY value out of it

# --- Step 1: Build the facts table the AI will read ---
# For each loan grade (A-G), we want three facts:
#   1. how many loans        -> .size()
#   2. the default rate       -> mean of the 0/1 "defaulted" column
#   3. total money lent       -> sum of loan_amnt
df = pd.read_csv('loan_clean.csv')
facts = df.groupby('grade').agg(
    loans=('defaulted', 'size'),
    default_rate=('defaulted', 'mean'),
    total_lent=('loan_amnt', 'sum'),
)
facts['default_rate'] = (facts['default_rate'] * 100).round(2)
print(facts)

# --- Step 2: Turn the facts into an AI insight ---
def generate_insight(facts_table):
    """Send the facts to Groq's AI and get back an analyst-style summary."""
    client = Groq(api_key=api_key)     # "hire the waiter" — connect using your key

    # The order we hand the AI: who it is, the data, and exactly what we want back
    prompt = f"""You are a senior credit-risk analyst.
Here is default-rate data by loan grade (A = safest, G = riskiest):

{facts_table.to_string()}

Write a 3-sentence executive insight:
1. State the single most important risk finding, with the numbers.
2. Quantify the money exposed.
3. Give one concrete recommendation.
Be direct and specific. No preamble."""

    # Send the order to the AI model and wait for the reply
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",           # the AI model doing the thinking
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content     # dig the text answer out of the reply

# --- Step 3: Run it and print the insight ---
print("\n🤖 AI Root-Cause Insight:\n")
print(generate_insight(facts))
