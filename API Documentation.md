## Play My Emotions API Documentation

### Overview

The Play My Emotions API provides song recommendations based on user emotions. The primary endpoint is `/recommend`, which takes in a user's emotional text and returns a list of recommended songs.

### Base URL

```
http://127.0.0.1:8000
```

### Endpoints

#### 1. POST /recommend

**Description**:  
Provides song recommendations based on the user's emotional input.

**Request**:

- **Method**: POST
- **URL**: `/recommend`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:

```json
{
  "emotion_text": "string"
}
```

**Parameters**:

- `emotion_text` (required): A string containing the user's emotional state or feelings.

**Response**:

- **Status Code**: 200 OK
- **Body**:

```json
{
  "emotions": "string",
  "songs": [
    {
      "name": "string",
      "embed_url": "string"
    },
    ...
  ]
}
```

**Response Fields**:

- `emotions`: A string representing the interpreted emotions based on the user's input.
- `songs`: An array of song objects. Each object contains:
  - `name`: The name of the recommended song.
  - `embed_url`: The URL for embedding the song (e.g., a Spotify or YouTube embed link).

**Example Request**:

```json
{
  "emotion_text": "I am feeling joyful"
}
```

**Example Response**:

```json
{
  "emotions": "joyful, happy, elated",
  "songs": [
    {
      "name": "Song Name 1",
      "embed_url": "https://embed-link-1.com"
    },
    {
      "name": "Song Name 2",
      "embed_url": "https://embed-link-2.com"
    }
  ]
}