// Follow this setup guide to integrate the Supabase Edge Functions with your API server:
// https://supabase.com/docs/guides/functions

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

console.log('Gemini API Chat Function started')

interface RequestBody {
  message: string
}

serve(async (req) => {
  try {
    // Extract the message from the request body
    const { message } = await req.json() as RequestBody
    
    if (!message) {
      return new Response(
        JSON.stringify({ error: 'Message is required' }),
        { headers: { 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Call your API server that connects to Gemini
    const apiUrl = Deno.env.get('GEMINI_API_URL') || 'http://localhost:8000/chat'
    const apiKey = Deno.env.get('GEMINI_API_KEY') || ''

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': apiKey ? `Bearer ${apiKey}` : ''
      },
      body: JSON.stringify({ message })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `API responded with status ${response.status}`)
    }

    const data = await response.json()

    return new Response(
      JSON.stringify({ 
        response: data.response || 'No response from model',
        model: data.model || 'Gemini Pro'
      }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Error in Gemini Chat function:', error)
    
    // For development/testing, return mock data if the real API fails
    if (Deno.env.get('ENVIRONMENT') === 'development') {
      console.log('Development environment detected, returning mock response')
      return new Response(
        JSON.stringify({ 
          response: "This is a mock response from Gemini for development purposes. Your actual model connection isn't working yet.", 
          model: "Gemini Pro (Mock)"
        }),
        { headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    return new Response(
      JSON.stringify({ 
        error: error.message || 'Internal server error',
        details: 'Failed to process message with Gemini model'
      }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
}) 