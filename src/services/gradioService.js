import SimplifiedClient from './simplifiedGradioClient';

// The HF Space to connect to - use environment variable if available
const SPACE_NAME = process.env.REACT_APP_GRADIO_SPACE || "sreevarshan/aura-api";

/**
 * Service for interacting with Hugging Face Gradio space
 */
const gradioService = {
  /**
   * Initialize the Gradio client (lazy loading)
   */
  _client: null,
  async getClient() {
    if (!this._client) {
      try {
        // Use our simplified client instead
        this._client = await SimplifiedClient.connect(SPACE_NAME);
        console.log("Connected to Gradio space:", SPACE_NAME);
      } catch (error) {
        console.error("Failed to connect to Gradio space:", error);
        throw new Error(`Failed to connect to Gradio space: ${error.message}`);
      }
    }
    return this._client;
  },

  /**
   * Chat with the model
   * @param {string} message - The user message
   * @param {string} systemMessage - Optional system message
   * @param {Object} options - Additional options
   * @returns {Promise<string>} - The model's response
   */
  async chat(message, systemMessage = "", options = {}) {
    try {
      const client = await this.getClient();
      
      const defaultOptions = {
        max_tokens: 1024,
        temperature: 0.7,
        top_p: 0.95
      };
      
      const params = {
        message: message,
        system_message: systemMessage,
        ...defaultOptions,
        ...options
      };
      
      console.log("Sending request to Gradio API:", { message, systemMessage });
      
      const result = await client.predict("/chat", params);
      
      if (!result || !result.data) {
        throw new Error("Invalid response from Gradio API");
      }
      
      console.log("Received response from Gradio API:", result.data);
      
      return result.data;
    } catch (error) {
      console.error("Error in Gradio chat:", error);
      throw error;
    }
  },
  
  /**
   * Check if the Gradio API is available
   * @returns {Promise<boolean>}
   */
  async checkAvailability() {
    try {
      const client = await this.getClient();
      const result = await client.predict("/chat", {
        message: "test",
        system_message: "This is a test message. Please respond with 'OK'.",
        max_tokens: 10,
        temperature: 0.1,
        top_p: 0.9
      });
      
      return !!result && !!result.data;
    } catch (error) {
      console.error("Gradio API not available:", error);
      return false;
    }
  }
};

export default gradioService; 