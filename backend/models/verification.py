import re
from collections import defaultdict

# Función para validar letra correcta de DNI
def validar_dni_letra(dni):
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    try:
        numero = int(dni[:-1])
        letra_correcta = letras[numero % 23]
        return dni[-1].upper() == letra_correcta
    except:
        return False

# Función para limpiar texto antes de analizar
def limpiar_texto(text):
    text = re.sub(r'N\.I\.F\.|n\.i\.f\.|Número|número|nº|número de identificación|identificación', '', text, flags=re.IGNORECASE)
    text = text.replace(".", " ").replace(",", " ").replace(":", " ").replace(";", " ")
    return text

def verify_contract_data(contract_text):
    issues = []
    warnings = []

    # 🔥 Paso 1: Limpiar texto
    clean_text = limpiar_texto(contract_text)

    # 🔥 Paso 2: Escanear todo el texto
    posibles_dnis = re.findall(r'\b\d{7,8}[A-Za-z]\b', clean_text)
    posibles_telefonos = re.findall(r'\b6\d{8}\b|\b7\d{8}\b', clean_text)
    posibles_referencias = re.findall(r'\b\d{14}\b', clean_text)
    posibles_direcciones = re.findall(r'\b(calle|avenida|plaza|camino|paseo)\b', clean_text, re.IGNORECASE)

    # 🔥 Paso 3: Validar DNIs
    if not posibles_dnis:
        issues.append("❌ No se detectaron DNIs válidos en el contrato.")
    else:
        dnis_correctos = []
        dnis_incorrectos = []
        for dni in posibles_dnis:
            if not re.fullmatch(r'\d{8}[A-Za-z]', dni):
                issues.append(f"❌ El DNI '{dni}' tiene formato inválido (deben ser exactamente 8 cifras + 1 letra).")
                dnis_incorrectos.append(dni)
            else:
                dnis_correctos.append(dni)

        # Validar letras de DNIs correctos
        for dni in dnis_correctos:
            if not validar_dni_letra(dni):
                issues.append(f"❌ El DNI '{dni}' tiene letra incorrecta.")

        # Detectar duplicidad de DNIs
        dnis_repetidos = defaultdict(int)
        for dni in dnis_correctos:
            dnis_repetidos[dni] += 1
        for dni, count in dnis_repetidos.items():
            if count > 1:
                issues.append(f"❌ El DNI '{dni}' aparece duplicado en el contrato (potencial conflicto de identidad).")

    # 🔥 Paso 4: Validar teléfonos
    if not posibles_telefonos:
        warnings.append("⚠️ No se detectaron teléfonos en el contrato.")
    else:
        telefonos_repetidos = defaultdict(int)
        for tel in posibles_telefonos:
            telefonos_repetidos[tel] += 1
        for tel, count in telefonos_repetidos.items():
            if count > 1:
                warnings.append(f"⚠️ El teléfono '{tel}' está asociado a múltiples personas o se repite.")

    # 🔥 Paso 5: Validar referencias catastrales
    if not posibles_referencias:
        warnings.append("⚠️ No se detectó ninguna referencia catastral en el contrato (puede ser necesaria).")
    else:
        referencias_repetidas = defaultdict(int)
        for ref in posibles_referencias:
            referencias_repetidas[ref] += 1
        for ref, count in referencias_repetidas.items():
            if count > 1:
                issues.append(f"❌ La referencia catastral '{ref}' aparece asignada a múltiples propiedades distintas.")

    # 🔥 Paso 6: Validar direcciones
    if not posibles_direcciones:
        warnings.append("⚠️ No se detectaron direcciones asociadas a personas o inmuebles en el contrato.")

    # 🔥 Resultado final
    if not issues and not warnings:
        return ["✅ No se detectaron problemas en los datos del contrato."]
    else:
        return issues + warnings
