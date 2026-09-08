from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.agent_model import Agent


class AgentRepository:

    @staticmethod
    def create(db: Session, agent: Agent) -> Agent:
        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    @staticmethod
    def get_by_id(
        db: Session,
        agent_id: UUID,
    ) -> Agent | None:

        return (
            db.query(Agent)
            .filter(Agent.id == agent_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session) -> list[Agent]:
        return db.query(Agent).all()

    @staticmethod
    def delete(
        db: Session,
        agent: Agent,
    ) -> None:

        db.delete(agent)
        db.commit()

    @staticmethod
    def save(
        db: Session,
        agent: Agent,
    ) -> Agent:

        db.commit()
        db.refresh(agent)

        return agent