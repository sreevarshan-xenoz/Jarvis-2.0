// Follow this setup guide to integrate the Supabase Edge Functions with your API server:
// https://supabase.com/docs/guides/functions

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

console.log('Model Status function started')

serve(async (req) => {
  try {
    // Call your API server to check model status
    const apiUrl = Deno.env.get('STATUS_API_URL') || 'http://localhost:8000/status'
    const apiKey = Deno.env.get('GEMINI_API_KEY') || ''

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': apiKey ? `Bearer ${apiKey}` : ''
      }
    })

    if (!response.ok) {
      throw new Error('Failed to get model status')
    }

    const data = await response.json()

    return new Response(
      JSON.stringify({ 
        online: data.online || false,
        status: data.status || 'Unknown status',
        model: data.model || 'Gemini Pro',
        memory_usage: data.memory_usage || null,
        load: data.load || null
      }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Error in Model Status function:', error)
    
    // Return offline status on error
    return new Response(
      JSON.stringify({ 
        online: false, 
        status: 'Error checking model status',
        error: error.message || 'Internal server error'
      }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
}) 