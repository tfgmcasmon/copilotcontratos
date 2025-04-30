import React from 'react';
import TaskCard from './TaskCard'; // Asegúrate de que TaskCard se está importando

const TeamColumn = ({ member, tasks, handleTaskStatusChange }) => {
  return (
    <div className="team-column">
      <h3>{member.nombre}</h3>
      <div>
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            handleTaskStatusChange={handleTaskStatusChange}  // Pasamos la función de cambio de estado aquí
          />
        ))}
      </div>
    </div>
  );
};

export default TeamColumn;
