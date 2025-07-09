import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h2 className="title">Demo App</h2>
      <nav className="nav">
        <NavLink to="/createOrEditCustomGPT"    className="navlink">Create custom GPTs</NavLink>
        <NavLink to="/displayCustomGPTs" className="navlink">Display custom GPTs</NavLink>
        <NavLink to="/" className="navlink">Create new chat</NavLink>
      </nav>
    </aside>
  );
}