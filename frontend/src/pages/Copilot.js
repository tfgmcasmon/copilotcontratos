// src/pages/Copilot.js
import React, { useEffect, useState, useRef } from "react";
import "../styles/pages/Copilot.css";
import BackButton from "../components/BackButton";
import jsPDF from "jspdf";
import {
  fetchContractTitle,
  fetchAutocomplete,
  verifyContractData,
} from "../api/copilotAPI";

const Copilot = ({ onBack }) => {
  const [contractType, setContractType] = useState("compraventa");
  const [inputText, setInputText] = useState("");
  const [autocompleteText, setAutocompleteText] = useState("");
  const [verificationResult, setVerificationResult] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const debounceTimer = useRef(null);
  const [suggestion,setSuggestion]=useState("");

  useEffect(() => {
    fetchContractTitle(contractType, setInputText, setContractType, setErrorMessage);
  }, [contractType]);

  const handleInputChange = (e) => {
    const text = e.target.value;
    setInputText(text);
    console.log("Texto actual:", inputText);


    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    debounceTimer.current = setTimeout(() => {
      if (text.length >= 10) {
        fetchAutocomplete(text, contractType, setAutocompleteText);
      }
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Tab" && autocompleteText) {
      e.preventDefault();
      const cleanedText = autocompleteText
        .replace(/\n+/g, " ")        // ⚠️ quita saltos de línea
        .replace(/\s{2,}/g, " ")     // ⚠️ quita dobles espacios
        .trim();
  
      setInputText((prev) => (prev + cleanedText));
      setAutocompleteText(""); // limpia sugerencia después de usarla
    }
  };
  

  const handleSaveContract = () => {
    if (!inputText.trim()) {
      alert("El contrato está vacío.");
      return;
    }

    const doc = new jsPDF();
    const lines = doc.splitTextToSize(inputText, 180);
    doc.text(lines, 15, 20);
    doc.save("contrato.pdf");
  };

  const handleVerifyContract = () => {
    verifyContractData(inputText, setVerificationResult, setVerifying);
  };

  return (
    <div className="copilot-layout">
      <BackButton onClick={onBack} />

      <div className="editor-container">
        <div className="header-bar">
          <div>
            <h2 className="copilot-title">Copilot de Contratos</h2>
            <p className="copilot-subtitle">
              Redacción jurídica asistida por IA en tiempo real.
            </p>
          </div>
          <div className="toolbar">
            <select
              value={contractType}
              onChange={(e) => setContractType(e.target.value)}
              className="contract-selector"
            >
              <option value="compraventa">Compraventa</option>
              <option value="arras">Arras</option>
              <option value="arrendamiento">Arrendamiento</option>
            </select>

            <button className="toolbar-btn" onClick={handleSaveContract}>
               Guardar
            </button>
            <button className="toolbar-btn" onClick={handleVerifyContract}>
              {verifying ? "Verificando..." : " Verificar"}
            </button>
          </div>
        </div>

        <div className="main-panel">
          <textarea
            placeholder="Escribe tu contrato aquí..."
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="editor-textarea"
          ></textarea>

          <aside className="sidebar">
            {autocompleteText && (
              <>
                <h3>💡 Sugerencia:</h3>
                <p className="suggestion">{autocompleteText}</p>
              </>
            )}

            {verificationResult?.status === "warning" && (
              <>
                <h4>⚠️ Problemas:</h4>
                <ul className="issues-list">
                  {verificationResult.issues.map((issue, idx) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              </>
            )}

            {verificationResult?.status === "ok" && (
              <p className="ok">{verificationResult.message}</p>
            )}

            {verificationResult?.status === "error" && (
              <p className="error">{verificationResult.message}</p>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
};

export default Copilot;
