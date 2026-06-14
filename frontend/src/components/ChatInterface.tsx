import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessageStream } from '../lib/api';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Send, Bot, User, Loader2, BookOpen, AlertCircle } from 'lucide-react';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  sources?: string[];
}

interface ChatInterfaceProps {
  topicId: string;
}

export default function ChatInterface({ topicId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your LegalX assistant. Ask me any questions about this Act, and I will search the official documents to give you a plain-English translation, checklists, and legal citations.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "What are the main penalties under this Act?",
    "Who does this law protect?",
    "What are the key rights defined here?",
  ];

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;

    setError(null);
    const userMessage: Message = { sender: 'user', text: textToSend };
    const assistantPlaceholder: Message = {
      sender: 'assistant',
      text: '',
      sources: []
    };

    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setInput('');
    setLoading(true);

    try {
      await sendChatMessageStream(topicId, textToSend, (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          const lastMsgIndex = updated.length - 1;
          if (lastMsgIndex >= 0 && updated[lastMsgIndex].sender === 'assistant') {
            if (chunk.type === 'token' && chunk.token) {
              updated[lastMsgIndex] = {
                ...updated[lastMsgIndex],
                text: updated[lastMsgIndex].text + chunk.token
              };
            } else if (chunk.type === 'sources' && chunk.sources) {
              updated[lastMsgIndex] = {
                ...updated[lastMsgIndex],
                sources: chunk.sources
              };
            } else if (chunk.type === 'error' && chunk.detail) {
              setError(chunk.detail);
            }
          }
          return updated;
        });
      });
    } catch (err: any) {
      setError(err.message || 'Failed to connect to the AI reasoning server.');
      // Remove the last blank assistant message if we got an error and it's empty
      setMessages((prev) => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg && lastMsg.sender === 'assistant' && lastMsg.text === '') {
          updated.pop();
        }
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  return (
    <div className="flex flex-col h-[600px] border border-border bg-card/30 rounded-xl overflow-hidden shadow-sm">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-secondary/50 border-b border-border">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-indigo-500" />
          <span className="font-semibold text-sm">RAG Legal Assistant</span>
        </div>
        <Badge variant="outline" className="text-xs bg-indigo-500/5 text-indigo-600 dark:text-indigo-400 border-indigo-500/20">
          Llama 3.3 (Groq)
        </Badge>
      </div>

      {/* Messages Scroll Area */}
      <ScrollArea className="flex-1 min-h-0 p-6">
        <div className="space-y-6">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-4 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/10">
                  <Bot className="h-4 w-4 text-indigo-500" />
                </div>
              )}
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-none'
                    : 'bg-card border border-border rounded-bl-none text-foreground'
                }`}
              >
                {msg.sender === 'user' ? (
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                ) : (
                  <div className="prose prose-sm dark:prose-invert max-w-none space-y-2">
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>
                )}

                {/* Sources badges */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/60">
                    <p className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1 mb-1">
                      <BookOpen className="h-3 w-3" /> Citations & Sources:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((src, idx) => (
                        <Badge key={idx} variant="secondary" className="text-[10px] px-2 py-0.5 font-normal bg-secondary/80 text-secondary-foreground border border-border">
                          {src}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {msg.sender === 'user' && (
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <User className="h-4 w-4 text-primary" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="h-8 w-8 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/10">
                <Bot className="h-4 w-4 text-indigo-500" />
              </div>
              <div className="bg-card border border-border rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                <span className="text-xs text-muted-foreground">Consulting legal framework...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="flex gap-3 items-center justify-center p-3 border border-destructive/20 bg-destructive/5 rounded-xl text-xs text-destructive max-w-md mx-auto">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="px-6 py-3 border-t border-border/50 bg-secondary/20 flex flex-wrap gap-2">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              className="text-xs px-3 py-1.5 bg-card hover:bg-secondary border border-border rounded-lg text-muted-foreground hover:text-foreground transition-all duration-200"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(input);
        }}
        className="flex gap-2 p-4 bg-card/50 border-t border-border"
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this Act (e.g. 'What are the filing requirements?')..."
          disabled={loading}
          className="flex-grow bg-card border-border shadow-none focus-visible:ring-1 focus-visible:ring-indigo-500/40"
        />
        <Button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm transition-colors"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
