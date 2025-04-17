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
      // Call the Edge Function in Supabase that will process the Gemma 2B model request
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
}

export default new AIService(); 