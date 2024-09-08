import React from 'react';
import { HashRouter as Router, Route, Routes, Link, Outlet } from 'react-router-dom';
import Home from './pages/home';
import Futures from './pages/futures';
function Layout() {
  return (
    <div>
      <Outlet />  {/* Render child routes here */}
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="futures" element={<Futures />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;