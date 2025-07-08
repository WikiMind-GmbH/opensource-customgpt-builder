
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas.common import CommonResponse


app = FastAPI(
    root_path="/api",  # Explanation: While the proxy strips the /api prefix, we stil need this here: https://fastapi.tiangolo.com/advanced/behind-a-proxy/#proxy-with-a-stripped-path-prefix
)

origins = [
    f"https://localhost",
]

# Add the CORSMiddleware to your application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,  # Allows cookies, authorization headers, etc.
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/test_first", operation_id="test")
async def test_first(req: CommonResponse):
    return {"message": "This is the first test endpoint"}
