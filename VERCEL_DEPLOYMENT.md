# Deploying AURA to Vercel

This guide explains how to deploy the AURA API server to Vercel as a serverless application.

## Prerequisites

1. A [Vercel](https://vercel.com) account
2. [Vercel CLI](https://vercel.com/docs/cli) installed
3. Git repository with your AURA code

## Troubleshooting Common Errors

### Dependency Installation Failures

If you encounter errors like this during deployment:

```
Error: Command failed: pip3.12 install --disable-pip-version-check --target . --upgrade -r /vercel/path1/requirements.txt
error: subprocess-exited-with-error
```

This is usually caused by:

1. **System-level dependencies** that can't be installed in Vercel's environment:
   - `PyAudio`, `pywin32`, `python-vlc`, etc.
   
2. **Large ML packages** that exceed size or build time limits:
   - `torch`, `transformers`, large model weights

**Solution**: Use the simplified `requirements.txt` included in this project that:
- Includes only core API dependencies
- Uses Google's Gemini API instead of local models
- Avoids system-level dependencies

### Memory Limit Exceeded

If your function crashes with memory errors:

**Solution**: The `vercel.json` file includes increased memory limits:
```json
"functions": {
  "api_server.py": {
    "memory": 1024,
    "maxDuration": 10
  }
}
```

## Steps to Deploy

### 1. Login to Vercel

```bash
vercel login
```

### 2. Configure Environment Variables

You'll need to set up the following environment variables in Vercel:

- `USE_HUGGINGFACE`: Set to "true" to use the Hugging Face model
- `HF_MODEL_NAME`: Your Hugging Face model name (e.g., "naxwinn/qlora-jarvis-output")
- `GEMINI_API_KEY`: Your Google Gemini API key (as fallback)
- `GEMINI_MODEL`: The Gemini model to use (e.g., "gemini-pro")

You can set these either through the Vercel dashboard or using the CLI:

```bash
vercel env add USE_HUGGINGFACE
vercel env add HF_MODEL_NAME
vercel env add GEMINI_API_KEY
vercel env add GEMINI_MODEL
```

### 3. Deploy the Application

From your project directory, run:

```bash
vercel --prod
```

### 4. Limitations and Considerations

#### Cold Start

Serverless functions have a "cold start" delay when they haven't been used for a while. The first request after a period of inactivity may take longer to respond.

#### Execution Time Limits

Vercel has execution time limits for serverless functions:
- Hobby plan: 10 seconds
- Pro plan: 60 seconds
- Enterprise plan: 900 seconds

Loading large ML models like the Hugging Face transformer may exceed these limits. Consider using a smaller model or offloading model hosting to a dedicated service like Hugging Face Inference API.

#### File Storage

The TTS feature generates audio files. On Vercel, these files should be saved to the `public` directory, but these files are ephemeral and won't persist between function invocations. Consider using:

- External storage service (S3, Google Cloud Storage)
- A dedicated TTS service with direct URL responses

### 5. Post-Deployment

After deployment, you'll receive a URL for your API. Update the frontend to use this URL by setting:

```
REACT_APP_API_URL=https://your-vercel-deployment-url.vercel.app
```

## Alternative Approaches

If your model is too large for Vercel's serverless functions:

1. **Use Hugging Face Inference API**: Instead of hosting the model yourself, use the Hugging Face hosted inference API
2. **Deploy the Backend Separately**: Use a service like Railway, Render, or a traditional VPS that can handle larger models
3. **Use Smaller Models**: Fine-tune smaller versions of the models that fit within Vercel's limitations 