from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import psycopg2
import json

app = FastAPI()

DB_HOST = 'localhost'
DB_NAME = 'zap_results'
DB_USER = 'zap_user'
DB_PASS = 'your_password'


class ResponseMessage(BaseModel):
    success: bool
    message: str
    data: str



def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn


# Pydantic model for the target data
class Target(BaseModel):
    targets: List[str]


@app.post("/api/targets")
async def add_target(request: Request):
    data = await request.form()
    targets_raw = data.get('targets')
    print(targets_raw)
    return ResponseMessage(success=True, message="Targets saved to database", data=targets_raw)
    if not targets_raw:
        raise HTTPException(status_code=400, detail="Targets not provided")

    targets_list = json.loads(targets_raw)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for target in targets_list:
            cur.execute("""
                INSERT INTO targets (value)
                VALUES (%s)
            """, (target,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save targets to database: {str(e)}")
    finally:
        cur.close()
        conn.close()

    return {"message": "Targets saved to database"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9001)
