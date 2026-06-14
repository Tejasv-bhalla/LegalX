import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import TopicPage from './pages/TopicPage';
import { Scale, Heart } from 'lucide-react';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-200">
        {/* Global Navigation Header */}
        <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between max-w-6xl">
            <Link to="/" className="flex items-center gap-2 hover:opacity-90 transition-opacity">
              <Scale className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-indigo-600 to-violet-500 bg-clip-text text-transparent dark:from-indigo-400 dark:to-violet-300">
                LegalX
              </span>
            </Link>
            <nav className="flex items-center gap-4 text-sm font-medium text-muted-foreground">
              <Link to="/" className="hover:text-foreground transition-colors">Dashboard</Link>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
              >
                Docs
              </a>
            </nav>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/topic/:id" element={<TopicPage />} />
          </Routes>
        </main>

        {/* Global Footer */}
        <footer className="border-t border-border bg-secondary/30 py-8">
          <div className="container mx-auto px-4 max-w-6xl flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <span>Built with</span>
              <Heart className="h-4.5 w-4.5 text-rose-500 fill-rose-500" />
              <span>for legal empowerment</span>
            </div>
            <p>© {new Date().getFullYear()} LegalX AI. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
