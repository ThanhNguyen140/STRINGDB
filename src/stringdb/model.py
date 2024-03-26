from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class Protein(Base):
    __tablename__ = "protein"
    id: Mapped[int] = mapped_column(primary_key=True)
    string_protein_id: Mapped[str]
    uniprot_AC: Mapped[str]

    def __repr__(self) -> str:
        return f"Protein(id={self.id!r}, string_protein_id={self.string_protein_id!r},uniprot_AC ={self.uniprot_AC})"


class Interaction(Base):
    __tablename__ = "interaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    protein1: Mapped[str] = mapped_column(ForeignKey("protein.id"))
    protein2: Mapped[str] = mapped_column(ForeignKey("protein.id"))
    neighborhood: Mapped[int]
    cooccurence: Mapped[int]
    homology: Mapped[int]
    coexpression: Mapped[int]
    combined_score: Mapped[int]
    interact1: Mapped["Protein"] = relationship(foreign_keys=[protein1])
    interact2: Mapped["Protein"] = relationship(foreign_keys=[protein2])

    def __repr__(self) -> str:
        return f"Interaction(id={self.id!r},\
        neighborhood={self.neighborhood},\
        cooccurence={self.cooccurence},\
        homology={self.homology},\
        coexpression={self.coexpression},\
        combined_score={self.combined_score})"
