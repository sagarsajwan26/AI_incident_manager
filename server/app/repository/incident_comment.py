from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_comment import IncidentComment


class IncidentCommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, incident_id: int, tenant_id: int, author_id: int, content: str
    ) -> IncidentComment:
        comment = IncidentComment(
            incident_id=incident_id,
            tenant_id=tenant_id,
            author_id=author_id,
            content=content,
        )

        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def get_by_incident(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> list[IncidentComment]:
        result = await self.db.execute(
            select(IncidentComment)
            .where(
                IncidentComment.incident_id == incident_id,
                IncidentComment.tenant_id == tenant_id,
            )
            .order_by(IncidentComment.created_at.asc())
        )
        return list(result.scalars().all())
