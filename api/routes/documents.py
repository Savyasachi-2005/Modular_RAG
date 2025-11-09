from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import Dict, Any
from service.auth_service import get_current_user
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

# Directory where uploaded files are stored
UPLOAD_DIR = "uploads"

@router.get(
    "/view/{filename}",
    summary="View/Download a document"
)
async def view_document(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Serve a document file for viewing or downloading.
    
    This endpoint returns the actual file content so it can be:
    - Viewed in browser (PDFs, images, text files)
    - Downloaded by the user
    - Embedded in iframes
    
    Protected endpoint - requires authentication.
    """
    try:
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Construct file path
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{filename}' not found"
            )
        
        # Check if user has access to this file
        # TODO: Add user-specific file access control
        username = current_user.get('username')
        logger.info(f"User '{username}' accessing file: {filename}")
        
        # Determine media type based on file extension
        ext = filename.split('.')[-1].lower()
        media_types = {
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'html': 'text/html',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
        }
        
        media_type = media_types.get(ext, 'application/octet-stream')
        
        # Return file
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving document '{filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document"
        )


@router.get(
    "/download/{filename}",
    summary="Download a document"
)
async def download_document(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a document file.
    
    Forces download instead of inline viewing.
    Protected endpoint - requires authentication.
    """
    try:
        # Sanitize filename
        filename = os.path.basename(filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{filename}' not found"
            )
        
        username = current_user.get('username')
        logger.info(f"User '{username}' downloading file: {filename}")
        
        # Force download with Content-Disposition header
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document '{filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading document"
        )


@router.get("/health", summary="Health Check")
async def documents_health_check():
    """
    Health check endpoint for documents service.
    """
    return {
        "status": "healthy",
        "service": "documents",
        "message": "Documents service is operational"
    }
