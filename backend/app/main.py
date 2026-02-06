# Entry point for DocuGuard backend
# Import FastAPI class from the fastapi library
# FastAPI is the framework we use to build our backend APIs
from fastapi import FastAPI

# Create an instance of the FastAPI application
# This 'app' object represents our backend server
app = FastAPI(
    title="DocuGuard",                  # Name of the application
    description="HR Policy Compliance Analyzer Backend",
    version="0.1.0"
)

# This is a simple GET API endpoint
# Endpoint URL: /health
# Purpose: Check if the backend server is running correctly
@app.get("/health")
def health_check():
    """
    Health check endpoint.

    This endpoint is used to verify that:
    - The FastAPI server is running
    - The application is reachable

    It returns a simple JSON response.
    """

    # Return a JSON response
    # This will be shown in the browser or API client
    return {
        "status": "DocuGuard is running"
    }

