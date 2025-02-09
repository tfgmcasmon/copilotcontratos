import React, { useState, useRef } from "react";
import "katex/dist/katex.min.css"; // Importa KaTeX para renderizar LaTeX
import { renderToString } from "katex"; // Convierte LaTeX a HTML
import "./App.css";

const App = () => {
    const [currentScreen, setCurrentScreen] = useState("home"); // Pantalla actual (home o editor)
    const [contractType, setContractType] = useState(""); // Tipo de contrato seleccionado
    const [inputText, setInputText] = useState(""); // Texto actual del input
    const [autocompleteText, setAutocompleteText] = useState(""); // Texto autocompletado
    const [formattedLatex, setFormattedLatex] = useState(""); // Texto formateado con LaTeX
    const [errorMessage, setErrorMessage] = useState(""); // Mensaje de error para el usuario
    const debounceTimer = useRef(null); // Temporizador de debounce

    /**
     * Obtiene el contexto inicial específico para el tipo de contrato seleccionado.
     * @param {string} type - Tipo de contrato.
     */
    const fetchContractTitle = async (type) => {
        try {
            const response = await fetch("http://127.0.0.1:8080/generateContractContext", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ contract_type: type }),
            });

            if (response.ok) {
                const data = await response.json();
                const title = data.prompt.split("\n")[0]; // Solo toma el título
                setInputText(title || ""); // Muestra solo el título en el textarea
                setContractType(type); // Guarda el tipo de contrato seleccionado
                setCurrentScreen("editor"); // Cambia a la pantalla del editor
                setErrorMessage(""); // Limpia cualquier mensaje de error previo
            } else {
                setErrorMessage("Error al obtener el título del contrato.");
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
            setErrorMessage("No se pudo conectar al servidor. Por favor, intente de nuevo.");
        }
    };

    /**
     * Realiza una solicitud al backend para obtener el autocompletado.
     * @param {string} text - Texto del usuario.
     */
    const fetchAutocomplete = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8080/trackChanges", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ changes: text, contract_type: contractType }),
            });

            if (response.ok) {
                const data = await response.json();
                setAutocompleteText(data.autocomplete || ""); // Guarda el texto autocompletado
            } else {
                console.error("Error en la solicitud al backend:", response.statusText);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
        }
    };

    /**
     * Maneja cambios en el textarea.
     * @param {Event} e - Evento de cambio.
     */
    const handleInputChange = (e) => {
        const text = e.target.value;
        setInputText(text);

        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        debounceTimer.current = setTimeout(() => {
            if (text.length >= 10) {
                fetchAutocomplete(text); // Realiza la solicitud de autocompletado
            }
        }, 1000);
    };

    /**
     * Maneja el tabulador para aceptar la sugerencia.
     * @param {Event} e - Evento de teclado.
     */
    const handleKeyDown = (e) => {
        if (e.key === "Tab" && autocompleteText) {
            e.preventDefault();
            const sanitizedText = autocompleteText.trim();
    
            // Ignorar autocompletados que sean solo números o irrelevantes
            if (!sanitizedText || !/[a-zA-Z]/.test(sanitizedText)) {
                setAutocompleteText(""); // Limpia el autocompletado si es irrelevante
                return;
            }
    
            // Insertar la sugerencia como una nueva línea
            setInputText((prevText) => `${prevText}\n${sanitizedText}`);
            setAutocompleteText(""); // Limpia el texto autocompletado
        }
    };
    
    // Pantalla inicial
    if (currentScreen === "home") {
        return (
            <div className="app-container">
                <header className="header">
                    <img src="./logo.jpg" alt="Themis Logo" className="logo" />
                    <h1 className="title">Themis</h1>
                </header>
                <div className="contract-selection">
                    <h2>Selecciona el tipo de contrato:</h2>
                    <button onClick={() => fetchContractTitle("arras")} className="contract-button">Contrato de Arras</button>
                    <button onClick={() => fetchContractTitle("compraventa")} className="contract-button">Contrato de Compraventa</button>
                    <button onClick={() => fetchContractTitle("arrendamiento")} className="contract-button">Contrato de Arrendamiento</button>
                    {errorMessage && <p className="error-message">{errorMessage}</p>}
                </div>
            </div>
        );
    }

    // Pantalla del editor
    return (
        <div className="app-container">
            <header className="header">
                <img src="./logo.jpg" alt="Themis Logo" className="logo" />
                <h1 className="title">Themis</h1>
            </header>
            <div className="main-content">
                <textarea
                    rows="6"
                    value={inputText}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Escribe algo para obtener sugerencias..."
                    className="input-box"
                ></textarea>
                <div className="autocomplete-output">
                    <h2>Texto Autocompletado:</h2>
                    <p>{autocompleteText}</p>
                </div>
            </div>
        </div>
    );
};

export default App;
