"""IT Help Desk RAG assistant."""

import truststore

# Verify TLS against the OS certificate store instead of certifi's bundle, so HTTPS to
# OpenAI/Pinecone works behind corporate proxies that re-sign traffic with an internal CA.
truststore.inject_into_ssl()
