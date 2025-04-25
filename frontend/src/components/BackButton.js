// src/components/BackButton.js

import React from "react";
import "../styles/components/BackButton.css"; // (opcional si quieres estilos específicos)

const BackButton = ({ onClick }) => {
    return (
        <button className="back-button" onClick={onClick}>
            ← Volver
        </button>
    );
};

export default BackButton;
