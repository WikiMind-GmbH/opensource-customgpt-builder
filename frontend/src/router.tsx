import { createBrowserRouter } from "react-router-dom";
import Layout from "./layout/Layout";
import ChatWindow from "./pages/ChatWindow";
import DisplayCustomGPTs from "./pages/DisplayCustomGPTs";
import CreateOrEditCustomGPT from "./pages/CreateOrEditCustomGPT";


export const router = createBrowserRouter([
  {
    element: <Layout />,              // sidebar lives inside Layout
    children: [
      { index: true, element: <ChatWindow /> }, 
      { path: "chatWindow/:idOfChat", element: <ChatWindow /> },
      { path: "createOrEditCustomGPT", element: <CreateOrEditCustomGPT /> },
      { path: "createOrEditCustomGPT/:idOfCustomGPT", element: <CreateOrEditCustomGPT /> },
      { path: "displayCustomGPTs", element: <DisplayCustomGPTs /> }, 
    ],
  },
]);