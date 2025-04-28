import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/pages/VisionBoard.css';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import BackButton from "../components/BackButton";
import TeamColumn from '../components/TeamColumn';
import AlertCard from '../components/AlertCard';
import SuggestionCard from '../components/SuggestionCard';

import { fetchUsers, fetchTasks, fetchAlerts, fetchSuggestions } from '../api/VisionBoardAPI';

function VisionBoard({ onBack }) {
  const [teamMembers, setTeamMembers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [filter, setFilter] = useState("Todos"); // Filtro de estado de tareas
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const usersData = await fetchUsers();
        const tasksData = await fetchTasks();
        const alertsData = await fetchAlerts();
        const suggestionsData = await fetchSuggestions();

        setTeamMembers(usersData);
        const assignedTasks = assignTasksToMembers(tasksData, usersData);
        setTasks(assignedTasks);
        setAlerts(alertsData);
        setSuggestions(suggestionsData);
      } catch (error) {
        console.error("Error al cargar los datos del Vision Board", error);
      }
    };

    loadData();
  }, []);

  // Función para asignar tareas a miembros con menos carga
  const assignTasksToMembers = (tasks, teamMembers) => {
    let workload = teamMembers.reduce((acc, member) => {
      acc[member.id] = 0;
      return acc;
    }, {});

    tasks.forEach(task => {
      if (task.estado !== "Terminada") {
        workload[task.asignado_a] += task.estimacion_horas;
      }
    });

    tasks.forEach(task => {
      if (task.estado === "No empezada") {
        const memberWithLeastWorkload = Object.keys(workload).reduce((prev, curr) => {
          return workload[prev] < workload[curr] ? prev : curr;
        });

        task.asignado_a = memberWithLeastWorkload;
        workload[memberWithLeastWorkload] += task.estimacion_horas;
      }
    });

    return tasks;
  };

  // Función para obtener el estado de la tarea (urgente o próxima a vencerse)
  const getTaskStatus = (task) => {
    const now = new Date();
    const deadline = new Date(task.deadline);

    if (task.estado === "No empezada" && deadline < now) {
      return "urgente";
    }

    if (task.estado === "No empezada" && deadline - now < 2 * 24 * 60 * 60 * 1000) {
      return "próxima";
    }

    return "normal";
  };

  // Cambiar el filtro de estado
  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };

  // Filtrar tareas según el estado
  const filteredTasks = tasks.filter(task => {
    if (filter === "Todos") return true;
    return task.estado === filter;
  });

  // Manejar el cambio de tareas con Drag-and-Drop
  const onDragEnd = (result) => {
    const { destination, source } = result;

    if (!destination) return;

    const tasksCopy = [...tasks];
    const [movedTask] = tasksCopy.splice(source.index, 1);
    tasksCopy.splice(destination.index, 0, movedTask);
    setTasks(tasksCopy);
  };

  // Función para manejar el clic en el botón de volver
  const handleBack = () => {
    navigate("/home");
  };

  return (
    <div className="vision-board">
      <BackButton onClick={handleBack} />
      <h1 className="vision-board-title">Vision Board del Equipo</h1>

      <div className="filters">
        <select onChange={handleFilterChange}>
          <option value="Todos">Todos</option>
          <option value="No empezada">No empezada</option>
          <option value="En curso">En curso</option>
          <option value="Terminada">Terminada</option>
        </select>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="kanban-board" direction="horizontal">
          {(provided) => (
            <div className="kanban-board" ref={provided.innerRef} {...provided.droppableProps}>
              {teamMembers.length > 0 ? (
                teamMembers.map((member, index) => (
                  <Draggable key={member.id} draggableId={member.id} index={index}>
                    {(provided) => (
                      <div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                        <TeamColumn
                          key={member.id}
                          member={member}
                          tasks={filteredTasks.filter(task => task.asignado_a === member.id)}
                          getTaskStatus={getTaskStatus}
                        />
                      </div>
                    )}
                  </Draggable>
                ))
              ) : (
                <p className="no-tasks">No hay miembros de equipo.</p>
              )}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <div className="alert-section">
        <h2 className="section-title">Alertas Críticas</h2>
        <div className="alert-grid">
          {alerts.map(alert => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      </div>

      <div className="suggestion-section">
        <h2 className="section-title">Sugerencias de Optimización</h2>
        <div className="suggestion-grid">
          {suggestions.map(suggestion => (
            <SuggestionCard key={suggestion.id} suggestion={suggestion} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default VisionBoard;
