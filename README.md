# ApplePye

ApplePye is a free and open-source scrobbler for Apple Music on Windows, written in Python. This tool allows you to scrobble your listened tracks to Last.fm automatically.

## Setup

### Prerequisites

Make sure you have Python installed on your system. If not, you can download it from python.org.

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/code-irisnk/ApplePye.git
```

Navigate to the project directory:

```bash
cd ApplePye
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

[Create a Last.fm API account](https://www.last.fm/api/account/create) and obtain your API key, API secret, username, and password hash.

Edit the file named auth.json keeping the following structure:

```json
{
    "api_key": "your_lastfm_api_key",
    "api_secret": "your_lastfm_api_secret",
    "username": "your_lastfm_username",
    "password_hash": "your_lastfm_password_hash"
}
```

Replace the placeholders with your actual Last.fm API credentials.
To get the hashed equivalent of your password, run

```bash
python hasher.py
```

It should look something like this: `465aedcc10d6e4d5dea60f8ba422df82`

## Usage

Run the scrobbler using the following command:

```bash
python main.py
```

The scrobbler will continuously monitor Apple Music on your Windows system and automatically scrobble tracks to Last.fm when Apple Music is detected.

## Notes

Ensure that [Apple Music (Preview) is installed on your system using Microsoft Store](https://apps.microsoft.com/detail/9PFHDD62MXS1) before starting the scrobbler.
The scrobbler checks if at least 25% of a song has been played before scrobbling.

## Contributing

If you'd like to contribute to ApplePye, please follow these steps:

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Make your changes and commit them.
- Submit a pull request.
