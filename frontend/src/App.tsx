import TestComponent from "./components/TestComponent";
const appDomain = import.meta.env.VITE_APP_DOMAIN;
function App(): any {
    return (
        <div>
            <h2> Hello</h2>
            <TestComponent test="Component"/>
        </div>

    )
}

export default App;