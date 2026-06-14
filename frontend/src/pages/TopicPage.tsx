import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { fetchTopicDetail, type TopicDetail } from '../lib/api';
import ChatInterface from '../components/ChatInterface';
import AudioPlayer from '../components/AudioPlayer';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { ArrowLeft, BookOpen, AlertCircle, ShieldAlert, Award, ExternalLink, Loader2 } from 'lucide-react';

export default function TopicPage() {
  const { id } = useParams<{ id: string }>();
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      setLoading(true);
      fetchTopicDetail(id)
        .then((data) => {
          setTopic(data);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || 'Failed to load topic details.');
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm font-medium">Loading details from LegalX server...</p>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="mx-auto max-w-md my-16 p-6 border border-destructive/20 bg-destructive/5 rounded-lg flex flex-col items-center gap-4 text-center">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-1">Failed to Load Topic</h3>
          <p className="text-sm text-muted-foreground">{error || 'Topic not found'}</p>
        </div>
        <Link to="/" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/95 transition-colors">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Navigation & Topic Header */}
      <div className="mb-8">
        <Link to="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors duration-200">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Link>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl my-0">
              {topic.title}
            </h1>
            <p className="text-sm text-muted-foreground mt-2 font-mono uppercase">Topic Reference ID: {topic.id}</p>
          </div>
          <a
            href={topic.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 border border-border bg-card hover:bg-secondary text-sm font-medium rounded-lg shadow-sm transition-colors duration-200 shrink-0 self-start md:self-center"
          >
            Official Gazette URL <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>

      {/* Main Two-Column Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Panel: Legal Details (Tabs view) */}
        <div className="lg:col-span-7 space-y-6">
          <AudioPlayer topicId={topic.id} />
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-secondary/80 p-1 rounded-xl">
              <TabsTrigger value="summary" className="rounded-lg py-2 text-xs md:text-sm font-semibold">Summary</TabsTrigger>
              <TabsTrigger value="rights" className="rounded-lg py-2 text-xs md:text-sm font-semibold">Rights</TabsTrigger>
              <TabsTrigger value="penalties" className="rounded-lg py-2 text-xs md:text-sm font-semibold">Penalties</TabsTrigger>
            </TabsList>
            
            <TabsContent value="summary" className="mt-6">
              <Card className="border border-border bg-card/50 shadow-sm rounded-xl overflow-hidden">
                <CardHeader className="border-b border-border/50 pb-4 bg-secondary/20">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-indigo-500" />
                    <CardTitle className="text-base font-bold">Plain-English Summary</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground leading-relaxed space-y-4">
                    <ReactMarkdown>{topic.summary}</ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="rights" className="mt-6">
              <Card className="border border-border bg-card/50 shadow-sm rounded-xl overflow-hidden">
                <CardHeader className="border-b border-border/50 pb-4 bg-secondary/20">
                  <div className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-emerald-500" />
                    <CardTitle className="text-base font-bold">Your Rights Under This Act</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  {topic.key_rights && topic.key_rights.length > 0 ? (
                    <ul className="space-y-4">
                      {topic.key_rights.map((right, index) => (
                        <li key={index} className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed">
                          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold font-mono">
                            {index + 1}
                          </span>
                          <span>{right}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">No specific citizen rights retrieved for this topic.</p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="penalties" className="mt-6">
              <Card className="border border-border bg-card/50 shadow-sm rounded-xl overflow-hidden">
                <CardHeader className="border-b border-border/50 pb-4 bg-secondary/20">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-rose-500" />
                    <CardTitle className="text-base font-bold">Important Penalties & Offences</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  {topic.penalties && topic.penalties.length > 0 ? (
                    <ul className="space-y-4">
                      {topic.penalties.map((penalty, index) => (
                        <li key={index} className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed">
                          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 text-xs font-bold font-mono">
                            {index + 1}
                          </span>
                          <span>{penalty}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">No specific penalties retrieved for this topic.</p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Panel: RAG Chat Assistant */}
        <div className="lg:col-span-5">
          <ChatInterface topicId={topic.id} />
        </div>
      </div>
    </div>
  );
}
