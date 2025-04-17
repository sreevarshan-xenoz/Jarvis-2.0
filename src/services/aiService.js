import supabase from './supabase';

// Fallback audio URL for testing when the Supabase function is not available
const FALLBACK_AUDIO_URL = 'https://actions.google.com/sounds/v1/alarms/beep_short.ogg';

/**
 * AI Service to handle interactions with the Gemma 2B model through Supabase
 */
class AIService {
  /**
   * Sends a message to the AI and gets a response
   * @param {string} message - The user's message
   * @returns {Promise<string>} - The AI's response
   */
  async sendMessage(message) {
    try {
      // For development testing purposes, return a mock successful response if Supabase isn't configured
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode detected, attempting to use Supabase function with fallback');
        try {
          const { data, error } = await supabase.functions.invoke('gemma-2b-chat', {
            body: { message }
          });

          if (error) throw error;
          return data.response;
        } catch (error) {
          console.warn('Could not connect to Supabase Edge Function in development mode, returning mock response');
          
          // Return mock response
          const responses = [
            "I'm a simulated response from the Gemma 2B model in development mode. Your actual model isn't connected yet.",
            "This is a development mode response. The real Gemma 2B model will provide more helpful answers when connected.",
            "Development mode activated. I'm not the real Gemma 2B model, just a placeholder until your backend is configured."
          ];
          
          return responses[Math.floor(Math.random() * responses.length)];
        }
      }

      // Production mode - Call the Edge Function in Supabase
      const { data, error } = await supabase.functions.invoke('gemma-2b-chat', {
        body: { message }
      });

      if (error) {
        console.error('Error calling Gemma 2B model:', error);
        throw new Error(error.message || 'Failed to get response from AI');
      }

      return data.response;
    } catch (error) {
      console.error('Error in AI service:', error);
      throw error;
    }
  }

  /**
   * Executes a custom command using the Python backend
   * @param {string} command - The command to execute
   * @returns {Promise<object>} - The result of the command execution
   */
  async executeCommand(command) {
    try {
      // Call the Edge Function in Supabase that will process the custom command
      const { data, error } = await supabase.functions.invoke('execute-command', {
        body: { command }
      });

      if (error) {
        console.error('Error executing command:', error);
        throw new Error(error.message || 'Failed to execute command');
      }

      return data;
    } catch (error) {
      console.error('Error in command execution:', error);
      throw error;
    }
  }

  /**
   * Fetches the AI model status
   * @returns {Promise<object>} - The status of the AI model
   */
  async getModelStatus() {
    try {
      // For development testing purposes, return a mock successful response
      // Remove this condition in production
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode detected, returning mock model status');
        return {
          online: true,
          status: 'Gemma 2B model is online (Development Mode)',
          model: 'Gemma 2B',
          memory_usage: '4.2GB',
          load: 0.3
        };
      }

      const { data, error } = await supabase.functions.invoke('model-status', {
        method: 'GET'
      });

      if (error) {
        console.error('Error fetching model status:', error);
        throw new Error(error.message || 'Failed to get model status');
      }

      return data;
    } catch (error) {
      console.error('Error in model status check:', error);
      throw error;
    }
  }

  /**
   * Converts text to speech
   * @param {string} text - The text to convert to speech
   * @returns {Promise<object>} - The result containing the audio URL
   */
  async textToSpeech(text) {
    try {
      // For development testing purposes, return a mock audio URL
      // Remove this condition in production
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode detected, returning mock audio URL');
        return {
          audioUrl: FALLBACK_AUDIO_URL,
          duration: 2.1
        };
      }

      const { data, error } = await supabase.functions.invoke('text-to-speech', {
        body: { text }
      });

      if (error) {
        console.error('Error converting text to speech:', error);
        throw new Error(error.message || 'Failed to convert text to speech');
      }

      if (!data || !data.audioUrl) {
        console.error('Invalid response from text-to-speech function:', data);
        throw new Error('No audio URL returned from service');
      }

      return data;
    } catch (error) {
      console.error('Error in text-to-speech conversion:', error);
      // In production, you might want to throw the error instead of returning a fallback
      // For better UX during development, we'll return a fallback
      if (process.env.NODE_ENV === 'development') {
        console.log('Returning fallback audio URL due to error');
        return {
          audioUrl: FALLBACK_AUDIO_URL,
          duration: 2.1,
          error: error.message
        };
      }
      throw error;
    }
  }

  /**
   * Run a diagnostic test on the AI model
   * @returns {Promise<object>} - The diagnostic results
   */
  async runDiagnostic() {
    try {
      console.log('Running AI model diagnostic...');
      
      // 1. Test the model status
      const statusResult = { success: false, message: '', details: {} };
      try {
        const status = await this.getModelStatus();
        statusResult.success = status.online;
        statusResult.message = status.online ? 'Model is online' : 'Model is offline';
        statusResult.details = status;
      } catch (error) {
        statusResult.message = `Status check failed: ${error.message}`;
        statusResult.details = { error: error.message };
      }
      
      // 2. Test a simple inference request
      const inferenceResult = { success: false, message: '', details: {} };
      try {
        const response = await this.sendMessage('Hello, this is a diagnostic test.');
        inferenceResult.success = Boolean(response);
        inferenceResult.message = response ? 'Inference test successful' : 'Inference test failed - no response';
        inferenceResult.details = { response: response ? response.substring(0, 100) + '...' : 'No response' };
      } catch (error) {
        inferenceResult.message = `Inference test failed: ${error.message}`;
        inferenceResult.details = { error: error.message };
      }
      
      // 3. Test a simple command execution
      const commandResult = { success: false, message: '', details: {} };
      try {
        const result = await this.executeCommand('status');
        commandResult.success = Boolean(result && result.success);
        commandResult.message = result && result.success ? 'Command test successful' : 'Command test failed';
        commandResult.details = result || { error: 'No result returned' };
      } catch (error) {
        commandResult.message = `Command test failed: ${error.message}`;
        commandResult.details = { error: error.message };
      }
      
      // 4. Test text-to-speech functionality
      const ttsResult = { success: false, message: '', details: {} };
      try {
        const result = await this.textToSpeech('This is a TTS test.');
        ttsResult.success = Boolean(result && result.audioUrl);
        ttsResult.message = result && result.audioUrl ? 'TTS test successful' : 'TTS test failed - no audio URL';
        ttsResult.details = result || { error: 'No result returned' };
      } catch (error) {
        ttsResult.message = `TTS test failed: ${error.message}`;
        ttsResult.details = { error: error.message };
      }
      
      // Overall diagnostic result
      const overallSuccess = statusResult.success && inferenceResult.success && 
                            commandResult.success && ttsResult.success;
                            
      return {
        success: overallSuccess,
        message: overallSuccess ? 'All diagnostic tests passed' : 'Some diagnostic tests failed',
        tests: {
          modelStatus: statusResult,
          inference: inferenceResult,
          command: commandResult,
          tts: ttsResult
        },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error running diagnostic:', error);
      return {
        success: false,
        message: `Diagnostic failed with error: ${error.message}`,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

export default new AIService(); 