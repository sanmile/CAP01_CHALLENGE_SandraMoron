from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import List
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_db = {"users": {}}

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Payload(BaseModel):
    numbers: List[int]

class BinarySearchPayload(BaseModel):
    numbers: List[int]
    target: int

def create_access_token(data: dict):
    """
    Create an access token with the provided data and a specified expiration time.
    
    Args:
        data (dict): A dictionary containing the data to be encoded in the access token.
    
    Returns:
        str: The encoded JWT access token.
    """
        to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@app.post("/login")
async def login(user: User):
    """
    Authenticate a user and generate an access token.
    
    This function takes a `User` object containing the user's username and password, and
    verifies the credentials against the fake database. If the credentials are valid,
    it generates an access token that can be used to authenticate the user in subsequent
    requests.
    
    Args:
        user (User): A `User` object containing the user's username and password.
    
    Returns:
        dict: A dictionary containing the access token and the token type.
    """
        if user.username not in fake_db["users"]:
        raise HTTPException(status_code=401, detail="Credenciales Inválidas")
    if not pwd_context.verify(user.password, fake_db["users"][user.username]):
        raise HTTPException(status_code=401, detail="Credenciales Inválidas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

@app.post("/register", status_code=200)
async def register(user: User):
    """
    Register a new user in the system.
    
    This function takes a `User` object containing the user's username and password, and
    registers the user in the fake database. If the username already exists in the database,
    an `HTTPException` with a 400 status code is raised.
    
    Args:
        user (User): A `User` object containing the user's username and password.
    
    Returns:
        dict: A dictionary containing a success message.
    
    Raises:
        HTTPException: If the username already exists in the database.
    """
        if user.username in fake_db["users"]:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = pwd_context.hash(user.password)
    fake_db["users"][user.username] = hashed_password
    return {"message": "User registered successfully"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user from the provided authentication token.
    
    This function decodes the JWT token provided in the `token` parameter, extracts the
    username from the token's payload, and returns the username. If the token is invalid
    or the username is not present in the payload, an `HTTPException` with a 401 status
    code is raised.
    
    Args:
        token (str): The JWT token to be decoded.
    
    Returns:
        str: The username extracted from the token's payload.
    
    Raises:
        HTTPException: If the token is invalid or the username is not present in the payload.
    """
        try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    return username

@app.post("/bubble-sort")
async def bubble_sort(payload: Payload, token: str = Query(...)):
    """
    Sorts the provided list of numbers using the bubble sort algorithm.
    
    Args:
        payload (Payload): A Payload object containing the list of numbers to be sorted.
        token (str): An authentication token used to verify the current user.
    
    Returns:
        dict: A dictionary containing the sorted list of numbers.
    """
        # Verificar la autenticación
    current_user = await get_current_user(token)
    
    numbers = payload.numbers
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    
    return {"numbers": numbers}

@app.post("/filter-even")
async def filter_even(payload: Payload, token: str = Query(...)):
    """
        Filters the provided list of numbers and returns a list of even numbers.
    
        Args:
            payload (Payload): A Payload object containing the list of numbers to be filtered.
            token (str): An authentication token used to verify the current user.
    
        Returns:
            dict: A dictionary containing the list of even numbers.
        """
        # Verificar la autenticación
    current_user = await get_current_user(token)
    
    numbers = payload.numbers
    even_numbers = [num for num in numbers if num % 2 == 0]
    
    return {"even_numbers": even_numbers}

@app.post("/sum-elements")
async def sum_elements(payload: Payload, token: str = Query(...)):
    """
        Calculates the sum of the provided list of numbers.
        
        Args:
            payload (Payload): A Payload object containing the list of numbers to be summed.
            token (str): An authentication token used to verify the current user.
        
        Returns:
            dict: A dictionary containing the sum of the numbers.
    """
        # Verificar la autenticación
    current_user = await get_current_user(token)
    
    numbers = payload.numbers
    total_sum = sum(numbers)
    
    return {"sum": total_sum}

@app.post("/max-value")
async def max_value(payload: Payload, token: str = Query(...)):
    """
            Calculates the maximum value from the provided list of numbers.
            
            Args:
                payload (Payload): A Payload object containing the list of numbers.
                token (str): An authentication token used to verify the current user.
            
            Returns:
                dict: A dictionary containing the maximum value from the list of numbers.
    """
        # Verificar la autenticación
    current_user = await get_current_user(token)
    
    numbers = payload.numbers
    max_num = max(numbers)
    
    return {"max": max_num}


@app.post("/binary-search")
async def binary_search(payload: BinarySearchPayload, token: str = Query(...)):
    """
        Performs a binary search on the provided list of numbers to find the target value.
    
        Args:
            payload (BinarySearchPayload): A payload object containing the list of numbers and the target value to search for.
            token (str): An authentication token used to verify the current user.
    
        Returns:
            dict: A dictionary containing the result of the binary search. If the target value is found, the dictionary will contain the keys "found" (set to True) and "index" (the index of the target value in the list). If the target value is not found, the dictionary will contain the keys "found" (set to False) and "index" (set to -1).
    """
        # Verificar la autenticación
    current_user = await get_current_user(token)
    
    numbers = payload.numbers
    target = payload.target
    
    left, right = 0, len(numbers) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == target:
            return {"found": True, "index": mid}
        elif numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return {"found": False, "index": -1}
