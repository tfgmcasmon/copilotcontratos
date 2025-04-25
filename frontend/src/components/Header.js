import React from "react";
import "../styles/components/Header.css";
import logo from "./logo.jpg"; 

const Header = () => (
    <header className="main-header">
        <img src={logo} alt="Themis Logo" className="logo" />
        <h1 className="title">Themis</h1>
    </header>
);

export default Header;
