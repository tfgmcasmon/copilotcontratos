import React, { useState, useRef } from "react";
import "katex/dist/katex.min.css"; // Importa KaTeX para renderizar LaTeX
import { renderToString } from "katex"; // Convierte LaTeX a HTML
import "./App.css";
import jsPDF from "jspdf";
import LegalChat  from "./pages/LegalChat";
import TaskManager from "./pages/TaskManager";


const App = () => {
    const [currentScreen, setCurrentScreen] = useState("home"); // Pantalla actual (home o editor)
    const [contractType, setContractType] = useState(""); // Tipo de contrato seleccionado
    const [inputText, setInputText] = useState(""); // Texto actual del input
    const [autocompleteText, setAutocompleteText] = useState(""); // Texto autocompletado
    const [formattedLatex, setFormattedLatex] = useState(""); // Texto formateado con LaTeX
    const [errorMessage, setErrorMessage] = useState(""); // Mensaje de error para el usuario
    const debounceTimer = useRef(null); // Temporizador de debounce
    const [verificationResult, setVerificationResult] = useState(null);
    const [verifying, setVerifying] = useState(false);
    const [issues, setIssues] = useState([]);
    const [highlightedText, setHighlightedText] = useState("");



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

    const verifyContractData = async () => {
        setVerifying(true);
        setVerificationResult(null);
    
        try {
            const response = await fetch("http://127.0.0.1:8080/verifyContractData", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ contract_text: inputText }),
            });
    
            const data = await response.json();
    
            if (response.ok) {
                if (Array.isArray(data.issues) && data.issues.length > 0) {
                    setVerificationResult({ status: "warning", issues: data.issues });
                } else if (data.message) {
                    setVerificationResult({ status: "ok", message: data.message });
                } else {
                    setVerificationResult({ status: "ok", message: "✅ Todo parece correcto." });
                }
            } else {
                setVerificationResult({ status: "error", message: data.error || "❌ Error al verificar los datos." });
            }
        } catch (err) {
            console.error("❌ Error al conectar con el backend:", err);
            setVerificationResult({ status: "error", message: "❌ No se pudo conectar al servidor." });
        } finally {
            setVerifying(false);
        }
    };

    const generateHighlightedText = (text, issues) => {
        let result = "";
        let lastIndex = 0;
    
        if (!Array.isArray(issues)) return text;
    
        // Detecta patrones para highlight si no hay posiciones (fallback)
        const regexIssues = issues.map((msg) => {
            const match = msg.match(/'([^']+)'/);
            return match ? match[1] : null;
        }).filter(Boolean);
    
        const segments = [];
    
        regexIssues.forEach((fragment) => {
            let index = text.toLowerCase().indexOf(fragment.toLowerCase());
            if (index !== -1 && !segments.some(seg => seg.start === index)) {
                segments.push({
                    start: index,
                    end: index + fragment.length,
                    message: fragment,
                });
            }
        });
    
        segments.sort((a, b) => a.start - b.start).forEach((seg) => {
            result += text.slice(lastIndex, seg.start);
            result += `<span class="highlight" title="${seg.message}">${text.slice(seg.start, seg.end)}</span>`;
            lastIndex = seg.end;
        });
    
        result += text.slice(lastIndex);
        return result;
    };
    
    
    const applyHighlights = (text, issues) => {
        let highlighted = "";
        let lastIndex = 0;
      
        issues.sort((a, b) => a.start - b.start).forEach(issue => {
          highlighted += text.slice(lastIndex, issue.start);
          highlighted += `<span class="error" title="${issue.message}">${text.slice(issue.start, issue.end)}</span>`;
          lastIndex = issue.end;
        });
      
        highlighted += text.slice(lastIndex);
        return highlighted;
      };
      

      const handleVerifyContract = async () => {
        console.log("✅ Botón de verificación presionado");
        try {
            await verifyContractData(); // Usamos tu función escalable
            if (verificationResult?.issues?.length) {
                const html = generateHighlightedText(inputText, verificationResult.issues);
                setHighlightedText(html);
            }

        } catch (error) {
            console.error("❌ Error al verificar datos:", error);
        }
    };
    
    const getHighlightedText = () => {
        if (!issues.length) return inputText;

        let highlighted = "";
        let lastIndex = 0;

        // Ordenamos los errores por posición
        const sorted = [...issues].sort((a, b) => a.start - b.start);

        sorted.forEach(issue => {
            highlighted += inputText.slice(lastIndex, issue.start);
            highlighted += `<span class="error" title="${issue.message}">${inputText.slice(issue.start, issue.end)}</span>`;
            lastIndex = issue.end;
        });

        highlighted += inputText.slice(lastIndex);
        return highlighted;
    };


    const handleSaveContract = () => {
        if (!inputText.trim()) {
            alert("El contrato está vacío.");
            return;
        }
    
        const doc = new jsPDF();
        const lines = doc.splitTextToSize(inputText, 180); // ajusta a ancho de página
        doc.text(lines, 15, 20);
        doc.save("contrato.pdf");
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
                    <button onClick={() => fetchContractTitle("arras")&&setCurrentScreen("editor")} className="contract-button">Contrato de Arras</button>
                    <button onClick={() => fetchContractTitle("compraventa")&&setCurrentScreen("editor")} className="contract-button">Contrato de Compraventa</button>
                    <button onClick={() => fetchContractTitle("arrendamiento")&&setCurrentScreen("editor")} className="contract-button">Contrato de Arrendamiento</button>
                    <button onClick={() => setCurrentScreen("legalchat")} className="contract-button">
                    📚 Asistente Legal
                    </button>
                    <button onClick={() => setCurrentScreen("taskmanager")} className="contract-button">
                    🧠 Gestor de Tareas Inteligente
                    </button>

                    {errorMessage && <p className="error-message">{errorMessage}</p>}
                </div>
            </div>
        );
    }
  
    if (currentScreen === "taskmanager") {
        return <TaskManager onBack={() => setCurrentScreen("home")} />;
    }
    
    if (currentScreen === "editor") {

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
                    {highlightedText && (
                        <div className="highlighted-output">
                            <h3>Texto con Errores Marcados:</h3>
                            <div dangerouslySetInnerHTML={{ __html: highlightedText }} />
                        </div>
                    )}

                    <div className="autocomplete-output">
                        <h2>Texto Autocompletado:</h2>
                        <p>{autocompleteText}</p>
                    </div>
                    <button onClick={handleSaveContract} className="save-button">
                        Guardar Contrato
                    </button>
                    <button onClick={handleVerifyContract} className="verify-button">
                        {verifying ? "Verificando..." : "Verificar Datos"}
                    </button>
                    {verificationResult && (
                        <div className={`verification-message ${verificationResult.status}`}>
                            {verificationResult.status === "ok" && (
                                <p>{verificationResult.message}</p>
                            )}

                            {verificationResult.status === "warning" && (
                                <div>
                                    <p>⚠️ Se detectaron los siguientes posibles errores:</p>
                                    <ul>
                                        {verificationResult.issues.map((issue, i) => (
                                            <li key={i}>{issue}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {verificationResult.status === "error" && (
                                <p>❌ {verificationResult.message}</p>
                            )}
                        </div>
                    )}

                </div>
            </div>
        );
    }

    if (currentScreen === "legalchat") {

        return <LegalChat onBack={() => setCurrentScreen("home")} />;

    };
}

export default App;
