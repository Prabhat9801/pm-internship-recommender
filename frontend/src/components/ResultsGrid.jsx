import React from "react";

export default function ResultsGrid({ items, userLocation, userSkills, userEducation }) {
  if (!items || items.length === 0) {
    return (
      <div className="no-results">
        <p className="hint">
          Enter details above and click <b>Get Recommendations</b>. 
          You'll get 3–7 personalized internship matches based on your skills and education.
        </p>
      </div>
    );
  }

  // Check if any internships match the user's preferred location
  const locationMatches = items.filter(internship => 
    internship.match_details?.location_match || 
    (userLocation && internship.location && 
     (internship.location.toLowerCase().includes(userLocation.toLowerCase()) ||
      userLocation.toLowerCase().includes(internship.location.toLowerCase()) ||
      internship.location.toLowerCase() === "remote" ||
      userLocation.toLowerCase() === "remote"))
  );

  const hasLocationMatches = locationMatches.length > 0;
  const hasNonLocationMatches = items.length > locationMatches.length;

  // Helper function to get match badge
  const getMatchBadge = (matchDetails) => {
    if (!matchDetails) return null;
    
    const { exact_skill_matches, education_match, location_match } = matchDetails;
    
    if (exact_skill_matches >= 2 && education_match && location_match) {
      return <span className="match-badge perfect">Perfect Match</span>;
    } else if (exact_skill_matches >= 2 && education_match) {
      return <span className="match-badge excellent">Excellent Match</span>;
    } else if (exact_skill_matches >= 1 && education_match) {
      return <span className="match-badge good">Good Match</span>;
    } else if (exact_skill_matches >= 1) {
      return <span className="match-badge skill">Skill Match</span>;
    }
    return null;
  };

  // Helper function to format match details
  const formatMatchDetails = (matchDetails) => {
    if (!matchDetails) return null;
    
    const details = [];
    
    if (matchDetails.exact_skill_matches > 0) {
      details.push(`${matchDetails.exact_skill_matches} exact skill match${matchDetails.exact_skill_matches > 1 ? 'es' : ''}`);
    }
    
    if (matchDetails.partial_skill_matches > 0) {
      details.push(`${matchDetails.partial_skill_matches} related skill${matchDetails.partial_skill_matches > 1 ? 's' : ''}`);
    }
    
    if (matchDetails.education_match) {
      details.push('education match');
    }
    
    if (matchDetails.location_match) {
      details.push('location match');
    }

    return details.length > 0 ? details.join(' • ') : 'semantic similarity';
  };

  return (
    <section className="results-section">
      {/* Location Status Message */}
      {userLocation && userLocation.trim() !== '' && (
        <div className="location-status">
          {hasLocationMatches && hasNonLocationMatches ? (
            <div className="status-message mixed">
              <div className="status-icon">📍</div>
              <div className="status-text">
                <strong>Mixed Results:</strong> {locationMatches.length} internship{locationMatches.length > 1 ? 's' : ''} 
                available in <strong>{userLocation}</strong>, plus {items.length - locationMatches.length} excellent 
                match{items.length - locationMatches.length > 1 ? 'es' : ''} in other locations based on your skills and education.
              </div>
            </div>
          ) : hasLocationMatches ? (
            <div className="status-message success">
              <div className="status-icon">✅</div>
              <div className="status-text">
                <strong>Great News!</strong> Found {locationMatches.length} internship{locationMatches.length > 1 ? 's' : ''} 
                in <strong>{userLocation}</strong> matching your profile.
              </div>
            </div>
          ) : (
            <div className="status-message info">
              <div className="status-icon">🌍</div>
              <div className="status-text">
                <strong>Location Note:</strong> No internships available in <strong>{userLocation}</strong>, 
                but we found {items.length} excellent match{items.length > 1 ? 'es' : ''} in other locations 
                based on your <strong>skills</strong> and <strong>education</strong>. 
                Consider these opportunities or try "Remote" as your location preference.
              </div>
            </div>
          )}
        </div>
      )}

      {/* Results Grid */}
      <div className="results-grid">
        {items.map((internship, index) => (
          <article 
            className={`card result-card ${internship.match_details?.location_match ? 'location-match' : 'other-location'}`} 
            key={internship.id || `internship-${index}`}
          >
            {/* Match Badge */}
            <div className="card-header">
              {getMatchBadge(internship.match_details)}
              {internship.match_details?.fallback_recommendation && (
                <span className="match-badge fallback">Similar Content</span>
              )}
            </div>

            {/* Main Content */}
            <div className="card-head">
              <h3>{internship.title}</h3>
              <span className="org">{internship.org || internship.company}</span>
            </div>

            {/* Location with indicator */}
            <div className="location-info">
              <p className="meta location">
                📍 <span className={internship.match_details?.location_match ? 'location-preferred' : 'location-other'}>
                  {internship.location}
                </span>
                {internship.match_details?.location_match && (
                  <span className="location-indicator">• Your Preference</span>
                )}
                {!internship.match_details?.location_match && internship.location?.toLowerCase() === 'remote' && (
                  <span className="location-indicator remote">• Work from Anywhere</span>
                )}
              </p>
            </div>

            <p className="meta education">🎓 {internship.required_education || internship.education}</p>
            
            <div className="skills-section">
              <p className="skills">
                🛠 {Array.isArray(internship.skills) ? internship.skills.join(", ") : internship.skills}
              </p>
              
              {/* Match Details */}
              {internship.match_details && (
                <div className="match-info">
                  <small className="match-details">
                    Why recommended: {formatMatchDetails(internship.match_details)}
                  </small>
                </div>
              )}
            </div>

            {/* Sector/Additional Info */}
            {internship.sector && (
              <p className="meta sector">
                🏢 {Array.isArray(internship.sector) ? internship.sector.join(", ") : internship.sector}
              </p>
            )}

            <div className="card-foot">
              <a 
                className="apply-btn" 
                href={internship.apply_url || internship.apply_link || '#'} 
                target="_blank" 
                rel="noreferrer"
                onClick={internship.apply_url || internship.apply_link ? undefined : (e) => {
                  e.preventDefault();
                  alert('Application link not available for this internship.');
                }}
              >
                Apply {internship.match_details?.location_match ? '🎯' : '🌍'}
              </a>
              <div className="score-info">
                <span className="score">
                  Match: {internship.score ? (internship.score * 100).toFixed(0) : "N/A"}%
                </span>
                {internship.match_details?.semantic_similarity && (
                  <small className="semantic-score">
                    Relevance: {(internship.match_details.semantic_similarity * 100).toFixed(0)}%
                  </small>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="results-summary">
        <div className="summary-stats">
          <span>📊 Showing {items.length} recommendation{items.length > 1 ? 's' : ''}</span>
          {userLocation && hasLocationMatches && (
            <span>📍 {locationMatches.length} in {userLocation}</span>
          )}
          {userLocation && hasNonLocationMatches && (
            <span>🌍 {items.length - locationMatches.length} in other locations</span>
          )}
        </div>
        
        {userLocation && !hasLocationMatches && (
          <div className="location-suggestion">
            <small>
              💡 <strong>Tip:</strong> Try searching with "Remote" or nearby cities for more local opportunities, 
              or consider the excellent matches above based on your skills.
            </small>
          </div>
        )}
      </div>

      {/* Enhanced CSS Styles */}
      <style jsx>{`
        .location-status {
          margin: 20px 0;
          padding: 0;
        }

        .status-message {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 16px;
          border-radius: 12px;
          margin-bottom: 20px;
          border-left: 4px solid;
        }

        .status-message.success {
          background: #f0f9ff;
          border-left-color: #10b981;
          color: #065f46;
        }

        .status-message.info {
          background: #fefce8;
          border-left-color: #f59e0b;
          color: #92400e;
        }

        .status-message.mixed {
          background: #f8fafc;
          border-left-color: #6366f1;
          color: #4338ca;
        }

        .status-icon {
          font-size: 20px;
          flex-shrink: 0;
        }

        .status-text {
          flex: 1;
          line-height: 1.5;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
          min-height: 24px;
        }

        .match-badge {
          font-size: 11px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .match-badge.perfect {
          background: #10b981;
          color: white;
        }

        .match-badge.excellent {
          background: #3b82f6;
          color: white;
        }

        .match-badge.good {
          background: #8b5cf6;
          color: white;
        }

        .match-badge.skill {
          background: #f59e0b;
          color: white;
        }

        .match-badge.fallback {
          background: #6b7280;
          color: white;
        }

        .location-preferred {
          color: #10b981;
          font-weight: 600;
        }

        .location-other {
          color: #6b7280;
        }

        .location-indicator {
          font-size: 12px;
          color: #10b981;
          font-weight: 500;
        }

        .location-indicator.remote {
          color: #8b5cf6;
        }

        .result-card.location-match {
          border-left: 4px solid #10b981;
        }

        .result-card.other-location {
          border-left: 4px solid #e5e7eb;
        }

        .match-info {
          margin-top: 8px;
        }

        .match-details {
          color: #6b7280;
          font-size: 12px;
          font-style: italic;
        }

        .score-info {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }

        .semantic-score {
          font-size: 10px;
          color: #9ca3af;
        }

        .results-summary {
          margin-top: 30px;
          padding: 20px;
          background: #f9fafb;
          border-radius: 12px;
          text-align: center;
        }

        .summary-stats {
          display: flex;
          justify-content: center;
          gap: 20px;
          flex-wrap: wrap;
          margin-bottom: 10px;
        }

        .summary-stats span {
          font-size: 14px;
          color: #4b5563;
        }

        .location-suggestion {
          margin-top: 12px;
          color: #6b7280;
        }
      `}</style>
    </section>
  );
}