import React from "react";
import "../styles/components/TaskCard.css";

function TaskCard({ task }) {
    return (
        <div className="task-card">
            <h3 className="task-card-title">{task.titulo}</h3>
            <p className="task-card-type">{task.tipo}</p>
            <p className="task-card-status">{task.estado}</p>
        </div>
    );
}

export default TaskCard;
