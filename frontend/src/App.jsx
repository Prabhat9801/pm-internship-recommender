import React, { useState } from "react";
import Navbar from "./components/Navbar";
import ProfileForm from "./components/ProfileForm";
import ResultsGrid from "./components/ResultsGrid";

export default function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState(null);
  const [apiStats, setApiStats] = useState(null);

  async function handleSearch(profile) {
    setLoading(true);
    setError("");
    setSearchQuery(profile); // Store the search query for location analysis
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile)
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${res.status}`);
      }
      
      const data = await res.json();
      
      // Enhanced results processing
      setResults(data.recommendations || []);
      setApiStats(data.metadata || null);
      
      // Log search analytics (optional)
      console.log("Search completed:", {
        query: data.query,
        resultsCount: data.recommendations?.length || 0,
        algorithmVersion: data.metadata?.algorithm_version
      });
      
    } catch (err) {
      console.error("Search error:", err);
      
      // Enhanced error handling
      if (err.message.includes("Failed to fetch")) {
        setError("❌ Cannot connect to recommendation server. Please ensure the backend is running on port 8000.");
      } else if (err.message.includes("Skills field cannot be empty")) {
        setError("⚠️ Please enter your skills to get personalized recommendations.");
      } else if (err.message.includes("503")) {
        setError("⚠️ Recommendation service is temporarily unavailable. Please try again later.");
      } else {
        setError(`❌ ${err.message || "Failed to get recommendations. Please try again."}`);
      }
      
      // Clear results on error
      setResults([]);
      setApiStats(null);
    } finally {
      setLoading(false);
    }
  }

  // Helper function to check if backend is available
  async function checkBackendHealth() {
    try {
      const res = await fetch("http://127.0.0.1:8000/", {
        method: "GET",
        timeout: 5000
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  return (
    <div className="app-root">
      <Navbar />
      
      <main className="main">
        <div className="hero">
          <h1>PM Internship Scheme — Personalized Recommendations</h1>
          <p className="sub">
            Enter your details and we'll show 3–7 best-matching internships based on your skills and education.
          </p>
          
          {/* API Status Indicator */}
          {apiStats && (
            <div className="api-status">
              <small>
                ✅ Powered by {apiStats.algorithm_version} • 
                {apiStats.total_internships_available} internships analyzed •
                {apiStats.skill_based_filtering ? " Smart skill filtering enabled" : ""}
              </small>
            </div>
          )}
        </div>

        <ProfileForm onSubmit={handleSearch} loading={loading} />
        
        {/* Enhanced Error Display */}
        {error && (
          <div className="error-container">
            <div className="error">
              {error}
            </div>
            
            {error.includes("backend is running") && (
              <div className="error-help">
                <details>
                  <summary>💡 How to fix this</summary>
                  <div className="help-content">
                    <p><strong>Backend Setup Instructions:</strong></p>
                    <ol>
                      <li>Open terminal in the backend folder</li>
                      <li>Run: <code>python app.py</code></li>
                      <li>Wait for "Ready to serve recommendations!" message</li>
                      <li>Ensure port 8000 is not blocked</li>
                    </ol>
                    <p>Need help? Check the README.md file for detailed setup instructions.</p>
                  </div>
                </details>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>🔍 Analyzing {apiStats?.total_internships_available || "thousands of"} internships to find your perfect matches...</p>
          </div>
        )}

        {/* Results with enhanced props */}
        <ResultsGrid 
          items={results}
          userLocation={searchQuery?.location}
          userSkills={searchQuery?.skills}
          userEducation={searchQuery?.education}
        />

        {/* Search Summary */}
        {searchQuery && results.length > 0 && (
          <div className="search-summary">
            <div className="summary-card">
              <h4>🎯 Your Search Summary</h4>
              <div className="summary-details">
                <div className="summary-item">
                  <span className="label">Education:</span>
                  <span className="value">{searchQuery.education || "Not specified"}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Skills:</span>
                  <span className="value">{searchQuery.skills || "Not specified"}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Location:</span>
                  <span className="value">{searchQuery.location || "Any location"}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Results:</span>
                  <span className="value">{results.length} personalized match{results.length > 1 ? 'es' : ''}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <span>Designed for SIH 2025 • Lightweight • Mobile-first</span>
          {apiStats && (
            <span className="footer-tech">
              • {apiStats.algorithm_version} • Skill-based AI matching
            </span>
          )}
        </div>
      </footer>

      {/* Enhanced Styles */}
      <style jsx>{`
        .api-status {
          margin-top: 10px;
          padding: 8px 16px;
          background: #f0f9ff;
          border-radius: 20px;
          display: inline-block;
        }

        .api-status small {
          color: #0369a1;
          font-weight: 500;
        }

        .error-container {
          margin: 20px 0;
        }

        .error {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #dc2626;
          padding: 16px;
          border-radius: 12px;
          margin-bottom: 10px;
          border-left: 4px solid #dc2626;
        }

        .error-help {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 12px;
        }

        .error-help details {
          cursor: pointer;
        }

        .error-help summary {
          font-weight: 600;
          color: #475569;
          outline: none;
        }

        .help-content {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #e2e8f0;
        }

        .help-content ol {
          margin: 10px 0;
          padding-left: 20px;
        }

        .help-content code {
          background: #1e293b;
          color: #e2e8f0;
          padding: 2px 6px;
          border-radius: 4px;
          font-family: monospace;
        }

        .loading-container {
          text-align: center;
          padding: 40px 20px;
          margin: 20px 0;
        }

        .loading-spinner {
          width: 50px;
          height: 50px;
          border: 4px solid #f3f4f6;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .search-summary {
          margin: 40px 0 20px;
          display: flex;
          justify-content: center;
        }

        .summary-card {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          padding: 24px;
          max-width: 500px;
          width: 100%;
        }

        .summary-card h4 {
          margin: 0 0 16px 0;
          color: #374151;
          font-size: 18px;
        }

        .summary-details {
          display: grid;
          gap: 12px;
        }

        .summary-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #e5e7eb;
        }

        .summary-item:last-child {
          border-bottom: none;
        }

        .summary-item .label {
          font-weight: 600;
          color: #6b7280;
        }

        .summary-item .value {
          color: #374151;
          text-align: right;
          max-width: 60%;
        }

        .footer-content {
          display: flex;
          justify-content: center;
          align-items: center;
          flex-wrap: wrap;
          gap: 10px;
        }

        .footer-tech {
          color: #6b7280;
          font-size: 12px;
        }

        @media (max-width: 768px) {
          .summary-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
          }

          .summary-item .value {
            max-width: 100%;
            text-align: left;
          }

          .footer-content {
            flex-direction: column;
            text-align: center;
          }
        }
      `}</style>
    </div>
  );
}