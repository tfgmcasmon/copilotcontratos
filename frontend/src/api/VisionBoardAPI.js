// src/api/VisionBoardAPI.js

export const fetchUsers = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/users/');
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error("Error al obtener usuarios");
      }
    } catch (error) {
      console.error("Error en la conexión con el backend:", error);
      throw error;
    }
  };
  
  export const fetchTasks = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/taskmanager/tasks/');
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error("Error al obtener tareas");
      }
    } catch (error) {
      console.error("Error en la conexión con el backend:", error);
      throw error;
    }
  };
  
  export const fetchAlerts = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/taskmanager/alerts/');
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error("Error al obtener alertas");
      }
    } catch (error) {
      console.error("Error en la conexión con el backend:", error);
      throw error;
    }
  };
  
  export const fetchSuggestions = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/taskmanager/suggestions/');
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error("Error al obtener sugerencias");
      }
    } catch (error) {
      console.error("Error en la conexión con el backend:", error);
      throw error;
    }
  };
  
  // Función para actualizar el estado de una tarea
export const updateTaskStatus = async (taskId, newStatus) => {
  try {
    const response = await fetch(`http://127.0.0.1:8080/taskmanager/tasks/${taskId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ estado: newStatus }),
    });

    if (response.ok) {
      const data = await response.json();
      return data; // Devuelve los datos actualizados de la tarea
    } else {
      throw new Error('Error al actualizar la tarea');
    }
  } catch (error) {
    console.error('Error en la conexión con el backend:', error);
    throw error;
  }
};
