// Template for Supabase configuration
// Copy this file to supabase-config.js and fill in your actual credentials
window.supabaseConfig = {
  supabaseUrl: "YOUR_SUPABASE_URL",
  supabaseKey: "YOUR_SUPABASE_ANON_KEY"
};

// Initialize Supabase client
window.initSupabase = function() {
  if (window.supabaseConfig.supabaseUrl === "YOUR_SUPABASE_URL") {
    console.warn("Supabase not configured. Please update supabase-config.js with your credentials.");
    window.supabaseClient = null;
    return false;
  }
  
  try {
    window.supabaseClient = supabase.createClient(
      window.supabaseConfig.supabaseUrl,
      window.supabaseConfig.supabaseKey
    );
    console.log("Supabase client initialized");
    return true;
  } catch (error) {
    console.error("Failed to initialize Supabase client:", error);
    window.supabaseClient = null;
    return false;
  }
}; 