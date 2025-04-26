import React, { useEffect, useState, useRef } from "react";
import "../styles/pages/Copilot.css";
import BackButton from "../components/BackButton";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import html2pdf from "html2pdf.js";
import {
  fetchContractTitle,
  fetchAutocomplete,
  verifyContractData,
} from "../api/copilotAPI";

const Copilot = ({ onBack }) => {
  const [contractName, setContractName] = useState("");
  const [inputText, setInputText] = useState("");
  const [autocompleteText, setAutocompleteText] = useState("");
  const [verificationResult, setVerificationResult] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const debounceTimer = useRef(null);
  const [legalAnalysis, setLegalAnalysis] = useState("");
  const [renderedContract, setRenderedContract] = useState("");
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [loadingRender, setLoadingRender] = useState(false);

  useEffect(() => {
    fetchContractTitle(contractName, setInputText, setContractName, setErrorMessage);
  }, [contractName]);

  const handleInputChange = (e) => {
    const text = e.target.value;
    setInputText(text);
  
    // Cancelar temporizador anterior si existe
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
  
    // Nuevo debounce
    debounceTimer.current = setTimeout(() => {
      // Solo pedir autocompletado si el texto ya tiene un mínimo de longitud útil
      if (text.trim().length >= 30) {
        fetchAutocomplete(inputText, contractName, setAutocompleteText);
      }
    }, 1000);
  };
  

  const handleKeyDown = (e) => {
    if (e.key === "Tab" && autocompleteText) {
      e.preventDefault();
      const cleanedText = autocompleteText
        .replace(/\n+/g, " ")
        .replace(/\s{2,}/g, " ")
        .trim();
      setInputText((prev) => prev + cleanedText);
      setAutocompleteText("");
    }
  };

  const handleVerifyContract = () => {
    verifyContractData(inputText, setVerificationResult, setVerifying);
  };

  const handleRunLegalCheck = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8080/legalCheck", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: inputText, contract_type: contractName }),
      });
      const data = await response.json();
      setLegalAnalysis(data.analysis);
    } catch (err) {
      console.error("Error al verificar contrato:", err);
    }
  };

  const handleRenderContract = async () => {
    if (!inputText.trim()) {
      alert("El contrato está vacío.");
      return;
    }
    setLoadingRender(true);
    try {
      const response = await fetch("http://127.0.0.1:8080/renderContract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: inputText }),
      });
      if (response.ok) {
        const data = await response.json();
        const cleanedHTML = (data.rendered_html || "").replace(/```html|```/g, "").trim();
        setRenderedContract(cleanedHTML);
        setIsPreviewMode(true);
      } else {
        console.error("Error al renderizar el contrato");
      }
    } catch (error) {
      console.error("Error al conectar con el backend:", error);
    } finally {
      setLoadingRender(false);
    }
  };


  const handleSaveRenderedContract = () => {
    if (!renderedContract.trim()) {
      alert("El contrato está vacío.");
      return;
    }
  
    const doc = new jsPDF();
    doc.setFont("times", "normal");
  
    // Título
    doc.setFontSize(18);
    doc.setFont("times","bold")
    doc.text(contractName.toUpperCase(), 105, 20, { align: "center" });

  
    // Disclaimer
    doc.setFontSize(10);
    doc.setFont("times","bold")
    const disclaimer = getDisclaimerByContractName(contractName);
    const disclaimerLines = doc.splitTextToSize(disclaimer, 180);
    doc.text(disclaimerLines, 15, 30);
  
    // Procesar el HTML del contrato renderizado
    const container = document.createElement("div");
    container.innerHTML = renderedContract;
    const paragraphs = container.querySelectorAll("p, strong");
  
    let currentY = 50;
  
    paragraphs.forEach((el) => {
      if (currentY > 270) {
        doc.addPage();
        currentY = 20;
      }
  
      if (el.tagName === "STRONG") {
        doc.setFontSize(14);
        doc.setFont("times", "bold");
        const lines = doc.splitTextToSize(el.innerText, 180);
        doc.text(lines, 15, currentY);
        currentY += lines.length * 8;
      } else {
        doc.setFontSize(12);
        doc.setFont(undefined, "normal");
        const lines = doc.splitTextToSize(el.innerText, 180);
        doc.text(lines, 15, currentY);
        currentY += lines.length * 7;
      }
    });
  
    // Firmas
    if (currentY + 30 > 270) {
      doc.addPage();
      currentY = 30;
    }
  
    doc.setFont("times", "normal");
    doc.setFontSize(12);
    doc.line(30, currentY + 20, 80, currentY + 20);
    doc.text("Firma del Comprador", 30, currentY + 25);
  
    doc.line(130, currentY + 20, 180, currentY + 20);
    doc.text("Firma del Vendedor", 130, currentY + 25);
  
    doc.save("contrato_renderizado.pdf");
  };

  const getDisclaimerByContractName = (contractName) => {
    const name = contractName.toLowerCase();
  
    if (name.includes("compraventa")) {
      return "Este contrato de compraventa se rige por el Código Civil Español y regula la transmisión de bienes entre las partes.";
    }
    if (name.includes("arrendamiento")) {
      return "Este contrato de arrendamiento se rige por la Ley de Arrendamientos Urbanos (LAU) y regula la cesión temporal del uso de bienes.";
    }
    if (name.includes("arras")) {
      return "Este contrato de arras regula el compromiso previo a la compraventa de un bien, estableciendo consecuencias en caso de incumplimiento.";
    }
  
    // Si no detectamos ningún patrón
    return "Este contrato se redacta conforme a la legislación vigente en España. Las partes firmantes acuerdan cumplir las obligaciones que se derivan del mismo.";
  };
  

  return (
    <div className="copilot-layout">
      <BackButton onClick={onBack} />
      <div className="editor-container">
        <div className="header-bar">
          <div>
            <h2 className="copilot-title">Copilot de Contratos</h2>
            <p className="copilot-subtitle">Redacción jurídica asistida por IA en tiempo real.</p>
          </div>
          <div className="toolbar">
            {!isPreviewMode ? (
              <>
                <input
                  tyoe="text"
                  value={contractName}
                  onChange={(e) => setContractName(e.target.value)}
                  placeholder="Tipo de contrato (Ej: Compraventa, prestación de servicios)"
                  className="contract-input"
                />
                <button className="toolbar-btn" onClick={handleVerifyContract}>
                  {verifying ? "Verificando..." : "Verificar"}
                </button>
                <button className="toolbar-btn" onClick={handleRunLegalCheck}>
                  Revisión Jurídica
                </button>
                <button className="toolbar-btn" onClick={handleRenderContract}>
                  {loadingRender ? "Renderizando..." : "Vista Previa Bonita"}
                </button>
              </>
            ) : (
              <>
                <button className="toolbar-btn" onClick={() => setIsPreviewMode(false)}>
                  Volver a Editar
                </button>
                <button className="toolbar-btn" onClick={handleSaveRenderedContract}>
                  Guardar Contrato Bonito
                </button>
              </>
            )}
          </div>
        </div>

        <div className="main-panel">
          {!isPreviewMode ? (
            <textarea
              placeholder="Escribe tu contrato aquí..."
              value={inputText}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              className="editor-textarea"
            />
          ) : (
            <div
              className="rendered-contract-preview"
              dangerouslySetInnerHTML={{ __html: renderedContract }}
            />
          )}

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

            {legalAnalysis && (
              <>
                <h3 className="suggestion-title">🧾 Informe Jurídico:</h3>
                <p className="suggestion-text">{legalAnalysis}</p>
              </>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
};

export default Copilot;