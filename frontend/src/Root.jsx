import { useEffect, useState } from 'react';
import App from './App.jsx';
import AboutPage from './components/AboutPage.jsx';
import './about.css';

const pageFromHash = () => (window.location.hash === '#/about' ? 'about' : 'map');

export default function Root() {
  const [page, setPage] = useState(pageFromHash);

  useEffect(() => {
    const onChange = () => setPage(pageFromHash());
    window.addEventListener('hashchange', onChange);
    return () => window.removeEventListener('hashchange', onChange);
  }, []);

  return page === 'about' ? <AboutPage /> : <App />;
}