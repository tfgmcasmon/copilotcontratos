// src/pages/LegalChat.js
import React, { useState } from "react";
import "./LegalChat.css";

const LegalChat = ({ onBack }) => {
    const [userInput, setUserInput] = useState("");
    const [messages, setMessages] = useState([]);

    const handleSend = async () => {
        if (!userInput.trim()) return;

        const userMessage = { role: "user", text: userInput };
        setMessages((prev) => [...prev, userMessage]);

        try {
            const response = await fetch("http://127.0.0.1:8080/legalChat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: [
                      { role: "user", content: userInput }
                    ]
                  }),
                  
            });

            const data = await response.json();
            const assistantMessage = { role: "assistant", text: data.response };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: "❌ Error al obtener respuesta del servidor." },
            ]);
        }

        setUserInput("");
    };

    return (
        <div className="legal-chat-container">
            <header className="header">
                <img src="./logo.jpg" alt="Themis Logo" className="logo" />
                <h1 className="title">Asistente Legal</h1>
            </header>

            <div className="chat-box">
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role}`}>
                        <span>{msg.text}</span>
                    </div>
                ))}
            </div>

            <div className="chat-input">
                <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="¿Qué necesitas saber?"
                />
                <button onClick={handleSend}>Enviar</button>
            </div>

            <button onClick={onBack} className="back-button">🔙 Volver</button>
        </div>
    );
};

export default LegalChat;
