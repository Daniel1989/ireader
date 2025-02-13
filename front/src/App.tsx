import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Outlet } from 'react-router-dom';
import './App.css'; // Adjust the path if necessary
import Home from './pages/home';
import Futures from './pages/futures';
import Chat from './pages/chat';
import WordCloud from './pages/wordcloud';
import { Select } from 'antd';
import { useTranslation } from 'react-i18next';
import './i18n/config';

type TranslationKeys = 
    | 'nav.chat'
    | 'nav.tagCloud';

function Layout() {
  const { i18n, t } = useTranslation();

  // Translation wrapper function with ts-ignore for type safety bypass
  const translate = (key: TranslationKeys) => {
    // @ts-ignore: Suppress type checking for translation function
    return t(key);
  };

  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value);
  };

  return (
    <div>
      <nav className="bg-gray-800 text-white p-4">
        <div className="flex justify-between items-center">
          <ul className="flex space-x-4">
            <li>
              <Link to="/" className="hover:text-gray-300">{translate('nav.chat')}</Link>
            </li>
            <li>
              <Link to="/wordcloud" className="hover:text-gray-300">{translate('nav.tagCloud')}</Link>
            </li>
          </ul>
          <Select
            defaultValue={i18n.language}
            onChange={handleLanguageChange}
            className="w-24"
            options={[
              { value: 'en', label: 'English' },
              { value: 'zh', label: '中文' },
            ]}
          />
        </div>
      </nav>
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
          <Route path="wordcloud" element={<WordCloud />} />
          {/* <Route path="chat" element={<Chat />} /> */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;