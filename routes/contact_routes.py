from fastapi import APIRouter, Depends, HTTPException
from schemas import Contact
from auth import get_current_user
from database import get_db_connection

router = APIRouter()

@router.get("/contacts/")
def get_contacts(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE owner = %s", (user["username"],))
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return contacts

@router.post("/contacts/")
def create_contact(contact: Contact, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, email, phone, owner) VALUES (%s, %s, %s, %s) RETURNING *",
                (contact.name, contact.email, contact.phone, user["username"]))
    new_contact = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_contact

@router.put("/contacts/{id}")
def update_contact(id: int, contact: Contact, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE contacts SET name=%s, email=%s, phone=%s WHERE id=%s AND owner=%s RETURNING *",
                (contact.name, contact.email, contact.phone, id, user["username"]))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(404, "Contact not found")
    return updated

@router.delete("/contacts/{id}")
def delete_contact(id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id=%s AND owner=%s RETURNING id", (id, user["username"]))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(404, "Contact not found")
    return {"message": "Deleted"}
