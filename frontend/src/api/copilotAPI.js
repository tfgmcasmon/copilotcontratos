// src/api/copilotAPI.js
export const fetchContractTitle = async (type, setInputText, setContractType, setErrorMessage) => {
  try {
    const response = await fetch("http://127.0.0.1:8080/generateContractContext", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_type: type }),
    });

    if (response.ok) {
      const data = await response.json();
      const title = data.prompt.split("\n")[0];
      setInputText(title || "");
      setContractType(type);
      setErrorMessage("");
    } else {
      setErrorMessage("Error al obtener el título del contrato.");
    }
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    setErrorMessage("No se pudo conectar al servidor.");
  }
};

export const fetchAutocomplete = async (text, type, setAutocompleteText) => {
  try {
    const response = await fetch("http://127.0.0.1:8080/trackChanges", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ changes: text, contract_type: type }),
    });

    if (response.ok) {
      const data = await response.json();
      setAutocompleteText(data.autocomplete || "");
    } else {
      console.error("Error al obtener sugerencia:", response.statusText);
    }
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
  }
};

export const verifyContractData = async (text, setResult, setVerifying) => {
  setVerifying(true);
  setResult(null);

  try {
    const response = await fetch("http://127.0.0.1:8080/verifyContractData", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_text: text }),
    });

    const data = await response.json();

    if (response.ok) {
      if (Array.isArray(data.issues) && data.issues.length > 0) {
        setResult({ status: "warning", issues: data.issues });
      } else if (data.message) {
        setResult({ status: "ok", message: data.message });
      } else {
        setResult({ status: "ok", message: "✅ Todo parece correcto." });
      }
    } else {
      setResult({ status: "error", message: data.error || "❌ Error al verificar los datos." });
    }
  } catch (err) {
    console.error("❌ Error al conectar con el backend:", err);
    setResult({ status: "error", message: "❌ No se pudo conectar al servidor." });
  } finally {
    setVerifying(false);
  }
};
