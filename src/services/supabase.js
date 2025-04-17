import { createClient } from '@supabase/supabase-js';

// Supabase Configuration
const supabaseUrl = 'https://yrut1xveshjsmwutdgwv.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlydXQxeHZlc2hqc213dXRkZ3d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQ1MjU3MDcsImV4cCI6MjA0MDEwMTcwN30.jYWkKNdg9p6nY2OYj4IEbF3yGijz1VPOlKBFv6vGqq8';

// Initialize Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase; 