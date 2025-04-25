import React, { useState, useRef, useEffect } from "react";
import "../styles/pages/LegalChat.css";
import BackButton from "../components/BackButton";
import { fetchLegalResponse } from "../api/legalChatAPI";
import jsPDF from "jspdf";

const formatLegalResponse = (text) => {
  const lines = text.split(/\n+/);
  return lines.map((line, i) => {
    if (line.startsWith("Respuesta:")) return <h3 key={i}>🧾 Respuesta</h3>;
    if (line.startsWith("📚")) return <h3 key={i}>📚 Leyes citadas</h3>;
    if (line.startsWith("🔎")) return <h3 key={i}>🔎 Palabras clave</h3>;
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

  const stopResponse = () => {
    clearInterval(typingIntervalRef.current);
    setTypingResponse("");
    setIsThinking(false);
    setLoading(false);
  };

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

    doc.setFillColor("#80002a");
    doc.rect(0, 0, pageWidth, 60, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.setTextColor("#ffffff");
    doc.text("Themis · Asistente Legal", margin, 38);
    y = 80;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(50);
    doc.text(`Consulta: ${inputText}`, margin, y);
    y += 20;
    doc.text(`Fecha de generación: ${new Date().toLocaleString()}`, margin, y);
    y += 30;

    doc.setFontSize(12);
    const lines = text.split(/\n+/);
    lines.forEach((line) => {
      const cleanLine = line.replace(/[📚🔎🧾]/g, "").trim();
      if (!cleanLine) {
        y += 10;
        return;
      }
      if (cleanLine.toLowerCase().startsWith("respuesta:") || cleanLine.startsWith("Leyes citadas") || cleanLine.startsWith("Palabras clave")) {
        doc.setFont("helvetica", "bold");
        doc.setFontSize(13);
        doc.setTextColor("#80002a");
      } else {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(12);
        doc.setTextColor(20);
      }
      const wrapped = doc.splitTextToSize(cleanLine.replace(/\*\*(.+?)\*\*/g, "$1"), pageWidth - 2 * margin);
      doc.text(wrapped, margin, y);
      y += wrapped.length * 16 + 6;
      if (y > doc.internal.pageSize.getHeight() - 60) {
        doc.addPage();
        y = 60;
      }
    });

    doc.setFont("helvetica", "italic");
    doc.setFontSize(9);
    doc.setTextColor(100);
    doc.text(
      "Este informe ha sido generado automáticamente por el asistente de IA de Themis. No sustituye asesoría legal profesional.",
      margin,
      doc.internal.pageSize.getHeight() - 30,
      { maxWidth: pageWidth - 2 * margin }
    );

    const keywords = inputText
      .toLowerCase()
      .replace(/[^\w\s]/g, "")
      .split(/\s+/)
      .filter((word) => word.length > 4)
      .slice(0, 4)
      .join("_") || "informe_themis";

    const blob = doc.output("blob");
    const blobUrl = URL.createObjectURL(blob);
    window.open(blobUrl, "_blank");
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

    const messagePayload = [{ role: "user", content: trimmed }];
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
        <button className="jurisprudencia-button" onClick={() => window.open("https://www.poderjudicial.es/search/indexAN.jsp", "_blank")}>Buscar Jurisprudencia</button>
      </div>

      <div className="legal-chat-wrapper">
        <div className="legal-chat-box">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              {msg.role === "assistant" ? (
                <div className="formatted-response">
                  {formatLegalResponse(msg.text)}
                  <div className="bubble-controls">
                    <button className="copy-button" onClick={() => handleCopy(msg.text, i)} onMouseEnter={() => setHoveredCopy(i)} onMouseLeave={() => setHoveredCopy(null)}>
                      📄
                    </button>
                    <button className="download-button" onClick={() => handleDownloadPDF(msg.text, msg.prompt)} title="Descargar informe">
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
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-area">
          <textarea value={userInput} onChange={(e) => setUserInput(e.target.value)} onKeyDown={handleKeyDown} placeholder="¿Qué necesitas saber?" rows={2} />
          {loading ? <button onClick={stopResponse} className="stop-button">⏹</button> : <button onClick={handleSend}>Enviar</button>}
        </div>
      </div>
    </div>
  );
};

export default LegalChat;