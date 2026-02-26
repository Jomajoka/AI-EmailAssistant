from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.services.processing_service import process_unprocessed_emails

router = APIRouter()

@router.get("/process")
def process_emails(user_id: int = Depends(get_current_user)):
    ##process_unprocessed_emails(user_id)
    return {"message": "Processing completed"}