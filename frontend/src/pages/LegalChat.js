import React, { useState, useRef, useEffect } from "react";
import "../styles/pages/LegalChat.css";
import BackButton from "../components/BackButton";
import { fetchLegalResponse } from "../api/legalChatAPI";
import jsPDF from "jspdf";

const formatLegalResponse = (text) => {
  const lines = text.split(/\n+/);
  return lines.map((line, i) => {
    if (line.startsWith("Respuesta:")) return <h3 key={i}>Respuesta</h3>;
    if (line.startsWith("📚")) return <h3 key={i}>Leyes citadas</h3>;
    if (line.startsWith("🔎")) return <h3 key={i}>Palabras clave</h3>;
    if (line.trim() === "---") return <hr key={i} />;
    const formattedLine = line.replace(/\*\*(.+?)\*\*/g, (_, boldText) => `<strong>${boldText}</strong>`);
    return <p key={i} dangerouslySetInnerHTML={{ __html: formattedLine }} />;
  });
};

const LegalChat = ({ onBack }) => {
  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [thinkingDots, setThinkingDots] = useState(".");
  const [typingResponse, setTypingResponse] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [hoveredCopy, setHoveredCopy] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const chatEndRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const [expertMode, setExpertMode] = useState(false);
  const [darkMode, setDarkMode]=useState(false);

  const stopResponse = () => {
    clearInterval(typingIntervalRef.current);
    setTypingResponse("");
    setIsThinking(false);
    setLoading(false);
  };

  const toggleMode=()=>{
    setExpertMode(!expertMode);
    setDarkMode(!darkMode);
  }

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleDownloadPDF = (text, inputText = "") => {
    const doc = new jsPDF("p", "pt", "a4");
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 50;
    let y = 60;

    // Cambiar fuente a Times New Roman
    doc.setFont("times", "normal");

    // Header con color y logo
    doc.setFillColor("#80002a");
    doc.rect(0, 0, pageWidth, 60, "F");
    doc.setFont("times", "bold");
    doc.setFontSize(16);
    doc.setTextColor("#ffffff");
    doc.text("Themis · Asistente Legal", margin, 38);
    y = 80;

    // Información adicional sobre la consulta
    doc.setFont("times", "normal");
    doc.setFontSize(10);
    doc.setTextColor(50);
    doc.text(`Consulta: ${inputText}`, margin, y);
    y += 20;
    doc.text(`Fecha de generación: ${new Date().toLocaleString()}`, margin, y);
    y += 30;

    // Estilo para las respuestas
    doc.setFontSize(12);
    const lines = text.split(/\n+/);
    lines.forEach((line) => {
      const cleanLine = line.replace(/[📚🔎🧾]/g, "").trim();
      if (!cleanLine) {
        y += 10;
        return;
      }

      // Si el texto contiene "Respuesta", "Leyes citadas" o "Palabras clave", se pone en negrita
      if (cleanLine.toLowerCase().startsWith("respuesta:") || cleanLine.startsWith("Leyes citadas") || cleanLine.startsWith("Palabras clave")) {
        doc.setFont("times", "bold");
        doc.setFontSize(13);
        doc.setTextColor("#80002a");
      } else {
        doc.setFont("times", "normal");
        doc.setFontSize(12);
        doc.setTextColor(20);
      }

      const wrapped = doc.splitTextToSize(cleanLine.replace(/\*\*(.+?)\*\*/g, "$1"), pageWidth - 2 * margin);
      doc.text(wrapped, margin, y);
      y += wrapped.length * 16 + 6;

      // Si se pasa de la página, añadir una nueva
      if (y > doc.internal.pageSize.getHeight() - 60) {
        doc.addPage();
        y = 60;
      }
    });

    // Pie de página con texto en cursiva
    doc.setFont("times", "italic");
    doc.setFontSize(9);
    doc.setTextColor(100);
    doc.text(
      "Este informe ha sido generado automáticamente por el asistente de IA de Themis. No sustituye asesoría legal profesional.",
      margin,
      doc.internal.pageSize.getHeight() - 30,
      { maxWidth: pageWidth - 2 * margin }
    );

    // Usar las palabras clave para generar el nombre del archivo
    const keywords = inputText
      .toLowerCase()
      .replace(/[^\w\s]/g, "")
      .split(/\s+/)
      .filter((word) => word.length > 4)
      .slice(0, 4)
      .join("_") || "informe_themis";

    // Generar y abrir el PDF en una nueva pestaña
    const blob = doc.output("blob");
    const blobUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = `${keywords}.pdf`; // Asignar el nombre adecuado con palabras clave
    link.target = "_blank"; // Abrir en nueva pestaña
    link.click();
};


  const handleSend = async () => {
    const trimmed = userInput.trim();

    if (trimmed.length < 3) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "⚠️ Por favor, escribe una consulta más larga para obtener una respuesta útil."
        }
      ]);
      return;
    }

    const userMsg = { role: "user", text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setUserInput("");
    setLoading(true);
    setIsThinking(true);
    setTypingResponse("");

    const modeInstruction = expertMode
      ? "Responde como un jurista experto, utilizando lenguaje técnico y preciso, sin simplificar."
      : "Responde de forma clara y explicativa, como si se lo explicaras a un cliente sin conocimientos jurídicos.";

    const messagePayload = [
      { role: "system", content: modeInstruction },
      { role: "user", content: trimmed }
    ];
    console.log("🧠 Enviando al backend:", JSON.stringify(messagePayload, null, 2));

    try {
      const response = await fetchLegalResponse(messagePayload);

      console.log("📥 Respuesta cruda recibida:", response);

      if (!response || typeof response !== "string" || !response.trim()) {
        setMessages((prev) => [...prev, { role: "assistant", text: "ℹ️ El servidor no ha proporcionado ninguna respuesta." }]);
        return;
      }

      let index = 0;
      let generated = "";

      typingIntervalRef.current = setInterval(() => {
        generated += response.charAt(index);
        setTypingResponse(generated);
        index++;

        if (index >= response.length) {
          clearInterval(typingIntervalRef.current);
          setTypingResponse("");
          setMessages((prev) => [...prev, { role: "assistant", text: response, prompt: trimmed }]);
          setIsThinking(false);
          setLoading(false);
        }
      }, 20);

    } catch (error) {
      setIsThinking(false);
      setTypingResponse("");
      setMessages((prev) => [...prev, {
        role: "assistant",
        text: "❌ Error al obtener respuesta del servidor."
      }]);
      console.error("🚨 Error al obtener respuesta:", error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Escape") stopResponse();
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typingResponse]);

  useEffect(() => {
    if (!isThinking) return;
    const interval = setInterval(() => {
      setThinkingDots((prev) => (prev.length === 3 ? "." : prev + "."));
    }, 500);
    return () => clearInterval(interval);
  }, [isThinking]);

  return (
    <div className="legal-chat-layout">
        <div className="chat-top-bar">
            <BackButton onClick={onBack} />
            <div className="chat-header">
            <h2 className="chat-title">Asistente Legal</h2>
            <p className="chat-subtitle">Realiza tus consultas legales y recibe respuestas fundamentadas en segundos.</p>
            </div>
            <div className="mode-switch">
            <label>
                <input 
                type="checkbox" 
                checked={expertMode} 
                onChange={() => setExpertMode(!expertMode)} 
                />
                <span className="switch-label">{expertMode ? "Modo experto" : "Modo explicativo"}</span>
            </label>
            </div>
            <button 
            className="jurisprudencia-button" 
            onClick={() => window.open("https://www.poderjudicial.es/search/indexAN.jsp", "_blank")}
            >
            Buscar Jurisprudencia
            </button>
        </div>

        <div className="legal-chat-wrapper">
            <div className="legal-chat-box">
            {messages.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role}`}>
                {msg.role === "assistant" ? (
                    <div className="formatted-response">
                    {formatLegalResponse(msg.text)}
                    <div className="bubble-controls">
                        <button 
                        className="copy-button" 
                        onClick={() => handleCopy(msg.text, i)} 
                        onMouseEnter={() => setHoveredCopy(i)} 
                        onMouseLeave={() => setHoveredCopy(null)}
                        >
                        📄
                        </button>
                        <button 
                        className="download-button" 
                        onClick={() => handleDownloadPDF(msg.text, msg.prompt)} 
                        title="Descargar informe"
                        >
                        ⬇️
                        </button>
                        {copiedIndex === i && <span className="tooltip copied">¡Copiado!</span>}
                        {hoveredCopy === i && <span className="tooltip">Copiar</span>}
                    </div>
                    </div>
                ) : (
                    <span>{msg.text}</span>
                )}
                </div>
            ))}

            {typingResponse && <div className="chat-bubble assistant formatted-response">{formatLegalResponse(typingResponse)}</div>}
            {!typingResponse && isThinking && <div className="chat-bubble assistant"><span>Escribiendo{thinkingDots}</span></div>}
            <div ref={chatEndRef} />
            </div>

            <div className="chat-input-area">
            <textarea 
                value={userInput} 
                onChange={(e) => setUserInput(e.target.value)} 
                onKeyDown={handleKeyDown} 
                placeholder="¿Qué necesitas saber?" 
                rows={2} 
            />
            {loading ? <button onClick={stopResponse} className="stop-button">⏹</button> : <button onClick={handleSend}>Enviar</button>}
            </div>
        </div>
    </div>

  );
};

export default LegalChat;
