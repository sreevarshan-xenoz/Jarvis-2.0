/**
 * Simplified Gradio API client for browser environments
 * This avoids using Node.js-specific modules
 */
class SimplifiedGradioClient {
  constructor(spaceUrl) {
    this.baseUrl = spaceUrl.startsWith('http') 
      ? spaceUrl 
      : `https://${spaceUrl.replace('/', '-')}.hf.space`;
    this.apiUrl = `${this.baseUrl}/api`;
    this.initialized = false;
    this.sessionHash = null;
  }

  async init() {
    if (this.initialized) return;
    
    try {
      // Get session hash
      const response = await fetch(`${this.apiUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fn_index: 0, // Use the first function by default
          data: [],
          session_hash: null,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to initialize: ${response.statusText}`);
      }
      
      const data = await response.json();
      this.sessionHash = data.session_hash;
      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize Gradio client:', error);
      throw error;
    }
  }

  async predict(endpoint, params) {
    await this.init();
    
    const fnIndex = endpoint === '/chat' ? 0 : 1; // Assume chat is the first function
    
    try {
      const response = await fetch(`${this.apiUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fn_index: fnIndex,
          data: [
            params.message,
            params.system_message || '',
            params.temperature || 0.7,
            params.top_p || 0.95,
            params.max_tokens || 1024
          ],
          session_hash: this.sessionHash,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      return {
        data: result.data[0] // Assuming first element is the response
      };
    } catch (error) {
      console.error('Prediction error:', error);
      throw error;
    }
  }
}

/**
 * Create a connection to a Gradio space
 */
export async function connect(spaceName) {
  const client = new SimplifiedGradioClient(spaceName);
  await client.init();
  return client;
}

export default {
  connect
}; 