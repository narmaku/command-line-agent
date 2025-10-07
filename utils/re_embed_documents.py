"""Re-embed all documents with the correct embedding model."""
import asyncio
import os
from dotenv import load_dotenv

from beeai_framework.backend.embedding import EmbeddingModel
from beeai_framework.backend.vector_store import VectorStore
import psycopg

load_dotenv()


async def re_embed_all():
    """Re-embed all documents from data_vectors using the current embedding model."""
    print("=" * 80)
    print("RE-EMBEDDING ALL DOCUMENTS")
    print("=" * 80)
    
    # Database config
    db_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB", "rag_db"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
    }
    
    # Get embedding model
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    
    print(f"\n1. Creating embedding model: {embedding_provider}:{embedding_model_name}")
    embedding_model = EmbeddingModel.from_name(
        f"{embedding_provider}:{embedding_model_name}",
        truncate_input_tokens=500
    )
    
    # Read data from source table
    print(f"\n2. Reading documents from data_vectors table...")
    conn = await psycopg.AsyncConnection.connect(**db_config)
    
    # Count total
    cursor = await conn.execute("SELECT COUNT(*) FROM data_vectors")
    total_count = (await cursor.fetchone())[0]
    print(f"   Total documents: {total_count:,}")
    
    # Confirm with user
    print(f"\n⚠️  WARNING: This will RE-EMBED all {total_count:,} documents!")
    print(f"   This will take significant time (~{total_count // 100} minutes at 100 docs/min)")
    print(f"   Existing embeddings in langchain_pg_embedding will be DELETED")
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("   Cancelled.")
        await conn.close()
        return
    
    # Delete existing embeddings
    print(f"\n3. Clearing existing langchain_pg_embedding table...")
    await conn.execute("DELETE FROM langchain_pg_embedding WHERE collection_id IN (SELECT uuid FROM langchain_pg_collection WHERE name = 'knowledge_base')")
    await conn.commit()
    print("   Cleared!")
    
    # Read all documents
    print(f"\n4. Reading all documents...")
    cursor = await conn.execute(
        "SELECT id, text, metadata_ FROM data_vectors ORDER BY id"
    )
    rows = await cursor.fetchall()
    print(f"   Loaded {len(rows):,} documents")
    
    # Convert to document format
    print(f"\n5. Preparing documents...")
    
    # Simple class to match BeeAI's expected document format
    class SimpleDocument:
        def __init__(self, content, metadata):
            self.content = content
            self.metadata = metadata
    
    documents = []
    for row_id, text, metadata in rows:
        file_name = metadata.get('file_name', f'doc_{row_id}') if metadata else f'doc_{row_id}'
        
        doc = SimpleDocument(
            content=text,
            metadata={
                "source": file_name,
                "original_id": str(row_id),
            }
        )
        documents.append(doc)
    
    print(f"   Prepared {len(documents):,} documents")
    await conn.close()
    
    # Create vector store and add documents
    print(f"\n6. Creating vector store and embedding documents...")
    print(f"   ⏳ This will take a while...")
    
    connection_string = f"postgresql+psycopg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    
    vector_store = VectorStore.from_name(
        name="langchain:PGVector",
        embedding_model=embedding_model,
        collection_name="knowledge_base",
        connection_string=connection_string,
        use_jsonb=True,
    )
    
    # Add documents in batches to show progress
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        await vector_store.add_documents(documents=batch)
        print(f"   Progress: {min(i+batch_size, len(documents)):,} / {len(documents):,} ({100*min(i+batch_size, len(documents))//len(documents)}%)")
    
    print("\n" + "=" * 80)
    print("✅ RE-EMBEDDING COMPLETE!")
    print("=" * 80)
    print(f"Successfully re-embedded {len(documents):,} documents")
    print(f"Embedding model: {embedding_provider}:{embedding_model_name}")
    print("\nYour RAG database is now ready with consistent embeddings!")


if __name__ == "__main__":
    asyncio.run(re_embed_all())

