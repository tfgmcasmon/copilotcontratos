import React from 'react';

const TaskCard = ({ task, handleTaskStatusChange }) => {
  const handleStatusChange = (e) => {
    const newStatus = e.target.value;
    handleTaskStatusChange(task.id, newStatus);  // Llamamos a la función para actualizar el estado
  };

  return (
    <div className={`task-card priority-${task.prioridad.toLowerCase()}`}>
      <h3>{task.titulo}</h3>
      <p>{task.descripcion}</p>
      <p>Prioridad: {task.prioridad}</p>

      {/* Dropdown para cambiar el estado de la tarea */}
      <select value={task.estado} onChange={handleStatusChange}>
        <option value="No empezada">No empezada</option>
        <option value="En curso">En curso</option>
        <option value="Terminada">Terminada</option>
      </select>
    </div>
  );
};

export default TaskCard;
