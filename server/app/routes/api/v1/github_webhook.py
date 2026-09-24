import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.integration import IntegrationProvider
from app.repository.integration_repository import IntegrationRepository

router = APIRouter()


def verify_github_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    if not signature:
        return False

    if not signature.startswith("sha256="):
        return False

    expected_signature = (
        "sha256="
        + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(expected_signature, signature)


@router.post("/{tenant_id}")
async def github_webhook(
    tenant_id: int,
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    repository = IntegrationRepository(db)
    integration = await repository.get_by_provider_and_tenant(
        provider=IntegrationProvider.GITHUB, tenant_id=tenant_id
    )

    if integration is None:
        raise HTTPException(status_code=404, detail="Github integration not found")

    if not integration.is_active:
        raise HTTPException(
            status_code=400,
            detail="GitHub integration is inactive",
        )
    if not integration.webhook_secret:
        raise HTTPException(
            status_code=400, detail="github webhook secret is not configured"
        )
    is_valid = verify_github_signature(
        payload=payload,
        signature=x_hub_signature_256,
        secret=integration.webhook_secret,
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid github webhook signature")

    import json
    from app.models.incident import Incident, IncidentSeverity, IncidentStatus
    from app.repository.incident import IncidentRepository
    from app.repository.user import UserRepository
    
    event = x_github_event or "unknown"
    
    if event == "issues":
        data = json.loads(payload)
        if data.get("action") == "opened":
            issue = data.get("issue", {})
            title = issue.get("title", "GitHub Issue")
            body = issue.get("body", "No description provided.")
            html_url = issue.get("html_url", "")
            
            # Find a user to assign as reporter
            user_repo = UserRepository(db)
            users = await user_repo.get_all(tenant_id)
            if not users:
                raise HTTPException(status_code=500, detail="No users found for tenant")
            reporter = users[0]
            
            incident_repo = IncidentRepository(db)
            new_incident = Incident(
                title=f"[GitHub] {title}",
                description=f"{body}\n\nIssue URL: {html_url}",
                severity=IncidentSeverity.MEDIUM,
                status=IncidentStatus.OPEN,
                reported_by=reporter.id,
                tenant_id=tenant_id
            )
            await incident_repo.create(new_incident)
            await db.commit()
            
    return {"status": "accepted", "event": event}
