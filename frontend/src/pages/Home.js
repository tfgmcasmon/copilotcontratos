import React from "react";
import "./Home.css";
import "../components/animations.css";

const Home = ({ onNavigate }) => {
    const modules = [
        { id: "copilot", title: "Copilot de Contratos", description: "Redacción jurídica asistida por IA en tiempo real." },
        { id: "legalChat", title: "Asistente Legal", description: "Consultas legales con respuestas fundamentadas." },
        { id: "visionBoard", title: "Vision Board", description: "Planificación y supervisión inteligente de tareas legales." }  
    ];

    return (
        <div className="home-container fade-in-up">
            <h2 className="home-title">Bienvenido a Themis</h2>
            <hr className="decorative-line" />
            <p className="home-subtitle">Selecciona un módulo para comenzar:</p>
            <div className="modules-container">
                {modules.map((mod, i) => (
                    <div
                        key={mod.id}
                        className="module-card animate__animated animate__fadeInUp animate__faster"
                        style={{ animationDelay: `${i * 0.1}s` }}
                        onClick={() => onNavigate(mod.id)}
                    >
                        <div className="module-icon">
                            {mod.id === "copilot" && <span>📝</span>}
                            {mod.id === "legalChat" && <span>⚖️</span>}
                            {mod.id === "visionBoard" && <span>📊</span>}  
                        </div>
                        <h3 className="module-title">{mod.title}</h3>
                        <p className="module-description">{mod.description}</p>
                        <button className="go-button">Ir →</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;
