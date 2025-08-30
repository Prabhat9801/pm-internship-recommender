import React from "react";
export default function Navbar(){
  return (
    <header className="navbar">
      <div className="nav-inner">
        <div className="brand">
          <div className="logo">PM</div>
          <div className="brand-text">
            <div className="title">PM Internship</div>
            <div className="subtitle">AI Recommendation</div>
          </div>
        </div>
        <nav className="nav-links">
          <a href="#" className="nav-link">Home</a>
          <a href="#" className="nav-link">About</a>
          <a href="#" className="nav-link">Help</a>
        </nav>
      </div>
    </header>
  );
}
