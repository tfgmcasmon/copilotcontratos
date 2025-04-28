import React from "react";
import "../styles/components/TeamColumn.css";
import TaskCard from "./TaskCard";

function TeamColumn({ member, tasks }) {
    return (
        <div className="team-column">
            <h2 className="team-column-title">{member.nombre}</h2>
            <div className="team-column-tasks">
                {tasks.length > 0 ? (
                    tasks.map(task => (
                        <TaskCard key={task.id} task={task} />
                    ))
                ) : (
                    <p className="team-column-empty">Sin tareas asignadas</p>
                )}
            </div>
        </div>
    );
}

export default TeamColumn;
