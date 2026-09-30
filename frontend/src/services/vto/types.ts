/**
 * MIRAI — Live Virtual Try-On (VTO) Provider Architecture
 *
 * Pluggable streaming interface decoupling the Live VTO engine from the MIRAI Smart Mirror UI.
 * Designed specifically for Real-Time Streaming Neural Video models (e.g. Decart Lucy V-TON).
 */

export type VTOConnectionState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'
  | 'error';

export interface VTOQualityReport {
  latencyMs?: number;
  fps?: number;
  packetLossPercent?: number;
  quality?: 'excellent' | 'good' | 'poor';
}

export interface GarmentReference {
  productId: string;
  name: string;
  category: string;
  /**
   * Reference garment image URL or data URI.
   * Sent to the neural video model to guide cloth synthesis.
   */
  referenceImageUrl: string;
  /**
   * Detailed conditioning prompt for the neural VTO model.
   * E.g. "Relaxed Camp-Collar Linen Shirt, natural flax, front buttons, short sleeves, camp collar"
   */
  vtonPrompt: string;
  /**
   * Whether this product has a tested, verified garment reference ready for Live VTO.
   * If false, Live VTO is disallowed to prevent displaying incorrect garments.
   */
  isLiveVTOReady: boolean;
}

export type VTOEventMap = {
  stream: MediaStream;
  stateChange: VTOConnectionState;
  error: Error;
  quality: VTOQualityReport;
};

export interface ILiveVTOProvider {
  readonly id: string;
  readonly name: string;
  readonly modelName: string;

  /**
   * Connects the local webcam stream to the real-time VTO session via WebRTC.
   * @param cameraStream The customer's local webcam MediaStream
   * @param initialGarment The starting garment reference to apply
   */
  connect(cameraStream: MediaStream, initialGarment?: GarmentReference): Promise<void>;

  /**
   * Dynamically updates the active garment during an ongoing live session.
   * Does NOT tear down the WebRTC connection.
   */
  setGarment(garment: GarmentReference): Promise<void>;

  /**
   * Returns the transformed remote video stream received from the neural model.
   * When connected, this stream is played in the mirror viewport.
   */
  getRemoteStream(): MediaStream | null;

  /**
   * Returns current connection state.
   */
  getConnectionState(): VTOConnectionState;

  /**
   * Closes the session and releases WebRTC resources.
   */
  disconnect(): void;

  on<K extends keyof VTOEventMap>(event: K, listener: (data: VTOEventMap[K]) => void): void;
  off<K extends keyof VTOEventMap>(event: K, listener: (data: VTOEventMap[K]) => void): void;
}
