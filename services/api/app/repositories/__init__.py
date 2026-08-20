from app.models import (
    Document,
    DocumentChunk,
    Evaluation,
    IngestionJob,
    KnowledgeBase,
    Query,
    QuerySource,
    User,
)
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    pass

class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    pass

class DocumentRepository(BaseRepository[Document]):
    pass

class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    pass

class IngestionJobRepository(BaseRepository[IngestionJob]):
    pass

class QueryRepository(BaseRepository[Query]):
    pass

class QuerySourceRepository(BaseRepository[QuerySource]):
    pass

class EvaluationRepository(BaseRepository[Evaluation]):
    pass

user_repo = UserRepository(User)
kb_repo = KnowledgeBaseRepository(KnowledgeBase)
document_repo = DocumentRepository(Document)
chunk_repo = DocumentChunkRepository(DocumentChunk)
job_repo = IngestionJobRepository(IngestionJob)
query_repo = QueryRepository(Query)
source_repo = QuerySourceRepository(QuerySource)
evaluation_repo = EvaluationRepository(Evaluation)
