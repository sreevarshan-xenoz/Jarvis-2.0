import supabase from './supabase';
import gradioService from './gradioService';

// Fallback audio URL for testing when the Supabase function is not available
const FALLBACK_AUDIO_URL = 'https://actions.google.com/sounds/v1/alarms/beep_short.ogg';

/**
 * AI Service - Handles communication with the API server for AI operations
 * 
 * Updated to support the unified input approach:
 * - Regular messages are sent via sendMessage() for conversation
 * - Commands (prefixed with /) are sent via executeCommand()
 * - Both types of interactions appear in the chat history
 */

// Base URL for API calls
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Add a flag to control whether to use the Gradio API
let useGradioApi = true;

// Helper function for API requests
const apiRequest = async (endpoint, method = 'GET', body = null) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed (${url}):`, error);
    throw error;
  }
};

const aiService = {
  /**
   * Get current model status
   */
  getModelStatus: async () => {
    return apiRequest('/status');
  },
  
  /**
   * Execute a command
   * @param {string} command - The command to execute
   * @param {boolean} useAura - Whether to route the command through AURA Core
   */
  executeCommand: async (command, useAura = false) => {
    return apiRequest('/execute', 'POST', { 
      command,
      use_jarvis: useAura  // Keep the API parameter name for backward compatibility
    });
  },
  
  /**
   * Send a message to the AI assistant
   * @param {string} message - The message to send
   * @param {Object} options - Additional options
   */
  sendMessage: async (message, options = {}) => {
    // Try using Gradio API first if enabled
    if (useGradioApi) {
      try {
        const systemMessage = options.systemMessage || "";
        const response = await gradioService.chat(message, systemMessage, {
          temperature: options.temperature || 0.7,
          max_tokens: options.maxTokens || 1024,
          top_p: options.topP || 0.95
        });
        
        return {
          success: true,
          response: response,
          source: 'gradio'
        };
      } catch (error) {
        console.warn("Gradio API failed, falling back to backend API:", error);
        useGradioApi = false; // Disable for future requests in this session
      }
    }
    
    // Fall back to regular API
    return apiRequest('/query', 'POST', { message });
  },
  
  /**
   * Convert text to speech
   * @param {string} text - The text to convert to speech
   */
  textToSpeech: async (text) => {
    return apiRequest('/tts', 'POST', { text });
  },
  
  /**
   * Run diagnostic tests on the AI system
   */
  runDiagnostic: async () => {
    const tests = [];
    
    // Model status test
    try {
      const status = await aiService.getModelStatus();
      tests.push({
        name: 'Model Status',
        success: status.online,
        message: status.status || (status.online ? 'Model is online' : 'Model is offline')
      });
    } catch (error) {
      tests.push({
        name: 'Model Status',
        success: false,
        message: `Error checking model status: ${error.message}`
      });
    }
    
    // Inference test
    try {
      const result = await aiService.sendMessage('Hello, this is a test message.');
      tests.push({
        name: 'Inference',
        success: !!result.response,
        message: result.response ? 'Inference test successful' : 'No response from model'
      });
    } catch (error) {
      tests.push({
        name: 'Inference',
        success: false,
        message: `Error in inference test: ${error.message}`
      });
    }
    
    // Command execution test
    try {
      const result = await aiService.executeCommand('status');
      tests.push({
        name: 'Command Execution',
        success: result.success !== false,
        message: result.message || 'Command execution test successful'
      });
    } catch (error) {
      tests.push({
        name: 'Command Execution',
        success: false,
        message: `Error in command execution test: ${error.message}`
      });
    }
    
    // TTS test
    try {
      const result = await aiService.textToSpeech('This is a test.');
      tests.push({
        name: 'Text-to-Speech',
        success: !!result.audioUrl,
        message: result.audioUrl ? 'TTS test successful' : 'No audio URL returned'
      });
    } catch (error) {
      tests.push({
        name: 'Text-to-Speech',
        success: false,
        message: `Error in TTS test: ${error.message}`
      });
    }
    
    return {
      timestamp: new Date().toLocaleString(),
      tests
    };
  },
  
  /**
   * Get available integrations
   */
  getIntegrations: async () => {
    return apiRequest('/integrations');
  },
  
  /**
   * Get AURA Core status
   */
  getAuraStatus: async () => {
    return apiRequest('/aura/status');
  },
  
  /**
   * Perform an action on AURA Core
   * @param {string} action - The action to perform: 'initialize', 'start', or 'stop'
   */
  auraAction: async (action) => {
    return apiRequest('/aura/action', 'POST', { action });
  },
  
  /**
   * Check if the model is available (including Gradio)
   */
  checkModelAvailability: async () => {
    try {
      // Check Gradio availability
      const gradioAvailable = await gradioService.checkAvailability();
      
      if (gradioAvailable) {
        useGradioApi = true;
        return {
          available: true,
          source: 'gradio',
          message: 'Connected to Hugging Face Gradio API'
        };
      }
      
      // Fall back to backend status check
      const status = await aiService.getModelStatus();
      useGradioApi = false;
      
      return {
        available: status.online,
        source: 'backend',
        message: status.status
      };
    } catch (error) {
      useGradioApi = false;
      console.error("Error checking model availability:", error);
      return {
        available: false,
        source: 'error',
        message: error.message
      };
    }
  }
};

export default aiService; 