import React from 'react';
import { MirrorView } from './components/MirrorView';

export const App: React.FC = () => {
  return (
    <div className="w-screen h-screen overflow-hidden bg-black">
      <MirrorView />
    </div>
  );
};

export default App;
