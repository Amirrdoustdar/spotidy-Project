# Spotidy Project

Spotidy Project is a Python tool that detects and removes duplicate tracks from your Spotify playlists. It leverages the Spotify API (via the spotipy library) to generate CSV reports and send email notifications, keeping your playlists clean and organized.

## Features

- **Duplicate Detection:** Identify duplicate tracks based on track name and primary artist.
- **CSV Reporting:** Generate a detailed CSV report of duplicates.
- **Email Notifications:** Optionally send the duplicate report directly to your email.
- **Playlist Cleanup:** Remove extra duplicate tracks while preserving one instance.

## Prerequisites

- Python 3.7 or higher.
- A Spotify Developer Account (to obtain API credentials).
- Valid email account credentials (for sending emails).

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Amirrdoustdar/spotidy-Project.git
    cd spotidy-Project
    ```

2. **Create a Virtual Environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables:**
    - Rename the file `.env.example` to `.env`.
    - Fill in your Spotify and email credentials in the `.env` file.

## Usage

Run the script:
```bash
python your_script.py
```

## Contributing to Spotidy Project

Thank you for your interest in contributing to the Spotidy Project!

## How to Contribute

### Reporting Bugs
- Open an issue on [GitHub](https://github.com/Amirrdoustdar/spotidy-Project/issues) with a detailed description of the bug.
- Include steps to reproduce the issue and any relevant logs or screenshots.

### Suggesting Enhancements
- Open an issue describing your suggestion.
- Provide as much detail as possible on how the feature could work.

### Submitting Pull Requests
1. Fork the repository.
2. Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them with clear commit messages.
4. Push your branch:
    ```bash
    git push origin feature/your-feature-name
    ```
5. Open a Pull Request against the main repository.

## Code Style
- Follow the existing code style and conventions.
- Write clear, concise commit messages.
- Ensure that your code is well-commented.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions
If you have any questions, feel free to open an issue on [GitHub](https://github.com/Amirrdoustdar/spotidy-Project) or contact [Amirrdoustdar](https://github.com/Amirrdoustdar).

