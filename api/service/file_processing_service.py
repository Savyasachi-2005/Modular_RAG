import io
import markdown
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup
from docx import Document
from fastapi import UploadFile, HTTPException, status
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

class FileProcessingService:
    """A service dedicated to extracting text content from various file formats."""

    async def extract_text_from_file(self, file: UploadFile) -> Dict[str, str]:
        """
        Extracts text content from an uploaded file based on its extension.
        Returns a dictionary containing the title and content.
        """
        contents = await file.read()
        filename = file.filename
        file_ext = Path(filename).suffix.lower()

        try:
            if file_ext == ".pdf":
                text = self._extract_from_pdf(contents)
            elif file_ext == ".docx":
                text = self._extract_from_docx(contents)
            elif file_ext == ".html":
                text = self._extract_from_html(contents)
            elif file_ext == ".md":
                text = self._extract_from_md(contents)
            elif file_ext == ".txt":
                text = self._extract_from_txt(contents)
            else:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported file type: {file_ext}",
                )
            
            # Use the filename (without extension) as the default title
            title = Path(filename).stem
            
            return {"title": title, "content": text}

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process file: {filename}. Error: {str(e)}",
            )

    def _extract_from_pdf(self, contents: bytes) -> str:
        """Extracts text from PDF file contents."""
        with io.BytesIO(contents) as pdf_file:
            reader = PdfReader(pdf_file)
            text = "".join(page.extract_text() for page in reader.pages)
        return text

    def _extract_from_docx(self, contents: bytes) -> str:
        """Extracts text from DOCX file contents."""
        with io.BytesIO(contents) as docx_file:
            doc = Document(docx_file)
            text = "\n".join(para.text for para in doc.paragraphs)
        return text

    def _extract_from_html(self, contents: bytes) -> str:
        """Extracts text from HTML file contents."""
        soup = BeautifulSoup(contents, "html.parser")
        return soup.get_text(separator="\n", strip=True)

    def _extract_from_md(self, contents: bytes) -> str:
        """Extracts text from Markdown file contents by converting to HTML first."""
        html = markdown.markdown(contents.decode("utf-8"))
        return self._extract_from_html(html.encode("utf-8"))

    def _extract_from_txt(self, contents: bytes) -> str:
        """Extracts text from a plain text file."""
        return contents.decode("utf-8")


# Singleton instance
file_processing_service = FileProcessingService()