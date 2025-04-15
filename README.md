# Cultivation Journal

A desktop application for tracking your character's journey in cultivation-themed role-playing games.

## Overview

Cultivation Journal is a tkinter-based application designed to help you document your character's progress, techniques, inventory, and goals in cultivation-themed RPGs. Whether you're playing a structured game or engaging in freeform cultivation roleplay, this tool provides an organized interface to track your character's development.

## Features

- **Character Information**: Track your character's name, background, and current cultivation stage
- **Cultivation Details**: Record your cultivation path, elemental affinities, breakthroughs, active and passive techniques
- **Inventory Management**: Keep track of spirit stones, artifacts, and consumable items
- **Quest Tracking**: Document your goals, unfinished quests, and gathered rumors
- **Session Notes**: Keep a detailed log of your adventures
- **Multiple Themes**: Choose from various cultivation-themed visual styles:
  - Mortal Realm (default - neutral gray/white)
  - Jade Forest (soothing green/white)
  - Crimson Path (dark with red accents)
  - Azure Sky (light blue with deep blue text)
  - Scholarly Scroll (parchment beige with brown text)
- **Text Formatting**: Basic formatting options for your notes
- **File Management**: Save and load multiple character journals with custom filenames
- **AI Integration**: Includes a customizable AI prompt to help share your character's journey with AI assistants

## Usage

1. Run the application: `python cultivation_journal.py`
2. Fill in your character details across the different tabs
3. Use keyboard shortcuts for common actions:
   - **Ctrl+S**: Save your journal
   - **Ctrl+O**: Open an existing journal
   - **Ctrl+N**: Create a new journal

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/labrosh/Journal.git
   ```
2. Navigate to the directory:
   ```
   cd Journal
   ```
3. Run the application:
   ```
   python cultivation_journal.py
   ```

## Journal Structure

The journal is organized into several tabs:

- **Cultivation**: Details about your cultivation practice
- **Background**: Your character's history and reputation
- **Inventory**: Items and resources your character possesses
- **Quests & Goals**: Current objectives and rumors
- **Session Journal**: Notes from your gaming sessions

## Using with AI Assistants (ChatGPT)

Cultivation Journal includes a special feature that helps you use your character data with AI assistants like ChatGPT for immersive roleplay experiences:

### Setting Up Your AI Prompt

1. In the application, go to **Settings > Edit AI Prompt**
2. Customize the prompt to fit your storytelling preferences
3. Save your journal with Ctrl+S

### Using Your Journal with ChatGPT

1. Save your journal using File > Save or Ctrl+S
2. Open the saved JSON file with a text editor or upload it directly to ChatGPT
3. Start a new chat with ChatGPT
4. If uploading the file directly:
   - Drag and drop your .json file into the ChatGPT chat window
   - Add the message: "This is my character's journal for a cultivation-themed game. Please read the AI Prompt field in this JSON and follow those guidelines."
5. If copying the contents:
   - Copy the entire contents of your .json file
   - Paste the following prompt and replace [PASTE JSON HERE] with your copied journal:
   ```
   I want to roleplay a cultivation-themed game. Here's my character's journal in JSON format:
   
   [PASTE JSON HERE]
   
   Please read the "AI Prompt" field in this JSON and follow those guidelines. 
   Start by introducing yourself as my cultivation guide and summarize what you know about my character 
   from the journal. Then help me continue my cultivation journey.
   ```
6. ChatGPT will use your character information to create an immersive experience following your custom prompt

### Tips for Better AI Roleplaying

- Fill out the Background and Cultivation tabs thoroughly for more context
- Keep goals specific in the Quests & Goals section
- Update your journal after each ChatGPT session with new developments
- Customize the AI prompt to guide the AI's tone and interaction style

## License

[Your License Here]

## Acknowledgments

- Created for cultivation roleplay enthusiasts
- Inspired by xianxia and cultivation novels
