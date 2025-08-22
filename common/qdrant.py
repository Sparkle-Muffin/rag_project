from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

import subprocess
from pathlib import Path


def ensure_qdrant_running():
    container_name = "qdrant_container"
    """Ensure Qdrant container is running, creating it if needed."""
    # Check if container exists and get its status
    command = f"docker ps -a --filter name={container_name}"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if len(result.stdout.strip().splitlines()) > 1:
            # Docker ps output contains multiple columns, we need to parse it carefully
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip the header line
                columns = line.split()
                if columns[-1] == container_name:
                    if 'Up' in line:
                        print("Qdrant container is already running")
                        return
                    # Container exists but is stopped - get container ID from first column
                    container_id = columns[0]
                    subprocess.run(f"docker start {container_id}", shell=True, check=True, text=True)
                    print("Successfully started existing Qdrant Docker container")
                    return
            # If we reach here, the container was not found
            print("Container not found in the list")
        else:
            # Container doesn't exist - create and run it
            qdrant_storage_dir = Path(__file__).parent.parent / "qdrant_storage"
            command = (
                f"docker run -d -p 6333:6333 "
                f"--name {container_name} "
                f"-v {qdrant_storage_dir}:/qdrant/storage "
                f"qdrant/qdrant"
            )
            subprocess.run(command, shell=True, check=True, text=True)
            print("Successfully created and started new Qdrant Docker container")
    except subprocess.CalledProcessError as e:
        print(f"Failed to manage Qdrant Docker container: {e}")


def upload_to_qdrant(collection_name, embeddings_and_metadata, vector_size):
    """Upload embeddings and metadata to Qdrant."""

    ensure_qdrant_running()

    # Create client
    qdrant_client = QdrantClient(url="http://localhost:6333")

    # Create collection 
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # Upload files to Qdrant
    operation_info = qdrant_client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=file["id"], 
                       vector=file["vector"], 
                       payload={"text": file["text"]})
            for file in embeddings_and_metadata
        ]
    )