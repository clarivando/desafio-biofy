from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO



def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        file_like = BytesIO(file_bytes)  # transforma bytes em arquivo PDF
        pdf = PdfReader(file_like)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Erro ao processar PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extrai o texto de um arquivo DOCX (bytes).
    """
    try:
        doc = Document(BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Erro ao processar DOCX: {e}")


def extract_text(file_bytes: bytes, extension: str) -> str:
    """
    Detecta o tipo de arquivo e extrai o texto.
    """
    if extension == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif extension == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Extensão de arquivo não suportada: {extension}")
