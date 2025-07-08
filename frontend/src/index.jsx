import ReactDOM from "react-dom/client";

import App from "./App.tsx";

const entryPoint = document.getElementById("root"); // react "injects" here
ReactDOM.createRoot(entryPoint).render(<App />); // this is our root component contains the other components
// Custom compontnts must start uppercase such that they can be differntiated from html elements
