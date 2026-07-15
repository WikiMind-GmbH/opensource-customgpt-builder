import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { client } from "./client/client.gen";
import "./styles.css";

client.setConfig({ baseURL: "https://localhost/api" });

createRoot(document.getElementById("root")!).render(
  <RouterProvider router={router} />
);
