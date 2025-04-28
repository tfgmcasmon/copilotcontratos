import React, { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import Home from "./pages/Home";
import Copilot from "./pages/Copilot";
import LegalChat from "./pages/LegalChat";
import VisionBoard from "./pages/VisionBoard";  

function App() {
    const [currentView, setCurrentView] = useState("home");

    const handleBack = () => setCurrentView("home");

    const renderView = () => {
        switch (currentView) {
            case "copilot":
                return <Copilot onBack={handleBack} />;
            case "legalChat":
                return <LegalChat onBack={handleBack} />;
            case "visionBoard":                       
                return <VisionBoard />;
            default:
                return <Home onNavigate={setCurrentView} />;
        }
    };

    return (
        <div className="app-container">
            <Header onNavigate={setCurrentView} />
            {renderView()}
        </div>
    );
}

export default App;
