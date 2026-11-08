import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, FastForward } from 'lucide-react';

interface AudioPlayerWaveformProps {
  duration: number; // in seconds
  waveform?: number[];
  audioUrl?: string;
  isOutgoing?: boolean;
}

export const AudioPlayerWaveform: React.FC<AudioPlayerWaveformProps> = ({
  duration,
  waveform = [],
  audioUrl,
  isOutgoing,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackProgress, setPlaybackProgress] = useState(0); // 0 to 1
  const [playbackSpeed, setPlaybackSpeed] = useState<1 | 1.5 | 2>(1);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Generate fallback waveform if empty
  const defaultWaveform = waveform.length > 0
    ? waveform
    : [20, 45, 60, 80, 50, 30, 70, 90, 100, 65, 40, 55, 75, 95, 80, 45, 30, 60, 85, 70, 50, 35, 65, 80, 40, 20];

  useEffect(() => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.ontimeupdate = () => {
        if (audio.duration) {
          setPlaybackProgress(audio.currentTime / audio.duration);
        }
      };

      audio.onended = () => {
        setIsPlaying(false);
        setPlaybackProgress(0);
      };

      return () => {
        audio.pause();
      };
    }
  }, [audioUrl]);

  // Synthetic timer for mock audio if no real URL is present
  useEffect(() => {
    let interval: number | null = null;
    if (isPlaying && !audioUrl) {
      const step = 0.05 * playbackSpeed;
      interval = window.setInterval(() => {
        setPlaybackProgress((prev) => {
          if (prev >= 1) {
            setIsPlaying(false);
            return 0;
          }
          return prev + step / duration;
        });
      }, 50);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, audioUrl, duration, playbackSpeed]);

  const togglePlay = () => {
    if (audioRef.current && audioUrl) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.playbackRate = playbackSpeed;
        audioRef.current.play();
        setIsPlaying(true);
      }
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleSpeedToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextSpeed: Record<number, 1 | 1.5 | 2> = { 1: 1.5, 1.5: 2, 2: 1 };
    const newSpeed = nextSpeed[playbackSpeed];
    setPlaybackSpeed(newSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const currentTimeDisplay = isPlaying
    ? formatTime(playbackProgress * duration)
    : formatTime(duration);

  return (
    <div className="flex items-center gap-3 py-1 px-1 min-w-[200px] max-w-[280px] select-none">
      {/* Play/Pause Button */}
      <button
        onClick={togglePlay}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-transform active:scale-95 shrink-0 ${
          isOutgoing
            ? 'bg-[#2481cc] text-white hover:bg-[#1c6fad]'
            : 'bg-[#2481cc] text-white hover:bg-[#1c6fad]'
        }`}
      >
        {isPlaying ? (
          <Pause className="w-5 h-5 fill-current" />
        ) : (
          <Play className="w-5 h-5 fill-current ml-0.5" />
        )}
      </button>

      {/* Waveform Bars & Timing */}
      <div className="flex-1 flex flex-col justify-center gap-1 min-w-0">
        <div
          className="flex items-center gap-[2px] h-6 cursor-pointer"
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const newProgress = Math.max(0, Math.min(1, clickX / rect.width));
            setPlaybackProgress(newProgress);
            if (audioRef.current && audioUrl) {
              audioRef.current.currentTime = newProgress * audioRef.current.duration;
            }
          }}
        >
          {defaultWaveform.map((amp, index) => {
            const barProgress = index / defaultWaveform.length;
            const isPlayed = barProgress <= playbackProgress;
            const heightPx = Math.max(4, Math.round((amp / 100) * 22));

            return (
              <span
                key={index}
                className={`w-[2.5px] rounded-full transition-colors ${
                  isPlayed
                    ? 'bg-[#2481cc]'
                    : isOutgoing
                    ? 'bg-gray-400/40'
                    : 'bg-gray-500/40'
                }`}
                style={{ height: `${heightPx}px` }}
              />
            );
          })}
        </div>

        <div className="flex items-center justify-between text-[11px] text-gray-400">
          <span>{currentTimeDisplay}</span>
          <button
            onClick={handleSpeedToggle}
            className="px-1 py-0.2 rounded bg-black/20 hover:bg-black/30 font-semibold text-[10px] text-sky-400 transition-colors"
          >
            {playbackSpeed}x
          </button>
        </div>
      </div>
    </div>
  );
};
