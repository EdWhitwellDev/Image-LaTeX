import App from "./components/App"; // load the component
import React, { Component } from "react";
import { createRoot } from 'react-dom/client';
const container = document.getElementById('app'); // get the element that will contain the app
const root = createRoot(container); // tell react that this is the root element to render within
root.render(<App tab="home" />); // render App within the element