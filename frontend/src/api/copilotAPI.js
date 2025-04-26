// src/api/copilotAPI.js
export const fetchContractTitle = async (contractName, setInputText, setContractName, setErrorMessage) => {
  try {
    const response = await fetch("http://127.0.0.1:8080/generateContractContext", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_name: contractName}),
    });

    if (response.ok) {
      const data = await response.json();
      const title = data.prompt.split("\n")[0];
      setInputText(title || "");
      setContractName(contractName);
      setErrorMessage("");
    } else {
      setErrorMessage("Error al obtener el título del contrato.");
    }
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    setErrorMessage("No se pudo conectar al servidor.");
  }
};

export const fetchAutocomplete = async (currentText, contractName, setAutocompleteText) => {
  try {
    const response = await fetch("http://127.0.0.1:8080/trackChanges", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        changes: currentText,
        contract_name: contractName
      }),
    });

    if (response.ok) {
      const data = await response.json();
      let suggestion = data.autocomplete || "";

      // 🔥 NUEVO: Cortar si hay doble salto de línea
      if (suggestion.includes("\n\n")) {
        suggestion = suggestion.split("\n\n")[0];
      }

      // 🔥 NUEVO: Cortar si sugerencia es demasiado larga
      if (suggestion.length > 300) {
        suggestion = "";
      }

      // 🔥 NUEVO: Limpiar espacios
      suggestion = suggestion.replace(/\s{2,}/g, " ").trim();

      setAutocompleteText(suggestion);
    } else {
      console.error("Error al obtener sugerencia de autocompletado");
      setAutocompleteText("");
    }
  } catch (error) {
    console.error("Error al conectar para autocompletar:", error);
    setAutocompleteText("");
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
