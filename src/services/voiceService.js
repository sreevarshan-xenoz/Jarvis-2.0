/**
 * Voice Service - Handles text-to-speech and speech-to-text functionality
 */

class VoiceService {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.audioContext = null;
    this.audioQueue = [];
    this.isProcessing = false;
    this.ws = null;
    this.mediaRecorder = null;
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/voice';
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
  }

  /**
   * Initialize WebSocket connection for real-time voice
   */
  initWebSocket() {
    if (this.ws) {
      this.ws.close();
    }

    this.ws = new WebSocket(this.wsUrl);
    
    this.ws.onopen = () => {
      console.log('WebSocket connection established');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket connection closed');
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectTimeout = setTimeout(() => {
          this.reconnectAttempts++;
          this.initWebSocket();
        }, 2000);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  /**
   * Initialize audio recording
   */
  async initAudioRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      this.mediaRecorder = new MediaRecorder(stream);
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(event.data);
        }
      };
      
      return true;
    } catch (error) {
      console.error('Failed to initialize audio recording:', error);
      return false;
    }
  }

  /**
   * Start real-time voice recognition
   * @param {Function} onTranscript - Callback for transcription results
   * @param {Function} onError - Callback for errors
   */
  async startRealtimeRecognition(onTranscript, onError) {
    if (!this.ws) {
      this.initWebSocket();
    }

    if (!this.mediaRecorder) {
      const initialized = await this.initAudioRecording();
      if (!initialized) {
        onError('Failed to initialize audio recording');
        return;
      }
    }

    // Set up WebSocket message handler
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'transcript') {
          onTranscript(data.text);
        } else if (data.type === 'error') {
          onError(data.message);
        }
      } catch (error) {
        onError('Error processing server response');
      }
    };

    // Start recording
    this.mediaRecorder.start(1000); // Send audio data every second
    this.isListening = true;
  }

  /**
   * Stop real-time voice recognition
   */
  stopRealtimeRecognition() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isListening = false;
  }

  /**
   * Enhanced speak method with voice options and error handling
   */
  async speak(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Apply options with fallbacks
      utterance.rate = Math.max(0.1, Math.min(options.rate || 1.0, 2.0));
      utterance.pitch = Math.max(0.1, Math.min(options.pitch || 1.0, 2.0));
      utterance.volume = Math.max(0, Math.min(options.volume || 1.0, 1.0));
      utterance.lang = options.language || navigator.language || 'en-US';

      // Set voice if specified and available
      if (options.voice) {
        const voices = this.synthesis.getVoices();
        const selectedVoice = voices.find(v => v.name === options.voice);
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
      }

      // Handle various speech synthesis events
      utterance.onend = () => resolve();
      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error);
        reject(error);
      };
      utterance.onpause = () => console.log('Speech paused');
      utterance.onresume = () => console.log('Speech resumed');
      utterance.onmark = (event) => console.log('Speech mark reached:', event.name);
      utterance.onboundary = (event) => console.log('Word boundary reached:', event.charIndex);

      try {
        this.synthesis.speak(utterance);
      } catch (error) {
        console.error('Failed to start speech synthesis:', error);
        reject(error);
      }
    });
  }

  /**
   * Stop speaking
   */
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  /**
   * Get available voices with fallback
   */
  getVoices() {
    if (!this.synthesis) return [];
    
    const voices = this.synthesis.getVoices();
    if (voices.length === 0) {
      // Return a default voice if none are available
      return [{
        name: 'Default',
        lang: navigator.language || 'en-US'
      }];
    }
    return voices;
  }

  /**
   * Clean up resources
   */
  cleanup() {
    this.stopRealtimeRecognition();
    this.stopSpeaking();
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
  }
}

// Create and export a singleton instance
const voiceService = new VoiceService();
export default voiceService; 