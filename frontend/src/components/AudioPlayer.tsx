import { useState, useRef, useEffect } from 'react';
import { getAudioUrl } from '../lib/api';
import { Button } from './ui/button';
import { Play, Pause, RotateCcw, Volume2, Loader2, Music } from 'lucide-react';
import { Badge } from './ui/badge';

interface AudioPlayerProps {
  topicId: string;
}

export default function AudioPlayer({ topicId }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const audioUrl = getAudioUrl(topicId);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      setIsLoading(true);
      audioRef.current.play()
        .then(() => {
          setIsPlaying(true);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("Audio playback failed:", err);
          setIsLoading(false);
        });
    }
  };

  const handleRestart = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = 0;
    setProgress(0);
    if (!isPlaying) {
      togglePlay();
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const current = audioRef.current.currentTime;
    const dur = audioRef.current.duration || 0;
    setProgress(dur > 0 ? (current / dur) * 100 : 0);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration || 0);
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
    setProgress(100);
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current || duration === 0) return;
    const clickPercent = parseFloat(e.target.value);
    const newTime = (clickPercent / 100) * duration;
    audioRef.current.currentTime = newTime;
    setProgress(clickPercent);
  };

  // Reset audio state when topic ID changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = audioUrl;
      audioRef.current.load();
    }
    setIsPlaying(false);
    setProgress(0);
    setDuration(0);
  }, [topicId, audioUrl]);

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '0:00';
    const minutes = Math.floor(secs / 60);
    const seconds = Math.floor(secs % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <div className="flex flex-col gap-3 p-4 bg-secondary/30 border border-border rounded-xl shadow-sm">
      {/* Hidden native audio tag */}
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleAudioEnded}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 rounded-lg shrink-0">
            <Music className="h-5 w-5 text-indigo-500" />
          </div>
          <div className="text-left">
            <p className="text-sm font-semibold text-foreground">Audio Translation</p>
            <p className="text-xs text-muted-foreground">Listen to plain-English summary</p>
          </div>
        </div>
        <Badge variant="outline" className="text-[10px] bg-secondary border-border font-mono font-normal">
          {formatTime(audioRef.current?.currentTime || 0)} / {formatTime(duration)}
        </Badge>
      </div>

      <div className="flex items-center gap-3 mt-1">
        {/* Play/Pause controls */}
        <Button
          onClick={togglePlay}
          disabled={isLoading}
          variant="outline"
          size="icon"
          className="h-10 w-10 shrink-0 border-border bg-card shadow-sm text-foreground hover:bg-secondary rounded-lg"
        >
          {isLoading ? (
            <Loader2 className="h-4.5 w-4.5 animate-spin text-indigo-500" />
          ) : isPlaying ? (
            <Pause className="h-4.5 w-4.5 text-foreground fill-foreground" />
          ) : (
            <Play className="h-4.5 w-4.5 text-foreground fill-foreground ml-0.5" />
          )}
        </Button>

        {/* Reset control */}
        <Button
          onClick={handleRestart}
          variant="outline"
          size="icon"
          className="h-10 w-10 shrink-0 border-border bg-card shadow-sm text-foreground hover:bg-secondary rounded-lg"
        >
          <RotateCcw className="h-4.5 w-4.5 text-muted-foreground" />
        </Button>

        {/* Progress track slider */}
        <div className="flex-grow flex items-center px-1">
          <input
            type="range"
            min="0"
            max="100"
            value={progress}
            onChange={handleProgressChange}
            className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-indigo-600 focus:outline-none dark:bg-zinc-800"
          />
        </div>
        
        <Volume2 className="h-4.5 w-4.5 text-muted-foreground shrink-0 hidden sm:block" />
      </div>
    </div>
  );
}
