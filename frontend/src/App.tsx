
import { JSX, useEffect, useState } from "react";
import { CommonResponse, DefaultService } from "./client";
import { request } from "http";

const appDomain = import.meta.env.VITE_APP_DOMAIN;

function App(): JSX.Element {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Call the backend endpoint on component mount
      const body: CommonResponse = {test: "Hello" }
      const res =DefaultService.testFirstTestFirstPost(body);
  }, []);

  return (
    <div>
      <h2>Hello</h2>
      <p>Backend says: {message}</p>
    </div>
  );
}

export default App;
