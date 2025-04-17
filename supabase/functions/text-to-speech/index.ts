// Follow this setup guide to integrate the Supabase Edge Functions with your Python backend:
// https://supabase.com/docs/guides/functions

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

console.log('Text-to-Speech function started')

interface RequestBody {
  text: string
}

serve(async (req) => {
  try {
    // Extract the text from the request body
    const { text } = await req.json() as RequestBody
    
    if (!text) {
      return new Response(
        JSON.stringify({ error: 'Text is required' }),
        { headers: { 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Call your Python backend for TTS conversion
    const apiUrl = Deno.env.get('TTS_API_URL') || 'http://localhost:8000/tts'
    const apiKey = Deno.env.get('TTS_API_KEY') || ''

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({ text })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to convert text to speech')
    }

    const data = await response.json()

    return new Response(
      JSON.stringify({ 
        audioUrl: data.audioUrl,
        duration: data.duration || null
      }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Error in Text-to-Speech function:', error)
    
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
}) 