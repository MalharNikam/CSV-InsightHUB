from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils.auth_token import get_current_user
from app.models.user import User
import pandas as pd
import os

router = APIRouter()

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    contents = await file.read()

    # Create per-user folder
    user_folder = f"uploads/{current_user.email.replace('@', '_')}"
    os.makedirs(user_folder, exist_ok=True)

    # Use original filename, avoid overwriting
    base_name = os.path.splitext(file.filename)[0]
    suffix = 1
    final_name = file.filename
    while os.path.exists(os.path.join(user_folder, final_name)):
        final_name = f"{base_name}_{suffix}.csv"
        suffix += 1

    file_path = os.path.join(user_folder, final_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Optional insight generation
    df = pd.read_csv(file_path)
    df.columns = [col.strip().lower() for col in df.columns]

    insights = {
        "total_rows": len(df),
        "columns": list(df.columns),
        "preview": df.head().to_dict(orient="records"),
        "uploaded_by": current_user.email
    }

    if "department" in df.columns:
        insights["employee_count_by_department"] = df["department"].value_counts().to_dict()

    if "salary" in df.columns:
        insights["average_salary"] = round(df["salary"].mean(), 2)

    if "attrition" in df.columns:
        attr_values = df["attrition"].astype(str).str.lower().value_counts(normalize=True)
        insights["attrition_rate_percent"] = round(attr_values.get("yes", 0.0) * 100, 2)

    return {
        "message": f"File `{final_name}` uploaded and processed.",
        "insights": insights
    }

@router.get("/files")
def list_uploaded_files(current_user: User = Depends(get_current_user)):
    user_folder = f"uploads/{current_user.email.replace('@', '_')}"
    if not os.path.exists(user_folder):
        return {"files": []}
    
    files = sorted([
        f for f in os.listdir(user_folder)
        if os.path.isfile(os.path.join(user_folder, f)) and f.endswith(".csv")
    ])[-5:]  # limit to last 5 alphabetically

    return {"files": files}