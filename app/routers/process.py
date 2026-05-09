from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user, verify_csrf_token
from app.services.processing_service import process_unprocessed_emails

router = APIRouter()

@router.post("/process")
def process_emails(
    user_id: int = Depends(get_current_user),
    _csrf: None = Depends(verify_csrf_token)
):
    process_unprocessed_emails(user_id)
    return {"message": "Processing completed"}
