import React, { useState, useRef } from "react";
import "katex/dist/katex.min.css"; // Importa KaTeX para renderizar LaTeX
import { renderToString } from "katex"; // Convierte LaTeX a HTML
import "./App.css";

const App = () => {
    const [inputText, setInputText] = useState(""); // Texto actual del input
    const [autocompleteText, setAutocompleteText] = useState(""); // Texto autocompletado
    const [formattedLatex, setFormattedLatex] = useState(""); // Texto formateado con LaTeX
    const [replacements, setReplacements] = useState({}); // Datos originales para desanonimización
    const debounceTimer = useRef(null); // Temporizador de debounce

    /**
     * Realiza una solicitud al backend para obtener el autocompletado.
     * @param {string} text - Texto del usuario.
     */
    const fetchAutocomplete = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8080/trackChanges", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ changes: text }),
            });

            if (response.ok) {
                const data = await response.json();
                const restoredAutocomplete = restoreText(data.autocomplete, data.replacements);
                setAutocompleteText(restoredAutocomplete); // Guarda el texto autocompletado
                setReplacements(data.replacements); // Guarda los datos anonimizados
            } else {
                console.error("Error en la solicitud al backend:", response.statusText);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
        }
    };

    /**
     * Realiza una solicitud al backend para convertir el texto a LaTeX.
     * @param {string} text - Texto del usuario.
     */
    const fetchFormattedLatex = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8080/formatToLatex", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });
    
            if (response.ok) {
                const data = await response.json();
                const renderedLatex = renderLatex(data.latex); // Renderiza el texto LaTeX como HTML
                setFormattedLatex(renderedLatex); // Guarda el texto formateado
            } else {
                console.error("Error en la solicitud al backend:", response.statusText);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
        }
    };
    
    
    /**
     * Restaura los datos originales a partir de un texto anonimizado.
     * @param {string} text - Texto anonimizado.
     * @param {object} replacementsMap - Mapa de marcadores a datos originales.
     * @returns {string} - Texto restaurado con los datos originales.
     */
    const restoreText = (text, replacementsMap) => {
        let restoredText = text;

        Object.keys(replacementsMap).forEach((key) => {
            restoredText = restoredText.replace(new RegExp(key, "g"), replacementsMap[key]);
        });

        return restoredText;
    };

    /**
     * Renderiza texto LaTeX como HTML.
     * @param {string} latexText - Texto en formato LaTeX.
     * @returns {string} - HTML renderizado.
     */
    const replaceAccentsWithLatex = (text) => {
        return text
            .replace(/á/g, "\\'a")
            .replace(/é/g, "\\'e")
            .replace(/í/g, "\\'i")
            .replace(/ó/g, "\\'o")
            .replace(/ú/g, "\\'u")
            .replace(/Á/g, "\\'A")
            .replace(/É/g, "\\'E")
            .replace(/Í/g, "\\'I")
            .replace(/Ó/g, "\\'O")
            .replace(/Ú/g, "\\'U")
            .replace(/ñ/g, "\\~n")
            .replace(/Ñ/g, "\\~N");
    };
    const cleanLatex = (latexText) => {
        // Extraer solo el contenido entre \begin{document} y \end{document}
        const start = latexText.indexOf("\\begin{document}");
        const end = latexText.indexOf("\\end{document}") + "\\end{document}".length;
        if (start !== -1 && end !== -1) {
            return latexText.substring(start, end);
        }
        return latexText; // Devuelve el texto completo si no se encuentran delimitadores
    };
    
    const renderLatex = (latexText) => {
        try {
            // Convierte el texto LaTeX en HTML usando KaTeX
            return renderToString(latexText, {
                throwOnError: false,
                displayMode: true, // Modo de visualización para documentos
                strict: "ignore", // Ignorar errores estrictos
            });
        } catch (error) {
            console.error("Error al renderizar LaTeX:", error);
            return latexText; // Devuelve el texto sin formato en caso de error
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
                fetchFormattedLatex(text); // Realiza la solicitud de formato LaTeX
            }
        }, 2000);
    };

    /**
     * Maneja el tabulador para aceptar la sugerencia.
     * @param {Event} e - Evento de teclado.
     */
    const handleKeyDown = (e) => {
        if (e.key === "Tab" && autocompleteText) {
            e.preventDefault();
            setInputText((prevText) => `${prevText} ${autocompleteText}`); // Añade el autocompletado
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
                <textarea
                    rows="4"
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
                <div className="formatted-output">
                    <h2>Texto Formateado en LaTeX:</h2>
                    <div dangerouslySetInnerHTML={{ __html: formattedLatex }} />
                </div>
            </div>
        </div>
    );
};

export default App;
