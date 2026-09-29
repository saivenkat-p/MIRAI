import React from 'react';

interface CameraBackdropProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  isActive: boolean;
  error: string | null;
}

export const CameraBackdrop: React.FC<CameraBackdropProps> = ({ videoRef, isActive, error }) => {
  return (
    <div className="absolute inset-0 w-full h-full bg-black overflow-hidden flex items-center justify-center">
      {/* Live mirrored video feed */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`w-full h-full object-cover transition-opacity duration-500 ${
          isActive ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ transform: 'scaleX(-1)' }} // Mirror flip
      />

      {/* Fallback / Offline backdrop when physical camera is starting or not present */}
      {!isActive && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8 bg-neutral-900/80">
          <div className="w-16 h-16 rounded-full border-2 border-dashed border-cyan-500/40 animate-spin mb-4" />
          <p className="text-white font-medium text-sm">INITIALIZING MIRROR CAMERA</p>
          <p className="text-xs text-neutral-400 mt-1 max-w-xs">
            {error ? error : 'Connecting to local UVC video device (1080x1920 portrait)...'}
          </p>
        </div>
      )}
    </div>
  );
};
