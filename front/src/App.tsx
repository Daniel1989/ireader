import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Outlet } from 'react-router-dom';
import './App.css'; // Adjust the path if necessary
import Home from './pages/home';
import Futures from './pages/futures';
import Chat from './pages/chat';
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
          <Route index element={<Chat />} />
          <Route path="futures" element={<Futures />} />
          {/* <Route path="chat" element={<Chat />} /> */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;