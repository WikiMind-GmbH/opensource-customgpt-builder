import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function Layout() {
  return (
    <div className="app">
      <Sidebar />
      <main className="content">
        <Outlet />   {/* child route appears here */}
      </main>
    </div>
  );
}