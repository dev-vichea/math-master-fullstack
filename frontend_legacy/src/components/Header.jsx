import React, { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';
import { BookOpen, Sun, Moon } from 'lucide-react';

export default function Header({ lang, setLang, theme, toggleTheme, onOpenGlossary }) {
  const [health, setHealth] = useState({ online: false, checking: true });

  useEffect(() => {
    let isMounted = true;
    const testConnection = async () => {
      const res = await checkHealth();
      if (isMounted) {
        setHealth({ ...res, checking: false });
      }
    };

    testConnection();
    const interval = setInterval(testConnection, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="header">
      <div className="header-container">
        <div className="brand">
          <div className="brand-logo">
            <span>∑</span>
          </div>
          <div className="brand-meta">
            <h1 className="brand-title">
              Khmer Math Lab <span className="demo-tag">React Demo</span>
            </h1>
            <p className="brand-subtitle">មន្ទីរពិសោធន៍គណិតវិទ្យាខ្មែរ — BacII Grade 12 Solver</p>
          </div>
        </div>

        <div className="header-controls">
          {/* Backend Status */}
          <div className={`status-pill ${health.online ? 'status-online' : 'status-offline'}`}>
            <span className="status-indicator"></span>
            <span className="status-text">
              {health.checking
                ? 'Connecting...'
                : health.online
                ? 'Backend Live'
                : 'Offline (Port 8000)'}
            </span>
          </div>

          {/* Theme Toggle (Light / Dark) */}
          <button
            type="button"
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={theme === 'light' ? 'ប្ដូរទៅ Dark Mode' : 'ប្ដូរទៅ Light Mode'}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>

          {/* Language Switcher */}
          <div className="lang-switcher">
            <button
              className={`lang-btn ${lang === 'km' ? 'active' : ''}`}
              onClick={() => setLang('km')}
              type="button"
            >
              🇰🇭 ខ្មែរ
            </button>
            <button
              className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
              onClick={() => setLang('en')}
              type="button"
            >
              🇬🇧 EN
            </button>
          </div>

          {/* Bilingual Math Glossary Trigger */}
          <button
            type="button"
            className="glossary-btn"
            onClick={onOpenGlossary}
            title="បើកពាក្យគន្លឹះគណិតវិទ្យា (English - Khmer BacII Glossary)"
          >
            <BookOpen size={16} />
            <span>ពាក្យគន្លឹះ (Glossary)</span>
          </button>

          {/* API Docs Link */}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="docs-link"
            title="FastAPI Swagger Documentation"
          >
            <span>API Docs</span>
          </a>
        </div>
      </div>
    </header>
  );
}
