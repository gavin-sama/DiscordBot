import requests

def get_genre(genre_name: str) -> dict:
    url = f"http://localhost:8000/genre/{genre_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"detail": "Genre not found"}
    

if __name__ == "__main__":
    genre_name = "Rock"
    genre = get_genre(genre_name)

    # display raw json like response
    print(genre)

    #Display name and description of the genre
    print(f'Name: {genre['name']}')
    print(f"Description: {genre['description']}")