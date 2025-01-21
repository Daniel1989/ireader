import json
import os
import uuid
import logging
import lancedb
from openai import AzureOpenAI
from dotenv import load_dotenv

VECTOR_NAMESPACE = 'urlV1'

# Load environment variables
load_dotenv()

# Set up logging directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging configuration
log_file = os.path.join(LOG_DIR, 'embedding.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(module)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

uri = "./iread_data"
if not os.access(os.path.dirname(uri), os.W_OK):
    print(f"No write permission for database location: {uri}")
else:
    print("有写权限")

db = lancedb.connect(uri)

# Azure OpenAI Configuration from environment variables
azure_client = AzureOpenAI(
    api_key=os.environ.get("AZURE_API_KEY"),
    api_version=os.environ.get("AZURE_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_ENDPOINT")
)

logger.info(f"Azure client configured with endpoint: {os.environ.get('AZURE_ENDPOINT')}")

def create_embedding(text):
    try:
        logger.info(f"Starting embedding creation for text: {text[:100]}...")  # Log first 100 chars
        
        response = azure_client.embeddings.create(
            input=str(text),
            model="text-embedding-ada-002",
            timeout=200
        )
        
        # Log successful response details
        logger.info(f"Embedding created successfully. Response model: {response.model}")
        logger.info(f"Number of embeddings created: {len(response.data)}")
        logger.info(f"Embedding dimensions: {len(response.data[0].embedding)}")
        logger.info(f"Usage tokens: {response.usage.total_tokens}")
        
        return response
    except Exception as e:
        logger.error(f"Azure embedding creation failed with error: {str(e)}")
        logger.error(f"Failed text: {text[:100]}...")  # Log the text that failed
        logger.exception("Full traceback:")  # This logs the full stack trace
        raise e

def check_table_exist(name):
    logger.info(f"11 Attempting to update or create table: {name}")
    tables = db.table_names()
    logger.info(f"22 Attempting to update or create table: {name}")
    print(f"tables name: {tables}")
    return name in tables

def updateOrCreateTable(data):
    name = VECTOR_NAMESPACE
    try:
        logger.info(f"Attempting to update or create table: {name}")
        if check_table_exist(name):
            logger.info(f"Table {name} exists, opening and adding data")
            tbl = db.open_table(name)
            tbl.add(data)
        else:
            logger.info(f"Table {name} does not exist, creating new table")
            db.create_table(name, data=data)
            tbl = db.open_table(name)
            tbl.add(data)
        logger.info(f"Successfully updated table {name}")
    except Exception as e:
        logger.error(f"Failed to update or create table {name}: {str(e)}")
        logger.exception("Full traceback:")
        raise e
        # tbl.create_index(num_sub_vectors=1)
    return True

def storeVectorResult(vectorData, url):
    path = 'vector_data'
    os.makedirs(path, exist_ok=True)
    digest = uuid.uuid5(uuid.NAMESPACE_DNS, url)
    path = os.path.join(path, digest.hex + '.json')
    with open(path, 'w') as f:
        f.write(json.dumps(vectorData))

def distanceToSimilarity(distance: None | float):
    if distance is None or not isinstance(distance, float):
        return 0.0
    elif distance >= 1.0:
        return 1.0
    elif distance <= 0.0:
        return 0.0
    else:
        return 1.0 - distance

def vectorSearch(query_vector):
    try:
        name = VECTOR_NAMESPACE
        logger.info(f"Starting vector search in table: {name}")
        logger.info(f"Query vector dimensions: {len(query_vector)}")
        
        tbl = db.open_table(name)
        logger.info(f"Successfully opened table: {name}")
        
        result = tbl.search(query_vector).metric("cosine").limit(4).to_pandas()
        logger.info(f"Search completed. Found {len(result)} results")
        
        context_texts = []
        source_documents = []
        score = []
        references = []  # New list for storing references
        
        logger.info("Processing search results...")
        MIN_DISTANCE = 0.15
        for index, row in result.iterrows():
            distance = row["_distance"]
            logger.info(f"Result {index + 1}: Distance = {distance}")
            
            if distance >= MIN_DISTANCE:
                similarity = distanceToSimilarity(distance)
                score.append(similarity)
                context_texts.append(row["text"])
                
                # Convert row to dict and ensure all numpy arrays are converted to lists
                doc_dict = row.to_dict()
                for key, value in doc_dict.items():
                    if hasattr(value, 'tolist'):  # Check if it's a numpy array
                        doc_dict[key] = value.tolist()
                source_documents.append(doc_dict)
                
                # Add reference information
                references.append({
                    "url": row["url"],
                    "title": row["title"],
                    "similarity": similarity
                })
                
                logger.info(f"Added result {index + 1} with similarity score: {similarity}")
                logger.debug(f"Text snippet: {row['text'][:100]}...")
            else:
                logger.info(f"Skipped result {index + 1}: Distance {distance} below threshold {MIN_DISTANCE}")
        
        logger.info(f"Vector search complete. Found {len(context_texts)} relevant matches")
        logger.info(f"Similarity scores: {score}")
        
        return context_texts, score, source_documents, references
    except Exception as e:
        logger.error("Error during vector search")
        logger.error(f"Error details: {str(e)}")
        logger.exception("Full traceback:")
        raise e
