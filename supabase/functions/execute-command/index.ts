// Follow this setup guide to integrate the Supabase Edge Functions with your API server:
// https://supabase.com/docs/guides/functions

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

console.log('Execute Command function started')

interface RequestBody {
  command: string
}

serve(async (req) => {
  try {
    // Extract the command from the request body
    const { command } = await req.json() as RequestBody
    
    if (!command) {
      return new Response(
        JSON.stringify({ success: false, message: 'Command is required' }),
        { headers: { 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Call your API server to execute the command
    const apiUrl = Deno.env.get('COMMAND_API_URL') || 'http://localhost:8000/execute'
    const apiKey = Deno.env.get('GEMINI_API_KEY') || ''

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': apiKey ? `Bearer ${apiKey}` : ''
      },
      body: JSON.stringify({ command })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to execute command')
    }

    const data = await response.json()

    return new Response(
      JSON.stringify(data),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Error in Execute Command function:', error)
    
    return new Response(
      JSON.stringify({ success: false, message: error.message || 'Internal server error' }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
}) 