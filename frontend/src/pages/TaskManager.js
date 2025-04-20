import React, { useEffect, useState } from "react";
import axios from "axios";
import "./TaskManager.css";

const TaskManager = ({ onBack }) => {
    const [tareas, setTareas] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [nuevaTarea, setNuevaTarea] = useState({
        titulo: "",
        tipo: "",
        cliente: "",
        urgencia: "media",
        fecha_limite: "",
        descripcion: ""
    });

    useEffect(() => {
        axios.get("http://127.0.0.1:8080/gestor_tareas/asignaciones")
            .then(response => {
                console.log("✅ Datos recibidos:", response.data);
                setTareas(response.data?.asignaciones || []);
            })
            .catch(error => {
                console.error("❌ Error al cargar las tareas:", error);
            });
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNuevaTarea({ ...nuevaTarea, [name]: value });
    };

    const handleNuevaTarea = async () => {
        try {
            const response = await axios.post("http://127.0.0.1:8080/gestor_tareas/nueva", nuevaTarea);
            if (response.data && response.data.resultado) {
                setTareas([...tareas, response.data.resultado]);
                setShowModal(false);
                setNuevaTarea({ titulo: "", tipo: "", cliente: "", urgencia: "media", fecha_limite: "" });
            }
        } catch (error) {
            console.error("❌ Error al añadir tarea:", error);
        }
    };

    return (
        <div className="task-manager">
            <header className="header">
                <h1 className="title">Gestor de Tareas Inteligente</h1>
                <div>
                    <button className="add-button" onClick={() => setShowModal(true)}>➕ Nueva tarea</button>
                    <button className="back-button" onClick={onBack}>Volver</button>
                </div>
            </header>

            <div className="task-board">
                {tareas.map((tarea, index) => (
                    <div key={tarea.id || index} className="task-card">
                        <h2 className="task-title">{tarea.titulo}</h2>
                        <p><strong>Cliente:</strong> {tarea.cliente}</p>
                        <p><strong>Asignado a:</strong> {tarea.asignado ? `${tarea.asignado} (${tarea.rol})` : "No asignado"}</p>
                        <p><strong>Fecha sugerida:</strong> {tarea.fecha_sugerida || "-"}</p>
                        <p><strong>Fecha de inicio estimada:</strong> {tarea.fecha_inicio || "-"}</p>
                        <p><strong>Fecha de fin estimada:</strong> {tarea.fecha_fin || "-"}</p>
                        <p><strong>Urgencia:</strong> {tarea.urgencia?.toUpperCase()}</p>
                        {tarea.descripcion && (
                            <p><strong>Descripción:</strong> {tarea.descripcion}</p>
                        )}
                    </div>
                ))}
            </div>


            {showModal && (
                <div className="modal">
                    <div className="modal-content">
                        <h2>Crear nueva tarea</h2>
                        <input type="text" name="titulo" placeholder="Título" value={nuevaTarea.titulo} onChange={handleInputChange} />
                        <input type="text" name="tipo" placeholder="Tipo (redaccion, traduccion, firma...)" value={nuevaTarea.tipo} onChange={handleInputChange} />
                        <input type="text" name="cliente" placeholder="Cliente" value={nuevaTarea.cliente} onChange={handleInputChange} />
                        <select name="urgencia" value={nuevaTarea.urgencia} onChange={handleInputChange}>
                            <option value="alta">Alta</option>
                            <option value="media">Media</option>
                            <option value="baja">Baja</option>
                        </select>
                        <input type="date" name="fecha_limite" value={nuevaTarea.fecha_limite} onChange={handleInputChange} />
                        <div className="modal-actions">
                        <textarea
                            name="descripcion"
                            placeholder="Descripción detallada de la tarea"
                            value={nuevaTarea.descripcion}
                            onChange={handleInputChange}
                        />
                            <button onClick={handleNuevaTarea}>Guardar</button>
                            <button onClick={() => setShowModal(false)}>Cancelar</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TaskManager;
