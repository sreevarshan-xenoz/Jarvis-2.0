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
   * Initialize WebSocket connection
   */
  initWebSocket() {
    if (this.ws) {
      this.ws.close();
    }

    try {
      this.ws = new WebSocket(this.wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connection established');
        this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
      };
      
      this.ws.onclose = (event) => {
        console.log('WebSocket connection closed', event.code);
        
        // Don't reconnect if the connection was closed normally
        if (event.code !== 1000) {
          this.handleReconnect();
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Let onclose handle reconnection
      };

      return this.ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleReconnect();
      return null;
    }
  }

  /**
   * Handle WebSocket reconnection
   */
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = setTimeout(() => {
        this.initWebSocket();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  /**
   * Clean up WebSocket connection
   */
  cleanup() {
    clearTimeout(this.reconnectTimeout);
    if (this.ws) {
      this.ws.close(1000); // Normal closure
    }
    if (this.mediaRecorder) {
      if (this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
      }
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
  }

  /**
   * Initialize audio context and media recorder
   */
  async initAudioRecording() {
    try {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(event.data);
        }
      };

      return true;
    } catch (error) {
      console.error('Error initializing audio recording:', error);
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
    this.isListening = false;
  }

  /**
   * Initialize speech recognition
   */
  initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
      throw new Error('Speech recognition not supported in this browser');
    }

    this.recognition = new window.webkitSpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
  }

  /**
   * Start speech recognition
   * @param {Function} onResult - Callback for recognition results
   * @param {Function} onError - Callback for errors
   */
  startListening(onResult, onError) {
    if (!this.recognition) {
      this.initSpeechRecognition();
    }

    this.recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      if (result.isFinal) {
        onResult(result[0].transcript);
      }
    };

    this.recognition.onerror = (event) => {
      onError(event.error);
    };

    this.recognition.start();
    this.isListening = true;
  }

  /**
   * Stop speech recognition
   */
  stopListening() {
    if (this.recognition) {
      this.recognition.stop();
      this.isListening = false;
    }
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
   * Convert text to speech using backend TTS service
   * @param {string} text - Text to convert to speech
   * @param {string} apiUrl - URL of the TTS API endpoint
   * @returns {Promise<string>} - URL of the generated audio file
   */
  async generateSpeech(text, apiUrl) {
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate speech');
      }

      const data = await response.json();
      return data.audioUrl;
    } catch (error) {
      console.error('TTS error:', error);
      throw error;
    }
  }

  /**
   * Play audio from URL
   * @param {string} audioUrl - URL of the audio file to play
   * @returns {Promise} - Resolves when audio playback is complete
   */
  async playAudio(audioUrl) {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      audio.onended = resolve;
      audio.onerror = reject;
      audio.play().catch(reject);
    });
  }

  /**
   * Queue audio for sequential playback
   * @param {string} audioUrl - URL of the audio file to queue
   */
  queueAudio(audioUrl) {
    this.audioQueue.push(audioUrl);
    this.processAudioQueue();
  }

  /**
   * Process audio queue
   */
  async processAudioQueue() {
    if (this.isProcessing || this.audioQueue.length === 0) {
      return;
    }

    this.isProcessing = true;
    while (this.audioQueue.length > 0) {
      const audioUrl = this.audioQueue.shift();
      try {
        await this.playAudio(audioUrl);
      } catch (error) {
        console.error('Audio playback error:', error);
      }
    }
    this.isProcessing = false;
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
}

export default new VoiceService(); 