import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import HomePage from './pages/HomePage';
import LeaderboardPage from './pages/LeaderboardPage';
import GamePlayPage from './pages/GamePlayPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AboutPage from './pages/AboutPage';
import GamesPage from './pages/GamesPage';
import BackToTop from './components/BackToTop/BackToTop';

const AppLayout = () => {
  const location = useLocation();
  const isPlaying = location.pathname.startsWith('/play/');
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <div className="min-h-screen relative text-white bg-[#050508]">
      {/* Animated Static Background Overlay */}
      <div className="fixed inset-0 z-[-1] pointer-events-none">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10" />
        <div className="absolute inset-0 bg-gradient-to-tr from-purple-900/10 via-black to-blue-900/10" />
      </div>

      {!isPlaying && !isAuthPage && <Navbar />}

      <main className="relative z-10">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/play/:gameId" element={<GamePlayPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/profile" element={<div className="pt-32 text-center text-3xl font-orbitron text-purple-500">Profile Coming Soon...</div>} />
        </Routes>
      </main>

      {!isAuthPage && <Footer />}

      {/* Floating Back to Top Button - hidden on game play & auth pages */}
      {!isPlaying && !isAuthPage && <BackToTop />}
    </div>
  );
};

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}

export default App;
