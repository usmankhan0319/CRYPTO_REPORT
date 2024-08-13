from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from crypto import Crypto_Analysis

            
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all domains. For production, specify actual domains.
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods.
    allow_headers=["*"],
)


@app.get("/analyze/{coin_name}")
async def analyze_crypto(coin_name: str):
    ca = Crypto_Analysis()
    ca.fundamental_analysis(coin_name)
    ca.technical_analysis()
    ca.create_sma_chart(coin_name)
    ca.moving_average()
    ca.sentiment_analysis(coin_name)
    ca.create_line_chart(coin_name)
    ca.closing_chart_analysis()
    ca.generate_summary()

    # Read the summary.json file and return its contents as a dictionary
    with open("summary.json", "r") as json_file:
        summary_data = json.load(json_file)

    if summary_data is None:
        return {"status": False , "data": None}
    else:
        return {"status": True , "data": summary_data}


def main():
    """Entry point"""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()