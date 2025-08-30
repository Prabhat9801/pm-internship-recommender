import React, { useState } from "react";

export default function ProfileForm({ onSubmit, loading }){
  const [education, setEducation] = useState("UG");
  const [skills, setSkills] = useState("");
  const [location, setLocation] = useState("remote");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ education, skills, location, top_k: 4 });
  };

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>Education</label>
        <select value={education} onChange={e=>setEducation(e.target.value)}>
          <option>12th</option>
          <option>UG</option>
          <option>BTech</option>
          <option>PG</option>
        </select>
      </div>

      <div className="form-row">
        <label>Skills (comma separated)</label>
        <input placeholder="e.g. python, html, machine learning" value={skills} onChange={e=>setSkills(e.target.value)} />
      </div>

      <div className="form-row">
        <label>Preferred Location</label>
        <input placeholder="e.g. remote, delhi, mumbai" value={location} onChange={e=>setLocation(e.target.value)} />
      </div>

      <div className="form-actions">
        <button className="btn-primary" type="submit" disabled={loading}>{loading ? "Searching..." : "Get Recommendations"}</button>
      </div>
    </form>
  );
}
