// Follow this setup guide to integrate the Supabase Edge Functions with your Gemma 2B model:
// https://supabase.com/docs/guides/functions

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

console.log('Gemma 2B Chat function started')

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

    // Here you would typically call your Python backend that hosts the Gemma 2B model
    // For now, we'll mock the response
    // Replace this with your actual API call to your Python backend running the Gemma 2B model
    
    // Example of how to call an external API
    const apiUrl = Deno.env.get('GEMMA_API_URL') || 'http://localhost:8000/chat'
    const apiKey = Deno.env.get('GEMMA_API_KEY') || ''

    const modelResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({ message })
    })

    if (!modelResponse.ok) {
      const errorData = await modelResponse.json()
      throw new Error(errorData.message || 'Failed to get response from Gemma 2B model')
    }

    const data = await modelResponse.json()

    return new Response(
      JSON.stringify({ response: data.response }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Error in Gemma 2B chat function:', error)
    
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
}) 