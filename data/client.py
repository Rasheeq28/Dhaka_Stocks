from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions # Add this import
from config.settings import SUPABASE_URL, SUPABASE_KEY

# Wrap your settings in the ClientOptions object
# This prevents the 'dict' object has no attribute error
opts = ClientOptions(
    postgrest_client_timeout=45,
    storage_client_timeout=45,
    schema="public"
)

# Initialize the client using the options object
supabase_client: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=opts
)