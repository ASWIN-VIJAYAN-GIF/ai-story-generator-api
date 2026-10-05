import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware      # NEW
from fastapi.responses import FileResponse              # NEW
from fastapi.staticfiles import StaticFiles             # NEW
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# 1. Force load the environment variables from your .env lockbox
load_dotenv()

# 2. Start our FastAPI server application
app = FastAPI()

# NEW: allow a frontend opened from another origin (e.g. a file or another port) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Create a helper function that reads the key right when a user asks for a story
def get_gemini_client():
    # Fetch the key we put in our .env file
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

# 4. Define what data our user needs to send us (the topic text)
class StoryRequest(BaseModel):
    topic: str

# 5. Create our API gate
@app.post("/generate-story")
def tell_a_story(request: StoryRequest):
    # Call our helper function to wake up Gemini with our key
    client = get_gemini_client()

    # Write down what we want Gemini to do
    prompt = f"Write a funny, creative short story for a kid about: {request.topic}. Keep it under 4 sentences."

    # Ask Gemini to generate the text
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )

    # Send the final text back to the browser screen
    return {"story": response.text}

# NEW: serve the frontend. "/" returns the page, "/static/..." serves any extra files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))
