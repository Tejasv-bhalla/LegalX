import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchTopics, type TopicOverview } from '../lib/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Shield, Scale, Terminal, Landmark, BookOpen, AlertCircle, Loader2 } from 'lucide-react';

export default function HomePage() {
  const [topics, setTopics] = useState<TopicOverview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopics()
      .then((data) => {
        setTopics(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load legal topics. Please ensure the backend is running.');
        setLoading(false);
      });
  }, []);

  const getTopicIcon = (id: string) => {
    switch (id.toLowerCase()) {
      case 'pocso':
        return <Shield className="h-8 w-8 text-indigo-500" />;
      case 'consumer_protection':
        return <Scale className="h-8 w-8 text-emerald-500" />;
      case 'cyber_crime':
        return <Terminal className="h-8 w-8 text-cyan-500" />;
      case 'gst_registration':
        return <Landmark className="h-8 w-8 text-amber-500" />;
      case 'rti':
        return <BookOpen className="h-8 w-8 text-rose-500" />;
      default:
        return <Scale className="h-8 w-8 text-purple-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm font-medium">Connecting to LegalX Knowledge Base...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-md my-16 p-6 border border-destructive/20 bg-destructive/5 rounded-lg flex flex-col items-center gap-4 text-center">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-1">Database Connection Error</h3>
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
        <button 
          onClick={() => { setLoading(true); setError(null); }}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/95 transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <div className="text-center space-y-4 mb-16">
        <Badge variant="secondary" className="px-3 py-1 text-xs font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
          AI-Powered Legal Assistant
        </Badge>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-foreground sm:text-6xl">
          LegalX Knowledge Centre
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
          Democratizing and simplifying official legal documents into plain English with actionable checklists and immediate RAG assistance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {topics.map((topic) => (
          <Link key={topic.id} to={`/topic/${topic.id}`} className="block group">
            <Card className="h-full border border-border bg-card/50 hover:bg-card hover:border-primary/30 transition-all duration-300 shadow-sm hover:shadow-md flex flex-col rounded-xl overflow-hidden">
              <CardHeader className="flex flex-row items-center gap-4 space-y-0 pb-4">
                <div className="p-3 bg-secondary/80 rounded-xl group-hover:bg-primary/10 transition-colors duration-300">
                  {getTopicIcon(topic.id)}
                </div>
                <div>
                  <CardTitle className="text-lg font-bold group-hover:text-primary transition-colors duration-200 line-clamp-1">
                    {topic.title}
                  </CardTitle>
                  <CardDescription className="text-xs text-muted-foreground uppercase font-mono mt-0.5">
                    ID: {topic.id}
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent className="flex-grow flex flex-col justify-between pt-0">
                <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3 mb-6">
                  {topic.card_description}
                </p>
                <div className="flex items-center text-sm font-semibold text-primary group-hover:translate-x-1 transition-transform duration-200">
                  Explore Act & Chat →
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
