import React from "react";
import "./FlipCard.css";

const FlipCard = ({ title, description, icon }) => {
  return (
    <div className="flip-card">
      <div className="flip-card-inner">
        <div className="flip-card-front">
          {icon}
          <h3>{title}</h3>
        </div>
        <div className="flip-card-back">
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
};

export default FlipCard;