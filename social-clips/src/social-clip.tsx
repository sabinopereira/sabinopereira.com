import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

type Props = {start: number; duration: number; hook: string};

const gold = '#d3943e';

export const SocialClip: React.FC<Props> = ({start, hook}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const fade = interpolate(frame, [0, 12, durationInFrames - 12, durationInFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const progress = frame / durationInFrames;
  return (
    <AbsoluteFill style={{backgroundColor: '#070707', color: '#f3eee5', fontFamily: 'Arial, Helvetica, sans-serif'}}>
      <OffthreadVideo
        src={staticFile('episode.mp4')}
        startFrom={start * fps}
        style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(28px) brightness(0.22)', transform: 'scale(1.15)'}}
      />
      <AbsoluteFill style={{background: 'linear-gradient(180deg,rgba(0,0,0,.45),rgba(0,0,0,.05) 45%,rgba(0,0,0,.82))'}} />
      <div style={{position: 'absolute', top: 82, left: 70, right: 70, display: 'flex', alignItems: 'center', gap: 18}}>
        <div style={{height: 3, width: 74, background: gold}} />
        <div style={{fontSize: 27, letterSpacing: 7, color: gold, fontWeight: 700}}>SABINO PEREIRA PRESENTS</div>
      </div>
      <div style={{position: 'absolute', top: 255, left: 70, right: 70, opacity: fade}}>
        <div style={{fontSize: 76, lineHeight: 1.06, fontWeight: 900, whiteSpace: 'pre-line', textShadow: '0 5px 28px #000'}}>{hook}</div>
        <div style={{height: 5, width: 160, background: gold, marginTop: 34}} />
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 720, height: 620, border: `2px solid ${gold}55`, borderRadius: 34, overflow: 'hidden', boxShadow: '0 25px 90px #000'}}>
        <OffthreadVideo src={staticFile('episode.mp4')} startFrom={start * fps} style={{width: '100%', height: '100%', objectFit: 'cover'}} muted />
      </div>
      <div style={{position: 'absolute', left: 70, right: 70, bottom: 215, textAlign: 'center'}}>
        <div style={{fontSize: 35, letterSpacing: 9, fontWeight: 800}}>BEYOND THE STORY</div>
        <div style={{fontSize: 25, letterSpacing: 2.5, color: gold, marginTop: 14}}>STORIES END. CONVERSATIONS DON’T.</div>
        <div style={{fontSize: 26, marginTop: 30, color: '#ddd'}}>Full episode • YouTube & Spotify</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 12, background: '#29231d'}}>
        <div style={{height: '100%', width: `${progress * 100}%`, background: gold}} />
      </div>
    </AbsoluteFill>
  );
};
