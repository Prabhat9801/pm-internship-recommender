# PM Internship Recommender

A full-stack web application that recommends personalized product management (PM) internships based on your education, skills, and location. Built with FastAPI (backend) and React (frontend), it uses AI-powered embeddings for smart matching.

## Features
- **Personalized Recommendations:** Get internship matches tailored to your profile.
- **AI Embeddings:** Uses Google Generative AI embeddings for semantic matching.
- **Location & Skills Filtering:** Matches based on preferred location and skills.
- **Modern UI:** Simple, responsive React frontend.
- **FastAPI Backend:** RESTful API for recommendations.

## Tech Stack
- **Backend:** FastAPI, Python, LangChain, Google Generative AI, scikit-learn, numpy
- **Frontend:** React, Vite
- **Data:** JSON-based internship listings

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js & npm

### Backend Setup
1. Navigate to the backend folder:
   ```powershell
   cd backend
   ```
2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set up your `.env` file (for API keys, if needed).
4. Run the FastAPI server:
   ```powershell
   python app.py
   ```
   The API will be available at `http://127.0.0.1:8000`.

### Frontend Setup
1. Navigate to the frontend folder:
   ```powershell
   cd frontend
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Start the development server:
   ```powershell
   npm run dev
   ```
   The app will be available at `http://localhost:5173` (default Vite port).

## Usage
1. Open the frontend in your browser.
2. Fill in your education, skills, and preferred location.
3. Click "Get Recommendations" to view personalized internship matches.

## Project Structure
```
backend/
  app.py                # FastAPI server
  recommender.py        # Embedding logic & recommendation engine
  compute_embeddings.py # Script to compute/update embeddings
  internships.json      # Internship data
  embeddings.json       # Precomputed embeddings
frontend/
  src/                  # React source code
    App.jsx             # Main app logic
    components/         # UI components
  index.html            # Entry point
  package.json          # Frontend dependencies
LICENSE
README.md
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
Prabhat9801
