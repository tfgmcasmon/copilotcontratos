def get_contract_context(contract_type):
    """
    Devuelve un contexto legal base según el tipo de contrato.
    """
    if contract_type == "arras":
        return "Estás redactando un contrato de arras. En este tipo de contrato se establece un acuerdo previo de compra de un inmueble, detallando condiciones y consecuencias del incumplimiento."
    elif contract_type == "compraventa":
        return "Estás redactando un contrato de compraventa de un bien inmueble. El documento debe incluir identificación de las partes, descripción del inmueble, precio acordado y obligaciones respectivas."
    elif contract_type == "arrendamiento":
        return "Estás redactando un contrato de arrendamiento de un inmueble. Debe especificar duración, renta, uso permitido, y condiciones de resolución anticipada."
    else:
        return "Estás redactando un contrato legal. Mantén precisión jurídica, cláusulas claras, y evita ambigüedades."
