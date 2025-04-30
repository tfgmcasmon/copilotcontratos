import React, { useEffect, useState } from 'react';
import '../styles/pages/VisionBoard.css';
import BackButton from "../components/BackButton";
import TeamColumn from '../components/TeamColumn';
import AlertCard from '../components/AlertCard';
import SuggestionCard from '../components/SuggestionCard';
import { fetchUsers, fetchTasks, fetchAlerts, fetchSuggestions, updateTaskStatus } from '../api/VisionBoardAPI'; 

function VisionBoard({ onBack }) {
  const [teamMembers, setTeamMembers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [filter, setFilter] = useState("Todos");

  useEffect(() => {
    const loadData = async () => {
      try {
        const usersData = await fetchUsers();
        const tasksData = await fetchTasks();
        const alertsData = await fetchAlerts();
        const suggestionsData = await fetchSuggestions();

        setTeamMembers(usersData);
        setTasks(tasksData);
        setAlerts(alertsData);
        setSuggestions(suggestionsData);
      } catch (error) {
        console.error("Error al cargar los datos del Vision Board", error);
      }
    };

    loadData();
  }, []);

  // Función para manejar el cambio de estado de la tarea
  const handleTaskStatusChange = async (taskId, newStatus) => {
    try {
      const updatedTask = await updateTaskStatus(taskId, newStatus);
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, estado: newStatus } : task
        )
      );
    } catch (error) {
      console.error("Error al cambiar el estado de la tarea:", error);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === "Todos") return true;
    return task.estado === filter;
  });

  return (
    <div className="vision-board">
      <BackButton onClick={onBack} />
      <h1 className="vision-board-title">Vision Board del Equipo</h1>

      <div className="filters">
        <select onChange={(e) => setFilter(e.target.value)}>
          <option value="Todos">Todos</option>
          <option value="No empezada">No empezada</option>
          <option value="En curso">En curso</option>
          <option value="Terminada">Terminada</option>
        </select>
      </div>

      <div className="kanban-board">
        {teamMembers.length > 0 ? (
          teamMembers.map((member) => (
            <TeamColumn
              key={member.id}
              member={member}
              tasks={filteredTasks.filter((task) => task.asignado_a === member.id)}
              handleTaskStatusChange={handleTaskStatusChange}  // Asegúrate de pasar esta función a los componentes hijos
            />
          ))
        ) : (
          <p className="no-tasks">No hay miembros de equipo.</p>
        )}
      </div>

      <div className="alert-section">
        <h2 className="section-title">Alertas Críticas</h2>
        <div className="alert-grid">
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      </div>

      <div className="suggestion-section">
        <h2 className="section-title">Sugerencias de Optimización</h2>
        <div className="suggestion-grid">
          {suggestions.map((suggestion) => (
            <SuggestionCard key={suggestion.id} suggestion={suggestion} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default VisionBoard;
