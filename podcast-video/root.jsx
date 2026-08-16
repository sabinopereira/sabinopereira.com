import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {useAudioData, visualizeAudio} from '@remotion/media-utils';

const FPS = 10;
const DURATION_IN_FRAMES = 11598;

const Waveform = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const audioData = useAudioData(staticFile('episode-01.m4a'));
  if (!audioData) return null;
  const values = visualizeAudio({fps, frame, audioData, numberOfSamples: 64});
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 5, height: 78, width: 720}}>
      {values.map((value, index) => (
        <div
          key={index}
          style={{
            width: 6,
            height: Math.max(6, Math.sqrt(value) * 175),
            borderRadius: 8,
            background: index % 4 === 0 ? '#f2d29b' : '#b97829',
            opacity: 0.62 + Math.sqrt(value) * 0.38,
            boxShadow: value > 0.12 ? '0 0 16px rgba(194,126,43,.45)' : 'none',
          }}
        />
      ))}
    </div>
  );
};

const PodcastVideo = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const breathe = interpolate(Math.sin(frame / 40), [-1, 1], [1.008, 1.028]);
  const entrance = interpolate(frame, [0, 15], [0, 1], {extrapolateRight: 'clamp'});
  const exit = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});
  const opacity = Math.min(entrance, exit);
  return (
    <AbsoluteFill style={{backgroundColor: '#07090b', overflow: 'hidden', opacity}}>
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(circle at 82% 27%, rgba(176,104,31,.28), transparent 34%), radial-gradient(circle at 12% 75%, rgba(73,28,21,.42), transparent 38%), #07090b',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: -45,
          opacity: 0.22,
          filter: 'blur(38px) saturate(.8)',
          transform: `scale(${breathe * 1.09})`,
        }}
      >
        <Img src={staticFile('episode-01-cover.png')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(5,7,8,.98), rgba(5,7,8,.7) 42%, rgba(5,7,8,.25))'}} />
      <div
        style={{
          position: 'absolute',
          top: 76,
          right: 76,
          bottom: 76,
          width: 920,
          overflow: 'hidden',
          border: '1px solid rgba(222,171,93,.28)',
          boxShadow: '0 36px 90px rgba(0,0,0,.65)',
          transform: `scale(${breathe})`,
        }}
      >
        <Img src={staticFile('episode-01-cover.png')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
      <div style={{position: 'absolute', left: 90, top: 110, width: 720, color: '#f6eee0'}}>
        <div style={{fontFamily: 'Arial, sans-serif', fontSize: 20, letterSpacing: 9, color: '#c88936', fontWeight: 700}}>
          SABINO PEREIRA PRESENTS
        </div>
        <div style={{marginTop: 58, fontFamily: 'Georgia, serif', fontSize: 94, lineHeight: 0.91, letterSpacing: -5}}>
          BEYOND<br />THE STORY
        </div>
        <div style={{marginTop: 46, fontFamily: 'Arial, sans-serif', fontSize: 18, letterSpacing: 7, color: '#c88936', fontWeight: 700}}>
          EPISODE 01
        </div>
        <div style={{marginTop: 28, maxWidth: 700, fontFamily: 'Georgia, serif', fontSize: 48, lineHeight: 1.08}}>
          What If the “Toxic Woman” Is Actually Terrified?
        </div>
      </div>
      <div style={{position: 'absolute', left: 90, bottom: 110}}>
        <Waveform />
        <div style={{marginTop: 20, color: '#d6a35b', fontFamily: 'Georgia, serif', fontStyle: 'italic', fontSize: 28}}>
          Stories end. Conversations don’t.
        </div>
      </div>
      <Audio src={staticFile('episode-01.m4a')} />
    </AbsoluteFill>
  );
};

export const PodcastVideoRoot = () => (
  <Composition
    id="BeyondTheStoryEpisode01"
    component={PodcastVideo}
    durationInFrames={DURATION_IN_FRAMES}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
