import React from "react";
import "../styles/components/SuggestionCard.css";

function SuggestionCard({ suggestion }) {
    return (
        <div className="suggestion-card">
            <h3 className="suggestion-card-title">Sugerencia de Reasignación</h3>
            <p className="suggestion-card-info">
                Mover tarea asignada a <strong>{suggestion.usuario_actual}</strong> hacia <strong>{suggestion.usuario_recomendado}</strong>
            </p>
            <p className="suggestion-card-motivo">Motivo: {suggestion.motivo}</p>
            {suggestion.aceptada === null && (
                <p className="suggestion-card-status">Pendiente de decisión</p>
            )}
            {suggestion.aceptada === true && (
                <p className="suggestion-card-status aceptada">Aceptada</p>
            )}
            {suggestion.aceptada === false && (
                <p className="suggestion-card-status rechazada">Rechazada</p>
            )}
        </div>
    );
}

export default SuggestionCard;
