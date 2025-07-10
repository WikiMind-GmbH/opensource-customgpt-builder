
import { JSX, useEffect, useState } from "react";
import { CommonResponse, DefaultService } from "./client";
import { request } from "http";

const appDomain = import.meta.env.VITE_APP_DOMAIN;

function App(): JSX.Element {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Call the backend endpoint on component mount
    

  }, []);

  return (
    <div>
      <h2>Hello</h2>
      <p>Backend says: {message}</p>
    </div>
  );
}

export default App;
