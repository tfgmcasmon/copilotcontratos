import React from "react";
import "../styles/components/AlertCard.css";

function AlertCard({ alert }) {
    return (
        <div className="alert-card">
            <h3 className="alert-card-type">{alert.tipo}</h3>
            <p className="alert-card-message">{alert.mensaje}</p>
        </div>
    );
}

export default AlertCard;
