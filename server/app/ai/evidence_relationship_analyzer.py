import json

from app.schemas.investigation import EvidenceRelationship
from app.schemas.incident_evidence import IncidentEvidenceResponse


class EvidenceRelationshipAnalyzer:

    def analyze(
        self,
        evidence: list[IncidentEvidenceResponse],
    ) -> list[EvidenceRelationship]:

        relationships: list[EvidenceRelationship] = []

        for index, source in enumerate(evidence):
            for target in evidence[index + 1 :]:

                relationship = self._match_github_commit_deployment(
                    source,
                    target,
                )

                if relationship:
                    relationships.append(relationship)

        return relationships

    def _match_github_commit_deployment(
        self,
        source: IncidentEvidenceResponse,
        target: IncidentEvidenceResponse,
    ) -> EvidenceRelationship | None:

        if source.source != "github" or target.source != "github":
            return None

        if source.evidence_type == "commit":
            commit = self._parse_content(source.content)

            if target.evidence_type != "deployment":
                return None

            deployment = self._parse_content(target.content)

            return self._build_relationship(
                source=source,
                target=target,
                commit=commit,
                deployment=deployment,
            )

        if source.evidence_type == "deployment":
            deployment = self._parse_content(source.content)

            if target.evidence_type != "commit":
                return None

            commit = self._parse_content(target.content)

            return self._build_relationship(
                source=target,
                target=source,
                commit=commit,
                deployment=deployment,
            )

        return None

    def _build_relationship(
        self,
        source: IncidentEvidenceResponse,
        target: IncidentEvidenceResponse,
        commit: dict,
        deployment: dict,
    ) -> EvidenceRelationship | None:
        print("SOURCE ID:", source.id)
        print("SOURCE TYPE:", source.evidence_type)

        print("TARGET ID:", target.id)
        print("TARGET TYPE:", target.evidence_type)

        print("COMMIT:", commit)
        print("DEPLOYMENT:", deployment)

        commit_sha = commit.get("sha")
        deployment_sha = deployment.get("sha")

        repository = commit.get("repository")
        deployment_repository = deployment.get("repository")
        print("COMMIT SHA:", commit_sha)
        print("DEPLOYMENT SHA:", deployment_sha)

        print("COMMIT REPOSITORY:", repository)
        print("DEPLOYMENT REPOSITORY:", deployment_repository)
        if not commit_sha or not deployment_sha:

            print("❌ SHA missing")
            return None

        if commit_sha != deployment_sha:
            print("❌ SHA DOES NOT MATCH")
            return None

        if repository != deployment_repository:
            print("❤️‍🔥 Repository does not match")
            return None
        print("sha + repository match")
        return EvidenceRelationship(
            source_evidence_id=source.id,
            target_evidence_id=target.id,
            relationship_type="commit_deployed",
            reason=(
                f"GitHub commit {commit_sha} is associated with "
                f"deployment {deployment.get('deployment_id')} because "
                f"both records reference the same SHA in repository "
                f"{repository}."
            ),
        )

    def _parse_content(self, content: str) -> dict:
        print("\n ===== PARSING CONTENT")
        print("CONTENT TYPE: ", type(content))
        print("CONTENT:")
        print(repr(content))
        try:
            data = json.loads(content)
            print("PARSED DATA: ", data)
        except (json.JSONDecodeError, TypeError) as e:
            print("❌ JSON PARSED FAILED", e)
            
            if isinstance(content, str):
                import re
                # Try extracting GitHub commit information from plaintext
                match = re.search(r'https://github\.com/([^/]+/[^/]+)/commit/([a-f0-9]+)', content)
                if match:
                    print("✅ Regex fallback extraction successful")
                    return {
                        "repository": match.group(1),
                        "sha": match.group(2)
                    }

            return {}
        print("PARSE SUCCESSS")
        return data if isinstance(data, dict) else {}
