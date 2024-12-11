import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const App = () => {
    const [inputText, setInputText] = useState(""); // Texto actual del input
    const [lastLength, setLastLength] = useState(0); // Longitud registrada en la última solicitud
    const [autocompleteText, setAutocompleteText] = useState(""); // Texto autocompletado
    const debounceTimer = useRef(null); // Temporizador de debounce

    // Función para manejar cambios en el input
    const handleInputChange = (e) => {
        const text = e.target.value;
        setInputText(text); // Actualiza el texto del input

        // Si hay un temporizador, lo limpiamos para evitar múltiples llamadas
        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        // Espera 2 segundos después de que el usuario deje de escribir
        debounceTimer.current = setTimeout(() => {
            const currentLength = text.length;
            const lengthDifference = Math.abs(currentLength - lastLength);

            // Condiciones para realizar la solicitud:
            // 1. Al menos 10 caracteres de diferencia.
            // 2. La longitud actual debe ser al menos 10.
            if (lengthDifference >= 10 && currentLength >= 10) {
                console.log(
                    `Detectados ${lengthDifference} caracteres de cambio. Realizando solicitud al backend.`
                );
                fetchAutocomplete(text); // Realiza la solicitud al backend
                setLastLength(currentLength); // Actualizamos la longitud registrada
            } else {
                console.log(
                    `Cambios insuficientes o texto demasiado corto (${lengthDifference} caracteres, longitud actual: ${currentLength}). No se realiza solicitud.`
                );
            }
        }, 2000); // 2 segundos
    };

    // Llamada al backend para obtener el autocompletado
    const fetchAutocomplete = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8080/trackChanges", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ changes: text }),
            });
            if (response.ok) {
                const data = await response.json();
                setAutocompleteText(data.autocomplete || ""); // Actualiza el texto autocompletado
            } else {
                console.error("Error en la solicitud al backend:", response.statusText);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
        }
    };

    // Manejar el tabulador para aceptar la sugerencia
    const handleKeyDown = (e) => {
        if (e.key === "Tab" && autocompleteText) {
            e.preventDefault();
            setInputText((prevText) => `${prevText}${autocompleteText}`); // Agrega la sugerencia al texto
            setAutocompleteText(""); // Limpia el texto autocompletado
        }
    };

    return (
        <div className="app-container">
            <header className="header">
                <img src="./logo.jpg" alt="Themis Logo" className="logo" />
                <h1 className="title">Themis</h1>
            </header>
            <div className="main-content">
                <nav className="sidebar">
                    <ul>
                        <li>Home</li>
                        <li className="active">Copilot de Contratos</li>
                        <li>Gestor de Tareas</li>
                        <li>Búsqueda Avanzada</li>
                    </ul>
                </nav>
                <div className="editor-container">
                    <div className="input-section">
                        <textarea
                            rows="4"
                            value={inputText}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Escribe algo para obtener sugerencias..."
                            className="input-box"
                        ></textarea>
                        {autocompleteText && (
                            <p className="autocomplete">
                                {autocompleteText}
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;
