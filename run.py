import uvicorn

if __name__ == "__main__":
    # Run uvicorn, pointing to the app.main module
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)