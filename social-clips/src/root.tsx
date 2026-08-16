import React from 'react';
import {Composition} from 'remotion';
import {SocialClip} from './social-clip';

const clips = [
  {id: 'Clip01', start: 0, duration: 45, hook: 'WHAT IF “TOXIC”\nACTUALLY MEANS\nTERRIFIED?'},
  {id: 'Clip02', start: 360, duration: 45, hook: 'WHEN DOES\nSELF-PROTECTION\nBECOME CONTROL?'},
  {id: 'Clip03', start: 720, duration: 45, hook: 'CAN THE WOUNDED\nSTILL BE RESPONSIBLE\nFOR THE WOUNDS THEY CAUSE?'}
];

export const Root: React.FC = () => <>
  {clips.map((clip) => (
    <Composition
      key={clip.id}
      id={clip.id}
      component={SocialClip}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={clip.duration * 30}
      defaultProps={clip}
    />
  ))}
</>;
