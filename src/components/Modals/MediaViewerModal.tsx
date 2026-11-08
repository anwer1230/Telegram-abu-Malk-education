import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  X,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Share2,
  ChevronLeft,
  ChevronRight,
  Volume2,
  VolumeX,
  Volume1,
  Maximize2,
  Minimize2,
  Maximize,
  Repeat,
  Tv,
  MoreVertical,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { ViewerMediaItem } from '../../types';

// Custom Telegram Play & Pause Icons matching Telegram native design
const TelegramPlayIcon: React.FC<{ className?: string }> = ({ className = 'w-5 h-5' }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M7 4.75a1.75 1.75 0 0 1 2.65-1.5l11 6.5a1.75 1.75 0 0 1 0 3l-11 6.5A1.75 1.75 0 0 1 7 17.75V4.75z" />
  </svg>
);

const TelegramPauseIcon: React.FC<{ className?: string }> = ({ className = 'w-5 h-5' }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <rect x="6.5" y="4.5" width="3.75" height="15" rx="1.8" />
    <rect x="13.75" y="4.5" width="3.75" height="15" rx="1.8" />
  </svg>
);

const TelegramReplayIcon: React.FC<{ className?: string }> = ({ className = 'w-5 h-5' }) => (
  <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
    <path d="M3 3v5h5" />
  </svg>
);

// Format seconds into mm:ss or hh:mm:ss like official Telegram
function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return '0:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

const PEER_COLORS = [
  '#e17076',
  '#faa774',
  '#a695e7',
  '#7bc862',
  '#6ec9cb',
  '#65aadd',
  '#ee7aae',
];

function getPeerColor(name: string = '') {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) % PEER_COLORS.length;
  }
  return PEER_COLORS[Math.abs(hash)] || PEER_COLORS[0];
}

const PLAYBACK_SPEEDS = [0.5, 1, 1.25, 1.5, 2];

export const MediaViewerModal: React.FC = () => {
  const {
    viewerMedia,
    viewerPlaylist,
    setViewerMedia,
    settings,
    setForwardingMessage,
    setActiveModal,
    showToast,
  } = useTelegram();

  const isArabic = settings.language === 'ar';

  // Video playback states
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const progressBarRef = useRef<HTMLDivElement | null>(null);
  const thumbnailsRef = useRef<HTMLDivElement | null>(null);

  const [isPlaying, setIsPlaying] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [bufferedPercent, setBufferedPercent] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [speedIndex, setSpeedIndex] = useState(1); // default 1x
  const [isLooping, setIsLooping] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const controlsTimeoutRef = useRef<number | null>(null);
  const lastVolumeRef = useRef<number>(1);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null);

  // Time format mode (total vs remaining)
  const [showRemainingTime, setShowRemainingTime] = useState(false);

  // Scrubber hover state
  const [hoverSeekTime, setHoverSeekTime] = useState<number | null>(null);
  const [hoverSeekPos, setHoverSeekPos] = useState<number>(0);
  const [isDraggingSeek, setIsDraggingSeek] = useState(false);

  // Seek ripple feedback for arrow keys
  const [seekFeedback, setSeekFeedback] = useState<{ text: string; dir: 'left' | 'right' } | null>(null);
  const seekFeedbackTimeoutRef = useRef<number | null>(null);

  // Photo viewer states
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDraggingPan, setIsDraggingPan] = useState(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Touch swipe handling
  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(null);

  // Close context menu on outside click
  useEffect(() => {
    const handleGlobalClick = () => {
      if (contextMenu) setContextMenu(null);
    };
    window.addEventListener('click', handleGlobalClick);
    return () => window.removeEventListener('click', handleGlobalClick);
  }, [contextMenu]);

  // Determine current active item and playlist index
  const activeItem: ViewerMediaItem | null = viewerMedia;

  const currentPlaylist = React.useMemo(() => {
    if (viewerPlaylist && viewerPlaylist.length > 0) {
      return viewerPlaylist;
    }
    if (activeItem) {
      return [activeItem];
    }
    return [];
  }, [viewerPlaylist, activeItem]);

  const currentIndex = React.useMemo(() => {
    if (!activeItem || currentPlaylist.length === 0) return -1;
    const idx = currentPlaylist.findIndex(
      (item) => item.url === activeItem.url || (item.messageId && item.messageId === activeItem.messageId)
    );
    return idx >= 0 ? idx : 0;
  }, [activeItem, currentPlaylist]);

  const isVideo = React.useMemo(() => {
    if (!activeItem) return false;
    if (activeItem.type === 'video' || activeItem.type === 'video_note') return true;
    const urlLower = activeItem.url.toLowerCase();
    return (
      urlLower.endsWith('.mp4') ||
      urlLower.endsWith('.webm') ||
      urlLower.endsWith('.mov') ||
      urlLower.endsWith('.mkv') ||
      urlLower.endsWith('.m4v')
    );
  }, [activeItem]);

  // Reset photo zoom/pan/rotation and video state when activeItem changes
  useEffect(() => {
    setZoom(1);
    setRotation(0);
    setPan({ x: 0, y: 0 });
    setIsPlaying(true);
    setCurrentTime(0);
    setDuration(activeItem?.duration || 0);
    setIsBuffering(false);

    // Scroll active thumbnail into center view
    if (thumbnailsRef.current && currentIndex >= 0) {
      const activeEl = thumbnailsRef.current.children[currentIndex] as HTMLElement;
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }
    }
  }, [activeItem?.url, currentIndex]);

  // Auto-hide controls for video when idle
  const handleUserActivity = useCallback(() => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      window.clearTimeout(controlsTimeoutRef.current);
    }
    if (isVideo && isPlaying) {
      controlsTimeoutRef.current = window.setTimeout(() => {
        setShowControls(false);
      }, 3000);
    }
  }, [isVideo, isPlaying]);

  useEffect(() => {
    if (!isPlaying) {
      setShowControls(true);
      if (controlsTimeoutRef.current) {
        window.clearTimeout(controlsTimeoutRef.current);
      }
    }
  }, [isPlaying]);

  // Navigation handlers
  const goToPrev = useCallback(() => {
    if (currentIndex > 0) {
      setViewerMedia(currentPlaylist[currentIndex - 1], currentPlaylist);
    }
  }, [currentIndex, currentPlaylist, setViewerMedia]);

  const goToNext = useCallback(() => {
    if (currentIndex < currentPlaylist.length - 1) {
      setViewerMedia(currentPlaylist[currentIndex + 1], currentPlaylist);
    }
  }, [currentIndex, currentPlaylist, setViewerMedia]);

  const togglePlayPause = useCallback(() => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const toggleMute = useCallback(() => {
    if (!videoRef.current) return;
    if (isMuted || volume === 0) {
      const restored = lastVolumeRef.current > 0 ? lastVolumeRef.current : 0.8;
      videoRef.current.muted = false;
      videoRef.current.volume = restored;
      setIsMuted(false);
      setVolume(restored);
    } else {
      lastVolumeRef.current = volume > 0 ? volume : 0.8;
      videoRef.current.muted = true;
      setIsMuted(true);
    }
  }, [isMuted, volume]);

  const showSeekRipple = useCallback((text: string, dir: 'left' | 'right') => {
    setSeekFeedback({ text, dir });
    if (seekFeedbackTimeoutRef.current) {
      window.clearTimeout(seekFeedbackTimeoutRef.current);
    }
    seekFeedbackTimeoutRef.current = window.setTimeout(() => {
      setSeekFeedback(null);
    }, 600);
  }, []);

  const handleVolumeChange = (newVolume: number) => {
    if (!videoRef.current) return;
    videoRef.current.volume = newVolume;
    setVolume(newVolume);
    if (newVolume === 0) {
      videoRef.current.muted = true;
      setIsMuted(true);
    } else if (isMuted) {
      videoRef.current.muted = false;
      setIsMuted(false);
    }
  };

  const handleSpeedCycle = () => {
    const nextIdx = (speedIndex + 1) % PLAYBACK_SPEEDS.length;
    const nextSpeed = PLAYBACK_SPEEDS[nextIdx];
    setSpeedIndex(nextIdx);
    if (videoRef.current) {
      videoRef.current.playbackRate = nextSpeed;
    }
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen?.().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.().catch(() => {});
      setIsFullscreen(false);
    }
  };

  const togglePiP = async () => {
    if (!videoRef.current) return;
    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
      } else if (videoRef.current.requestPictureInPicture) {
        await videoRef.current.requestPictureInPicture();
      }
    } catch (err) {
      console.warn('PiP error:', err);
    }
  };

  // Keyboard events listener
  useEffect(() => {
    if (!activeItem) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept inputs
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;

      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          if (contextMenu) {
            setContextMenu(null);
            return;
          }
          setViewerMedia(null);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          if (isVideo && videoRef.current) {
            const nextTime = Math.max(0, videoRef.current.currentTime - 5);
            videoRef.current.currentTime = nextTime;
            setCurrentTime(nextTime);
            showSeekRipple('-5s', 'left');
          } else {
            goToPrev();
          }
          break;
        case 'ArrowRight':
          e.preventDefault();
          if (isVideo && videoRef.current) {
            const nextTime = Math.min(
              videoRef.current.duration || 0,
              videoRef.current.currentTime + 5
            );
            videoRef.current.currentTime = nextTime;
            setCurrentTime(nextTime);
            showSeekRipple('+5s', 'right');
          } else {
            goToNext();
          }
          break;
        case ' ':
          if (isVideo) {
            e.preventDefault();
            togglePlayPause();
          }
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'm':
        case 'M':
          if (isVideo) {
            e.preventDefault();
            toggleMute();
          }
          break;
        case 'ArrowUp':
          if (isVideo) {
            e.preventDefault();
            handleVolumeChange(Math.min(1, volume + 0.1));
          }
          break;
        case 'ArrowDown':
          if (isVideo) {
            e.preventDefault();
            handleVolumeChange(Math.max(0, volume - 0.1));
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeItem, isVideo, volume, goToPrev, goToNext, togglePlayPause, toggleMute, contextMenu, showSeekRipple]);

  // Video progress & buffered calculation
  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);

    // Calculate buffer
    if (videoRef.current.buffered.length > 0 && videoRef.current.duration > 0) {
      const bufferedEnd = videoRef.current.buffered.end(videoRef.current.buffered.length - 1);
      const pct = (bufferedEnd / videoRef.current.duration) * 100;
      setBufferedPercent(pct);
    }
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration);
    setIsBuffering(false);
  };

  // Scrubber drag / click
  const handleScrubberMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || !videoRef.current || !duration) return;
    setIsDraggingSeek(true);
    const rect = progressBarRef.current.getBoundingClientRect();
    const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetTime = pos * duration;
    videoRef.current.currentTime = targetTime;
    setCurrentTime(targetTime);

    const onMouseMove = (moveEvent: MouseEvent) => {
      const mPos = Math.max(0, Math.min(1, (moveEvent.clientX - rect.left) / rect.width));
      const mTime = mPos * duration;
      if (videoRef.current) videoRef.current.currentTime = mTime;
      setCurrentTime(mTime);
    };

    const onMouseUp = () => {
      setIsDraggingSeek(false);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const handleScrubberMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || !duration) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    setHoverSeekPos(e.clientX - rect.left);
    setHoverSeekTime(pos * duration);
  };

  const handleScrubberMouseLeave = () => {
    if (!isDraggingSeek) {
      setHoverSeekTime(null);
    }
  };

  // Photo Zoom & Pan
  const handleZoomIn = () => setZoom((z) => Math.min(4, z + 0.5));
  const handleZoomOut = () => setZoom((z) => Math.max(1, z - 0.5));
  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setRotation(0);
  };
  const handleRotate = () => setRotation((r) => (r + 90) % 360);

  const handleImageDoubleClick = () => {
    if (zoom > 1) {
      handleResetZoom();
    } else {
      setZoom(2.5);
    }
  };

  const handleImageMouseDown = (e: React.MouseEvent) => {
    if (zoom <= 1) return;
    setIsDraggingPan(true);
    dragStartRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleImageMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingPan) return;
    setPan({
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y,
    });
  };

  const handleImageMouseUp = () => {
    setIsDraggingPan(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (isVideo) return;
    e.preventDefault();
    if (e.deltaY < 0) {
      setZoom((z) => Math.min(4, z + 0.25));
    } else {
      setZoom((z) => Math.max(1, z - 0.25));
    }
  };

  // Touch Swipe for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      touchStartRef.current = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY,
        time: Date.now(),
      };
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStartRef.current || zoom > 1) return;
    const touch = e.changedTouches[0];
    const dx = touch.clientX - touchStartRef.current.x;
    const dy = touch.clientY - touchStartRef.current.y;
    const dt = Date.now() - touchStartRef.current.time;

    // Horizontal swipe (> 50px in < 400ms)
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && dt < 400) {
      if (dx < 0) {
        goToNext();
      } else {
        goToPrev();
      }
    }
    // Vertical swipe down (> 90px) to close viewer like Telegram Android
    else if (dy > 90 && Math.abs(dy) > Math.abs(dx) && dt < 400) {
      setViewerMedia(null);
    }
    touchStartRef.current = null;
  };

  const handleForwardMedia = () => {
    if (!activeItem) return;
    setForwardingMessage({
      id: activeItem.messageId || 'media_' + Date.now(),
      chatId: activeItem.chatId || 'current',
      senderId: 'current',
      senderName: activeItem.sender || 'Media',
      senderAvatar: activeItem.senderAvatar,
      text: activeItem.caption || activeItem.title || '',
      timestamp: activeItem.timestamp || 'Just now',
      date: new Date().toISOString().split('T')[0],
      status: 'sent',
      isOutgoing: true,
      media: {
        type: isVideo ? 'video' : 'photo',
        url: activeItem.url,
        duration: activeItem.duration,
        fileName: activeItem.fileName,
        fileSize: activeItem.fileSize,
      },
    });
    setActiveModal('forward');
  };

  const handleSaveToDevice = async () => {
    if (!activeItem?.url) return;
    setContextMenu(null);
    const fallbackExt = isVideo ? 'mp4' : 'jpg';
    const fallbackName = isVideo
      ? `telegram_video_${Date.now()}.${fallbackExt}`
      : `telegram_photo_${Date.now()}.${fallbackExt}`;
    const targetFileName = activeItem.fileName || fallbackName;

    showToast(isArabic ? 'جارٍ حفظ الملف في جهازك...' : 'Saving to device...', '📥');

    try {
      const response = await fetch(activeItem.url);
      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = targetFileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(objectUrl);
      showToast(isArabic ? 'تم حفظ الملف في مساحة تخزين الجهاز بنجاح' : 'Saved to device successfully', '✅');
    } catch (err) {
      // Fallback direct link download
      const link = document.createElement('a');
      link.href = activeItem.url;
      link.download = targetFileName;
      link.target = '_blank';
      link.rel = 'noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast(isArabic ? 'بدأ تنزيل الملف إلى جهازك...' : 'Downloading to device...', '📥');
    }
  };

  const handleDownload = () => {
    handleSaveToDevice();
  };

  if (!activeItem) return null;

  const currentSpeed = PLAYBACK_SPEEDS[speedIndex];
  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      id="tg-official-media-viewer"
      onMouseMove={handleUserActivity}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onWheel={handleWheel}
      className="fixed inset-0 z-50 flex flex-col bg-[#0b0e14]/96 select-none animate-in fade-in duration-200 text-white overflow-hidden"
      style={{
        cursor: showControls ? 'default' : 'none',
      }}
    >
      {/* Top Header Controls Bar */}
      <div
        className={`h-16 px-4 sm:px-6 flex items-center justify-between border-b border-white/10 z-30 bg-gradient-to-b from-black/80 via-black/40 to-transparent transition-opacity duration-300 ${
          showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
        {/* Sender Info & Counter */}
        <div className="flex items-center gap-3 min-w-0">
          <div
            className="w-9 h-9 rounded-full overflow-hidden shrink-0 flex items-center justify-center font-bold text-xs shadow-md"
            style={{
              backgroundColor: getPeerColor(activeItem.sender || 'U'),
            }}
          >
            {activeItem.senderAvatar ? (
              <img
                src={activeItem.senderAvatar}
                alt=""
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            ) : (
              (activeItem.sender?.charAt(0) || 'U').toUpperCase()
            )}
          </div>

          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm truncate max-w-[200px] sm:max-w-md">
                {activeItem.sender || (isVideo ? (isArabic ? 'فيديو' : 'Video') : (isArabic ? 'صورة' : 'Photo'))}
              </span>
              {currentPlaylist.length > 1 && (
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-white/15 text-gray-200">
                  {currentIndex + 1} / {currentPlaylist.length}
                </span>
              )}
            </div>
            {activeItem.timestamp && (
              <span className="text-xs text-gray-400 truncate">{activeItem.timestamp}</span>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1 sm:gap-2">
          {/* Photo Specific Tools */}
          {!isVideo && (
            <>
              <button
                onClick={handleZoomIn}
                className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
                title={isArabic ? 'تكبير' : 'Zoom In'}
              >
                <ZoomIn className="w-5 h-5" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
                title={isArabic ? 'تصغير' : 'Zoom Out'}
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              {zoom > 1 && (
                <button
                  onClick={handleResetZoom}
                  className="p-2 rounded-full hover:bg-white/10 text-sky-400 hover:text-sky-300 transition-colors"
                  title={isArabic ? 'الحجم الأصلي' : 'Original Size'}
                >
                  <Maximize className="w-5 h-5" />
                </button>
              )}
              <button
                onClick={handleRotate}
                className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
                title={isArabic ? 'تدوير 90°' : 'Rotate 90°'}
              >
                <RotateCw className="w-5 h-5" />
              </button>
            </>
          )}

          {/* Video Specific Header Tools */}
          {isVideo && (
            <>
              <button
                onClick={handleSpeedCycle}
                className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 text-xs font-bold font-mono text-sky-300 transition-colors flex items-center gap-1"
                title={isArabic ? 'سرعة التشغيل' : 'Playback Speed'}
              >
                <span>{currentSpeed}x</span>
              </button>
              <button
                onClick={togglePiP}
                className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors hidden sm:block"
                title={isArabic ? 'صورة داخل صورة' : 'Picture-in-Picture'}
              >
                <Tv className="w-5 h-5" />
              </button>
            </>
          )}

          {/* Universal Tools */}
          <button
            onClick={handleForwardMedia}
            className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
            title={isArabic ? 'تحويل' : 'Forward'}
          >
            <Share2 className="w-5 h-5" />
          </button>

          <button
            onClick={handleSaveToDevice}
            className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
            title={isArabic ? 'حفظ في الجهاز' : 'Save to device'}
          >
            <Download className="w-5 h-5" />
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors hidden sm:block"
            title={isArabic ? 'ملء الشاشة' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
              setContextMenu({ x: rect.left - 140, y: rect.bottom + 8 });
            }}
            className="p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
            title={isArabic ? 'خيارات إضافية' : 'More options'}
          >
            <MoreVertical className="w-5 h-5" />
          </button>

          <button
            onClick={() => setViewerMedia(null)}
            className="p-2 rounded-full hover:bg-white/15 text-gray-300 hover:text-white transition-colors ml-1"
            title={isArabic ? 'إغلاق (Esc)' : 'Close (Esc)'}
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Main Media Stage */}
      <div
        className="relative flex-1 flex items-center justify-center p-2 sm:p-4 overflow-hidden"
        onContextMenu={(e) => {
          e.preventDefault();
          setContextMenu({ x: e.clientX, y: e.clientY });
        }}
        onClick={() => {
          if (isVideo) {
            togglePlayPause();
          }
        }}
        onDoubleClick={() => {
          if (isVideo) {
            toggleFullscreen();
          } else {
            handleImageDoubleClick();
          }
        }}
        onMouseDown={!isVideo ? handleImageMouseDown : undefined}
        onMouseMove={!isVideo ? handleImageMouseMove : undefined}
        onMouseUp={!isVideo ? handleImageMouseUp : undefined}
      >
        {/* Navigation Arrow: Previous */}
        {currentPlaylist.length > 1 && currentIndex > 0 && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              goToPrev();
            }}
            className={`absolute left-3 sm:left-6 z-20 w-12 h-12 rounded-full bg-black/50 hover:bg-black/80 backdrop-blur-md border border-white/10 flex items-center justify-center text-white/80 hover:text-white hover:scale-110 active:scale-95 transition-all shadow-2xl ${
              showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
            title={isArabic ? 'السابق (السهم الأيسر)' : 'Previous (Left Arrow)'}
          >
            <ChevronLeft className="w-7 h-7" />
          </button>
        )}

        {/* Navigation Arrow: Next */}
        {currentPlaylist.length > 1 && currentIndex < currentPlaylist.length - 1 && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              goToNext();
            }}
            className={`absolute right-3 sm:right-6 z-20 w-12 h-12 rounded-full bg-black/50 hover:bg-black/80 backdrop-blur-md border border-white/10 flex items-center justify-center text-white/80 hover:text-white hover:scale-110 active:scale-95 transition-all shadow-2xl ${
              showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
            title={isArabic ? 'التالي (السهم الأيمن)' : 'Next (Right Arrow)'}
          >
            <ChevronRight className="w-7 h-7" />
          </button>
        )}

        {/* Video Player */}
        {isVideo ? (
          <div className="relative max-h-[82vh] max-w-[94vw] flex items-center justify-center">
            <video
              ref={videoRef}
              src={activeItem.url}
              playsInline
              autoPlay
              loop={isLooping}
              muted={isMuted}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onWaiting={() => setIsBuffering(true)}
              onPlaying={() => {
                setIsBuffering(false);
                setIsPlaying(true);
              }}
              onPause={() => setIsPlaying(false)}
              onEnded={() => {
                if (!isLooping) setIsPlaying(false);
              }}
              className="max-h-[75vh] max-w-[92vw] rounded-xl shadow-2xl object-contain"
            />

            {/* Central Buffering Spinner */}
            {isBuffering && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                <div className="w-14 h-14 border-4 border-white/20 border-t-[#2481cc] rounded-full animate-spin shadow-xl" />
              </div>
            )}

            {/* Central Telegram Paused Play / Ended Replay Overlay Icon */}
            {!isPlaying && !isBuffering && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  togglePlayPause();
                }}
                className="absolute inset-0 m-auto w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-black/60 hover:bg-[#2481cc] text-white flex items-center justify-center backdrop-blur-md border border-white/20 shadow-2xl hover:scale-110 active:scale-95 transition-all z-10 group"
                title={
                  currentTime >= duration && duration > 0 && !isLooping
                    ? (isArabic ? 'إعادة التشغيل' : 'Replay')
                    : (isArabic ? 'تشغيل (المسافة)' : 'Play (Space)')
                }
              >
                {currentTime >= duration && duration > 0 && !isLooping ? (
                  <TelegramReplayIcon className="w-8 h-8 sm:w-10 sm:h-10" />
                ) : (
                  <TelegramPlayIcon className="w-8 h-8 sm:w-10 sm:h-10 ml-0.5" />
                )}
              </button>
            )}

            {/* Quick Seek / Action Feedback Overlay (Telegram Native) */}
            {seekFeedback && (
              <div className="absolute inset-0 m-auto w-24 h-24 rounded-full bg-black/75 backdrop-blur-md border border-white/20 flex flex-col items-center justify-center text-white z-20 pointer-events-none shadow-2xl animate-in zoom-in-75 fade-in duration-150">
                {seekFeedback.dir === 'left' ? (
                  <ChevronLeft className="w-8 h-8 text-[#50a7ea] animate-pulse" />
                ) : (
                  <ChevronRight className="w-8 h-8 text-[#50a7ea] animate-pulse" />
                )}
                <span className="text-xs font-mono font-bold tracking-wider">{seekFeedback.text}</span>
              </div>
            )}
          </div>
        ) : (
          /* Photo Preview */
          <div
            className="flex items-center justify-center max-h-[82vh] max-w-[94vw] overflow-hidden"
            style={{
              cursor: zoom > 1 ? (isDraggingPan ? 'grabbing' : 'grab') : 'default',
            }}
          >
            <img
              src={activeItem.url}
              alt={activeItem.title || 'Photo'}
              className="max-h-[78vh] max-w-[90vw] object-contain rounded-xl shadow-2xl transition-transform duration-100 ease-out select-none pointer-events-auto"
              style={{
                transform: `scale(${zoom}) rotate(${rotation}deg) translate(${pan.x / zoom}px, ${
                  pan.y / zoom
                }px)`,
              }}
              referrerPolicy="no-referrer"
              draggable={false}
            />
          </div>
        )}
      </div>

      {/* Media Caption Floating Bar */}
      {(activeItem.caption || activeItem.title) && (
        <div
          className={`mx-auto mb-2 px-4 py-2 rounded-xl bg-black/70 backdrop-blur-md border border-white/10 text-white text-xs sm:text-sm max-w-2xl text-center shadow-xl transition-opacity duration-300 z-20 ${
            showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
        >
          {activeItem.caption || activeItem.title}
        </div>
      )}

      {/* Bottom Video Controls Bar (Official Telegram Video Controller) */}
      {isVideo && (
        <div
          onClick={(e) => e.stopPropagation()}
          className={`px-4 sm:px-8 py-3 bg-gradient-to-t from-black/95 via-black/80 to-transparent border-t border-white/10 z-30 flex flex-col gap-2.5 transition-opacity duration-300 select-none ${
            showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
        >
          {/* Telegram Native Seek Bar (Scrubber) */}
          <div
            ref={progressBarRef}
            onMouseDown={handleScrubberMouseDown}
            onMouseMove={handleScrubberMouseMove}
            onMouseLeave={handleScrubberMouseLeave}
            className="relative w-full h-4 flex items-center cursor-pointer group/seek select-none py-1"
          >
            {/* Scrubber Background Rail (expands on hover like Telegram) */}
            <div className="w-full h-1 group-hover/seek:h-1.5 bg-white/20 rounded-full overflow-hidden transition-all duration-150 relative">
              {/* Buffered Track */}
              <div
                className="absolute top-0 bottom-0 left-0 bg-white/30 rounded-full transition-all"
                style={{ width: `${bufferedPercent}%` }}
              />
              {/* Played Track (Telegram Blue Gradient) */}
              <div
                className="absolute top-0 bottom-0 left-0 bg-gradient-to-r from-[#2481cc] to-[#50a7ea] rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Scrubber Thumb Knob (Telegram circular white knob with shadow) */}
            <div
              className={`absolute w-3.5 h-3.5 rounded-full bg-white shadow-md shadow-black/60 transform -translate-x-1/2 pointer-events-none transition-transform duration-100 ${
                isDraggingSeek ? 'scale-125' : 'scale-0 group-hover/seek:scale-100'
              }`}
              style={{ left: `${progressPercent}%` }}
            />

            {/* Hover Tooltip Timestamp (Telegram dark frosted glass bubble) */}
            {hoverSeekTime !== null && (
              <div
                className="absolute -top-7 px-2 py-0.5 rounded-lg bg-[#17212b]/95 border border-white/20 text-[11px] font-mono font-bold text-white shadow-2xl pointer-events-none transform -translate-x-1/2 backdrop-blur-md"
                style={{
                  left: `${Math.max(20, Math.min(hoverSeekPos, (progressBarRef.current?.clientWidth || 300) - 20))}px`,
                }}
              >
                {formatTime(hoverSeekTime)}
              </div>
            )}
          </div>

          {/* Controls Row */}
          <div className="flex items-center justify-between text-xs text-gray-300">
            {/* Left: Play/Pause, Time, Volume Toggle & Slider */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Custom Telegram Play/Pause Icon Button */}
              <button
                onClick={togglePlayPause}
                className="w-9 h-9 rounded-full hover:bg-white/15 active:scale-90 flex items-center justify-center text-white hover:text-[#50a7ea] transition-all"
                title={
                  currentTime >= duration && duration > 0 && !isLooping
                    ? (isArabic ? 'إعادة التشغيل' : 'Replay')
                    : isPlaying
                    ? (isArabic ? 'إيقاف مؤقت (المسافة)' : 'Pause (Space)')
                    : (isArabic ? 'تشغيل (المسافة)' : 'Play (Space)')
                }
              >
                {currentTime >= duration && duration > 0 && !isLooping ? (
                  <TelegramReplayIcon className="w-5 h-5" />
                ) : isPlaying ? (
                  <TelegramPauseIcon className="w-5 h-5" />
                ) : (
                  <TelegramPlayIcon className="w-5 h-5 ml-0.5" />
                )}
              </button>

              {/* Time display: clicking toggles remaining vs total time like Telegram Desktop */}
              <button
                onClick={() => setShowRemainingTime(!showRemainingTime)}
                className="font-mono text-xs text-gray-300 hover:text-white transition-colors tracking-wider px-1.5 py-0.5 rounded hover:bg-white/10"
                title={isArabic ? 'تبديل عرض الوقت المتبقي' : 'Toggle remaining time'}
              >
                <span>{formatTime(currentTime)}</span>
                <span className="mx-1 text-gray-500">/</span>
                <span>
                  {showRemainingTime && duration > 0
                    ? `-${formatTime(Math.max(0, duration - currentTime))}`
                    : formatTime(duration)}
                </span>
              </button>

              {/* Telegram Native Volume Toggle & Precision Slider */}
              <div
                className="flex items-center gap-1.5 group/vol ml-1 sm:ml-2 py-1 px-1.5 rounded-xl hover:bg-white/5 transition-colors"
                onWheel={(e) => {
                  e.preventDefault();
                  if (e.deltaY < 0) {
                    handleVolumeChange(Math.min(1, volume + 0.05));
                  } else {
                    handleVolumeChange(Math.max(0, volume - 0.05));
                  }
                }}
              >
                <button
                  onClick={toggleMute}
                  className="p-1 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 active:scale-90 transition-all"
                  title={isMuted ? (isArabic ? 'إلغاء الكتم (M)' : 'Unmute (M)') : (isArabic ? 'كتم الصوت (M)' : 'Mute (M)')}
                >
                  {isMuted || volume === 0 ? (
                    <VolumeX className="w-4 h-4 text-red-400" />
                  ) : volume < 0.5 ? (
                    <Volume1 className="w-4 h-4 text-gray-200" />
                  ) : (
                    <Volume2 className="w-4 h-4 text-gray-200" />
                  )}
                </button>

                {/* Sleek Telegram Volume Slider Track */}
                <div className="relative w-16 sm:w-20 h-4 flex items-center cursor-pointer">
                  <div className="w-full h-1 bg-white/20 rounded-full overflow-hidden relative">
                    <div
                      className="h-full bg-gradient-to-r from-[#2481cc] to-[#50a7ea] rounded-full transition-all"
                      style={{ width: `${(isMuted ? 0 : volume) * 100}%` }}
                    />
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.02"
                    value={isMuted ? 0 : volume}
                    onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    title={`${Math.round((isMuted ? 0 : volume) * 100)}%`}
                  />
                  <div
                    className="absolute w-2.5 h-2.5 rounded-full bg-white shadow-md shadow-black/50 transform -translate-x-1/2 pointer-events-none scale-0 group-hover/vol:scale-100 transition-transform duration-100"
                    style={{ left: `${(isMuted ? 0 : volume) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Right: Loop, Speed, PiP, Fullscreen */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              <button
                onClick={() => setIsLooping(!isLooping)}
                className={`p-1.5 rounded-full transition-colors ${
                  isLooping ? 'bg-[#2481cc]/25 text-[#50a7ea]' : 'hover:bg-white/10 text-gray-400 hover:text-white'
                }`}
                title={isArabic ? 'تكرار الفيديو' : 'Repeat Video'}
              >
                <Repeat className="w-4 h-4" />
              </button>

              <button
                onClick={handleSpeedCycle}
                className="px-2 py-0.5 rounded-md hover:bg-white/10 font-mono font-bold text-xs text-gray-300 hover:text-white transition-colors"
                title={isArabic ? 'السرعة' : 'Speed'}
              >
                {currentSpeed}x
              </button>

              <button
                onClick={toggleFullscreen}
                className="p-1.5 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                title={isArabic ? 'شاشة كاملة' : 'Fullscreen (F)'}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Filmstrip Carousel Strip for Playlist */}
      {currentPlaylist.length > 1 && (
        <div
          ref={thumbnailsRef}
          onClick={(e) => e.stopPropagation()}
          className={`h-16 px-4 py-2 bg-black/80 border-t border-white/10 flex items-center justify-center gap-2 overflow-x-auto no-scrollbar z-30 transition-opacity duration-300 ${
            showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
        >
          {currentPlaylist.map((item, idx) => {
            const isSelected = idx === currentIndex;
            const itemIsVideo =
              item.type === 'video' ||
              item.type === 'video_note' ||
              item.url.toLowerCase().endsWith('.mp4') ||
              item.url.toLowerCase().endsWith('.webm');

            return (
              <button
                key={`${item.url}_${idx}`}
                onClick={() => setViewerMedia(item, currentPlaylist)}
                className={`relative w-12 h-12 rounded-lg overflow-hidden shrink-0 border transition-all ${
                  isSelected
                    ? 'ring-2 ring-[#2481cc] border-[#2481cc] scale-105 opacity-100'
                    : 'border-white/10 opacity-50 hover:opacity-90 hover:scale-100'
                }`}
              >
                {itemIsVideo ? (
                  <div className="w-full h-full bg-slate-900 flex items-center justify-center relative">
                    <video
                      src={item.url}
                      className="w-full h-full object-cover"
                      muted
                      playsInline
                    />
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                      <TelegramPlayIcon className="w-3.5 h-3.5 text-white" />
                    </div>
                  </div>
                ) : (
                  <img
                    src={item.url}
                    alt=""
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Context Menu with 'Save to device' option */}
      {contextMenu && (
        <div
          id="tg-media-viewer-context-menu"
          style={{
            left: `${Math.max(12, Math.min(contextMenu.x, window.innerWidth - 240))}px`,
            top: `${Math.max(12, Math.min(contextMenu.y, window.innerHeight - 320))}px`,
          }}
          onClick={(e) => e.stopPropagation()}
          className="fixed z-50 w-56 py-1.5 px-1 bg-[#17212b]/95 border border-white/15 rounded-2xl shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150 text-xs font-medium text-gray-200 select-none"
        >
          {/* Option 1: Save to device */}
          <button
            onClick={handleSaveToDevice}
            className="w-full flex items-center gap-3 px-3 py-2 hover:bg-[#2481cc]/25 hover:text-[#50a7ea] rounded-xl text-left rtl:text-right transition-colors group"
          >
            <div className="w-7 h-7 rounded-lg bg-[#2481cc]/20 flex items-center justify-center text-[#2481cc] group-hover:bg-[#2481cc] group-hover:text-white transition-colors shrink-0">
              <Download className="w-4 h-4" />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-semibold text-white group-hover:text-[#50a7ea]">
                {isArabic ? 'حفظ في الجهاز' : 'Save to device'}
              </span>
              <span className="text-[10px] text-gray-400 truncate">
                {isArabic ? 'تنزيل إلى مساحة التخزين' : 'Download to local storage'}
              </span>
            </div>
          </button>

          <div className="h-px bg-white/10 my-1 mx-2" />

          {/* Option 2: Copy link */}
          <button
            onClick={() => {
              if (activeItem.url) {
                navigator.clipboard.writeText(activeItem.url).catch(() => {});
                showToast(isArabic ? 'تم نسخ الرابط' : 'Link copied to clipboard', '📋');
              }
              setContextMenu(null);
            }}
            className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/10 rounded-xl text-left rtl:text-right transition-colors"
          >
            <Copy className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{isArabic ? 'نسخ الرابط' : 'Copy link'}</span>
          </button>

          {/* Option 3: Forward */}
          <button
            onClick={() => {
              setContextMenu(null);
              handleForwardMedia();
            }}
            className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/10 rounded-xl text-left rtl:text-right transition-colors"
          >
            <Share2 className="w-4 h-4 text-sky-400 shrink-0" />
            <span>{isArabic ? 'تحويل' : 'Forward'}</span>
          </button>

          {/* Option 4: Open in new tab */}
          <button
            onClick={() => {
              if (activeItem.url) {
                window.open(activeItem.url, '_blank');
              }
              setContextMenu(null);
            }}
            className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/10 rounded-xl text-left rtl:text-right transition-colors"
          >
            <ExternalLink className="w-4 h-4 text-purple-400 shrink-0" />
            <span>{isArabic ? 'فتح في نافذة جديدة' : 'Open in new tab'}</span>
          </button>

          {/* Photo specific: Rotate */}
          {!isVideo && (
            <button
              onClick={() => {
                handleRotate();
                setContextMenu(null);
              }}
              className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/10 rounded-xl text-left rtl:text-right transition-colors"
            >
              <RotateCw className="w-4 h-4 text-amber-400 shrink-0" />
              <span>{isArabic ? 'تدوير 90°' : 'Rotate 90°'}</span>
            </button>
          )}

          {/* Video specific: Picture-in-Picture */}
          {isVideo && (
            <button
              onClick={() => {
                togglePiP();
                setContextMenu(null);
              }}
              className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/10 rounded-xl text-left rtl:text-right transition-colors"
            >
              <Tv className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>{isArabic ? 'صورة داخل صورة' : 'Picture in Picture'}</span>
            </button>
          )}

          <div className="h-px bg-white/10 my-1 mx-2" />

          {/* Option Close */}
          <button
            onClick={() => setContextMenu(null)}
            className="w-full flex items-center gap-3 px-3 py-2 hover:bg-red-500/15 text-red-400 hover:text-red-300 rounded-xl text-left rtl:text-right transition-colors"
          >
            <X className="w-4 h-4 shrink-0" />
            <span>{isArabic ? 'إغلاق' : 'Close'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
