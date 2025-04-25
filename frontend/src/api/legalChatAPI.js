export const fetchLegalResponse = async (messages) => {
    console.log("📤 Payload que se enviará al backend:", JSON.stringify({ messages }, null, 2));
  
    const response = await fetch("http://127.0.0.1:8080/legalChat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
  
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || "Error en la respuesta del servidor");
    }
  
    const data = await response.json();
    return data.response || data.result || "";
  };
  