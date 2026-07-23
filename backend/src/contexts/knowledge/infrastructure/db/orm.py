# adapters/orm.py

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    func,
)

# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry, relationship

from src.contexts.knowledge.application.ports.background_work import (
    DurableBackgroundJobState,
)
from src.contexts.knowledge.domain.models import (
    CgptPermissionsToFile,
    ChunkingStrategy,
    ParentOrChild,
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFile,
    UploadedTextLikeFileProcessingStatus,
)

# _id: str
#     _name: str
#     _file_type: FileType

#     # created_at: datetime.datetime
#     # user: UserId,
#     _raw_file_is_stored: bool
#     _transformed_text: str | None
#     _corresponding_chunks: list[TextFileChunk]
#     _hash_of_raw_file: str | None

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

uploaded_text_like_file = Table(
    "uploaded_text_like_file",
    metadata,
    Column("_id", UUID, primary_key=True),
    Column("_name", String, nullable=False),
    Column(
        "_file_type",
        Enum(
            TextFileTypeEnum,
            name="TextFileTypeEnum",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("_transformed_text", String, nullable=True),
    Column("_hash_of_raw_file", String, nullable=False),
    Column(
        "_status",
        Enum(
            UploadedTextLikeFileProcessingStatus,
            name="UploadedTextLikeFileProcessingStatus",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
)

cgpt_permissions_to_files = Table(
    "cgpt_permissions_to_files",
    metadata,
    Column("_id", String, primary_key=True),
    Column("file_id", UUID, ForeignKey("uploaded_text_like_file._id"), nullable=False),
    Column("cgpt_id", String, nullable=False),
)

document_deletion_jobs = Table(
    "document_deletion_jobs",
    metadata,
    Column("file_id", UUID, primary_key=True),
    Column(
        "state",
        Enum(
            DurableBackgroundJobState,
            name="DocumentDeletionJobState",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("attempt_count", Integer, nullable=False, default=0),
    Column("next_attempt_at", DateTime(timezone=True), nullable=False),
    Column("lease_token", UUID, nullable=True),
    Column("lease_expires_at", DateTime(timezone=True), nullable=True),
    Column("last_failure_category", String, nullable=True),
    Column("last_failure_at", DateTime(timezone=True), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

document_processing_jobs = Table(
    "document_processing_jobs",
    metadata,
    Column("file_id", UUID, primary_key=True),
    Column(
        "state",
        Enum(
            DurableBackgroundJobState,
            name="DocumentProcessingJobState",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("attempt_count", Integer, nullable=False, default=0),
    Column("next_attempt_at", DateTime(timezone=True), nullable=False),
    Column("lease_token", UUID, nullable=True),
    Column("lease_expires_at", DateTime(timezone=True), nullable=True),
    Column("last_failure_category", String, nullable=True),
    Column("last_failure_at", DateTime(timezone=True), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

Index(
    "ix_document_deletion_jobs_claimable",
    document_deletion_jobs.c.state,
    document_deletion_jobs.c.next_attempt_at,
    document_deletion_jobs.c.lease_expires_at,
    document_deletion_jobs.c.created_at,
)
Index(
    "ix_document_processing_jobs_claimable",
    document_processing_jobs.c.state,
    document_processing_jobs.c.next_attempt_at,
    document_processing_jobs.c.lease_expires_at,
    document_processing_jobs.c.created_at,
)

# _id: str
# _corresponding_text_file_id: str
# _text_content_of_chunk: str
# _chunking_stragegy: str
# _hierarchy_of_chunk: ParentOrChild
# _parent_id_if_child: str | None

text_chunks_of_files = Table(
    "text_chunks_of_files",
    metadata,
    Column("_id", UUID, nullable=False, primary_key=True),
    Column(
        "_corresponding_text_file_id",
        UUID,
        ForeignKey("uploaded_text_like_file._id"),
        nullable=False,
    ),
    Column("_text_content_of_chunk", String, nullable=False),
    Column(
        "_chunking_strategy",
        Enum(
            ChunkingStrategy,
            name="ChunkingStrategy",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column(
        "_hierarchy_level_of_chunk",
        Enum(
            ParentOrChild,
            name="ParentOrChild",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("_parent_id_if_child", UUID, nullable=True),
)


# Index("ix_messages_conv_created_at", messages.c.conversation_id, messages.c.created_at)
## Later: alembic revision -m "add composite index" → write op.create_index('ix_messages_conv_created_at', 'messages', ['conversation_id', 'created_at']) → alembic upgrade head.
def start_mappers() -> None:
    mapper_registry.map_imperatively(
        CgptPermissionsToFile,
        cgpt_permissions_to_files,
    )
    mapper_registry.map_imperatively(
        TextFileChunk,
        text_chunks_of_files,
    )
    mapper_registry.map_imperatively(
        UploadedTextLikeFile,
        uploaded_text_like_file,
        properties={
            # one-to-many; SQLAlchemy instruments `Conversation.messages`
            "_corresponding_chunks": relationship(
                TextFileChunk,
                primaryjoin=text_chunks_of_files.c._corresponding_text_file_id
                == uploaded_text_like_file.c._id,
                backref=None,
                cascade="all, delete-orphan",
            )
        },
    )
