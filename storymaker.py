import json
import random
import datetime
import os
import glob
import subprocess  # so we can choose chrome
import pygame

# Initialize Pygame
pygame.init()

# Screen size
screen_width, screen_height = 768, 1024
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
gothic_font = pygame.font.Font("fonts/CaslonAntique.ttf", 26)
title_font = pygame.font.Font("fonts/Almendra-Regular.ttf", 36)


# Load data sets
def load_data(file_name):
    with open(f"data/{file_name}") as file:
        return json.load(file)


# Load background image
background_image = pygame.image.load("bg/bg.png")

# Theme and category selection defaults
current_theme="Introduce"
data = load_data("introduce.json")  # Initial data load
current_categories = ["DescriptiveWords", "Nouns", "Actions"]


# Function to generate random phrases with a default theme of "Introduce"
def generate_phrases():
    """
    Generate random phrases based on a specified theme.

    Args:
        current_theme (str, optional): The theme for generating phrases. Defaults to "Introduce."

    Returns:
        list: A list of generated phrases, each represented as a tuple containing the phrase text
        and its initial position on the screen.

    The function generates random phrases by selecting words from categories associated with the
    specified theme. It constructs phrases by randomly selecting words from each category and
    joining them together. The resulting phrases are stored as tuples with their initial screen
    positions.

    Example:
        To generate phrases with the default theme:
        >>> phrases = generate_phrases()

        To generate phrases with a specific theme:
        >>> phrases = generate_phrases("Medieval")
    """
    phrases = []
    theme_key = current_theme.capitalize()
    for _ in range(5):
        phrase = " ".join(
            random.choice(data[theme_key][category]) for category in current_categories
        )
        phrases.append(
            (phrase, (screen_width - 500, _ * 100 + 215))
        )  # Store phrase with its initial position
    return phrases


# Updated generate_icons function with a default theme of "Medieval"
def generate_icons(num_icons=5):
    """
    Generate a random selection of icons associated with a specified theme.

    Args:
        theme (str, optional): The theme for which icons should be generated. Defaults 
        to "Medieval." 
        num_icons (int, optional): The number of icons to generate. Defaults to 5.

    Returns:
        list: A list of tuples, each containing a loaded image object and the file path 
        of the corresponding icon.

    The function generates a random selection of icons based on the specified theme. It
    constructs the file path to search for icons in the theme's directory. If the theme
    directory does not exist,    it falls back to the "Medieval" theme. It then selects
    a random subset of available icons and loads  them as image objects.

    Example:
        To generate a list of 5 icons with the default "Medieval" theme:
        >>> icons = generate_icons()

        To generate a list of icons with a specific theme and a custom number of icons:
        >>> icons = generate_icons("Fantasy", num_icons=10)
    """
    global current_theme
    icon_path = f"icons/{current_theme}/*.png"

    if not os.path.exists(f"icons/{current_theme}"):
        icon_path = "icons/Medieval/*.png"

    icon_files = glob.glob(icon_path)
    num_icons = min(num_icons, len(icon_files))
    if num_icons > 0:
        icon_files = random.sample(icon_files, num_icons)

    icons_with_paths = [
        (pygame.image.load(icon_file), icon_file) for icon_file in icon_files
    ]
    return icons_with_paths


# You can now call generate_phrases() and generate_icons() without passing current_theme.
random_icons = generate_icons()

# Labels for the boxes
arrow = "\u00BB"  # Unicode string for the arrow character
box_labels = [
    f"Plot Hook {arrow}",
    f"Barrier {arrow}",
    f"Challenge {arrow}",
    f"Showdown {arrow}",
    f"Reward {arrow}",
]

# Drag and drop variables
dragging = False
dragged_phrase_index = None
phrases = generate_phrases()

# Button and dropdown variables
save_button = pygame.Rect(50, 700, 100, 30)
generate_button = pygame.Rect(160, 700, 100, 30)

# Dropdown options with capitalized names
dropdown_options = [
    f.replace(".json", "") for f in os.listdir("data") if f.endswith(".json")
]


# DataSetButton class
class DataSetButton:
    """
    A class representing a button used for selecting data sets.

    Args:
        x (int): The x-coordinate of the button's top-left corner.
        y (int): The y-coordinate of the button's top-left corner.
        width (int): The width of the button.
        height (int): The height of the button.
        text (str): The text displayed on the button.

    Attributes:
        rect (pygame.Rect): A rectangular area defining the button's position and size.
        text (str): The text displayed on the button.
        selected (bool): A flag indicating whether the button is currently selected.

    Methods:
        draw(screen): Draw the button on the specified Pygame screen.
        toggle_select(): Toggle the selection state of the button.

    The `DataSetButton` class represents a clickable button with a rectangular shape, text,
    and a selection state. It is used for selecting data sets. You can create instances of this
    class and add them to your Pygame user interface.

    Example:
        # Create a data set button
        button = DataSetButton(100, 200, 150, 50, "Data Set 1")

        # Draw the button on the Pygame screen
        button.draw(screen)

        # Toggle the button's selection state
        button.toggle_select()
    """

    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.selected = False

    def draw(self, screen):
        # Button background and text colors
        bg_color = BLACK if self.selected else WHITE
        text_color = WHITE if self.selected else BLACK
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, text_color, self.rect, 1)

        # Render text
        text_surface = gothic_font.render(self.text, True, text_color)

        # Calculate text position for vertical centering
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2

        # Draw text
        screen.blit(text_surface, (text_x, text_y))

    def toggle_select(self):
        self.selected = not self.selected


# Initialize DataSet buttons
button_width, button_height = 108, 34  # Customize as needed
button_gap = 10
data_set_buttons = []
for i, option in enumerate(dropdown_options):
    x = (i % 6) * (button_width + button_gap) + 50  # Adjust starting x-position
    y = (i // 6) * (button_height + button_gap) + 750  # Adjust starting y-position
    data_set_buttons.append(DataSetButton(x, y, button_width, button_height, option))


# Function to draw the UI elements
def draw_ui():
    """
    Draw the user interface elements on the Pygame screen.

    This function is responsible for rendering various UI elements on the Pygame screen, including
    the background image, title, labels, icons, phrases, buttons, and data set buttons. It creates a
    visually appealing and interactive user interface for the application.

    Note:
        Make sure to set up the necessary global variables (e.g., background_image, title_font,
        box_labels, random_icons, phrases, save_button, generate_button, data_set_buttons) before
        calling this function.

    Example:
        # Set up UI elements
        background_image = pygame.image.load("background.png")
        title_font = pygame.font.Font(None, 36)
        box_labels = ["Label 1", "Label 2", "Label 3"]
        random_icons = [(icon_surface, _) for icon_surface, _ in random_icons]
        phrases = [("Phrase 1", (100, 200)), ("Phrase 2", (200, 300))]
        save_button = pygame.Rect(50, 400, 100, 40)
        generate_button = pygame.Rect(200, 400, 100, 40)
        data_set_buttons = [DataSetButton(100, 500, 120, 50, "Data Set 1")]

        # Call the draw_ui function to render the UI elements
        draw_ui()
    """
    screen.blit(background_image, (0, 0))

    # Draw title
    title_surface = title_font.render(
        "And then these thoughts billowed forth....", True, BLACK
    )
    title_x = (screen_width - title_surface.get_width()) // 2
    title_y = 20  # Adjust as needed for padding
    screen.blit(title_surface, (title_x, title_y))

    # Draw labels for boxes
    for i, label in enumerate(box_labels):
        text_surface = gothic_font.render(label, True, BLACK)
        screen.blit(text_surface, (50, i * 100 + 215))

    # Calculate positions and draw icons
    total_icons_width = (
        sum(icon_surface.get_width() for icon_surface, _ in random_icons)
        + (len(random_icons) - 1) * 10
    )
    start_x = (screen_width - total_icons_width) // 2
    y_position = (
        title_y + title_surface.get_height() + 20
    )  # Adjust as needed for vertical spacing

    for icon_surface, _ in random_icons:
        screen.blit(icon_surface, (start_x, y_position))
        start_x += (
            icon_surface.get_width() + 10
        )  # Move to the next position with a 10px gap

    # Draw phrases at their current positions
    for phrase, pos in phrases:
        text_surface = gothic_font.render(phrase, True, BLACK)
        screen.blit(text_surface, pos)

    # Draw buttons with text centered
    for button, button_text in [(save_button, "Save"), (generate_button, "Generate")]:
        pygame.draw.rect(screen, WHITE, button)
        pygame.draw.rect(screen, BLACK, button, 1)
        button_text_surface = gothic_font.render(button_text, True, BLACK)
        text_x = button.x + (button.width - button_text_surface.get_width()) // 2
        text_y = button.y + (button.height - button_text_surface.get_height()) // 2
        screen.blit(button_text_surface, (text_x, text_y))

    # Draw data set buttons
    for button in data_set_buttons:
        button.draw(screen)


def save_state():
    """
    Save the current state of the application as an HTML file and open it in a web browser.

    This function creates an HTML file containing the current state of the application, including
    selected icons and phrases. The file is saved with a timestamp and can be opened in a web
    browser for viewing. If the theme-specific icon folder does not exist, it falls back to the
    "Medieval" theme.

    The HTML content is generated based on the current state of the application, including icons
    and phrases. The content is embedded in an HTML template that includes a title and
    background styling.

    Note:
        Make sure to set up the necessary global variables (e.g., current_theme, random_icons,
        phrases) before calling this function.

    Example:
        # Set up necessary global variables
        current_theme = "Fantasy"
        random_icons = [(icon_surface, _) for icon_surface, _ in random_icons]
        phrases = [("Once upon a time...", (100, 200)), ("In a land far, far away...", 
        (200, 300))]

        # Call the save_state function to save the current state as an HTML file and open it
        in a browser
        save_state()
    """
    # Check if the theme-specific icon folder exists, if not, use 'Medieval'
    icon_theme_folder = (
        current_theme if os.path.exists(f"icons/{current_theme}") else "Medieval"
    )

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{current_theme}_{timestamp}.html"
    file_path = os.path.join("saves", file_name)

    content = ""

    content += "<div class='container1'>\n"
    for _, path in random_icons:  # Access the icon's path
        icon_file_name = os.path.basename(path)
        content += (
            f"<img src='../icons/{icon_theme_folder}/{icon_file_name}' alt='icon'>\n"
        )
    content += "</div><div class='container2'>\n"
    
    phrases_sorted = sorted(
        phrases, key=lambda x: x[1][1]
    )  # Sort phrases by their y-position
    for (phrase, _), label in zip(phrases_sorted, box_labels):
        content += f"<h3>{label} {phrase}</h3>\n"
    content += "</div>"

    first_phrase = phrases_sorted[0][0] if phrases_sorted else ""
    title = current_theme + " " + first_phrase if phrases_sorted else "Story Maker"

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>

<body>
    <div class="container">
    {content}
    </div>
</body>
</html>
"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_template.format(title=current_theme, content=content))

    # Open the HTML file in chrome
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    # Get the current directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the absolute path of the HTML file
    full_path = os.path.join(script_dir, file_path)

    # Open the HTML file in Chrome
    subprocess.Popen([chrome_path, "file://" + full_path])


# Function to handle phrase dragging and button interactions
def handle_dragging(event):
    """
    Handle phrase dragging and button interactions in the application.

    This function is responsible for managing interactions when the user clicks and drags phrases or
    interacts with buttons on the screen. It detects button clicks, initiates phrase dragging, and
    handles button actions such as saving, generating, and selecting data sets.

    Args:
        event (pygame.Event): The Pygame event representing user input.

    Global Variables:
        dragging (bool): A flag indicating whether a phrase is currently being dragged.
        dragged_phrase_index (int): The index of the currently dragged phrase in the 'phrases' list.
        current_theme (str): The currently selected theme for generating phrases and icons.
        data (dict): The data loaded for the current theme.
        random_icons (list): The list of randomly selected icons for the current theme.

    Note:
        Make sure to set up the necessary global variables (e.g., save_button, generate_button,
        data_set_buttons, phrases, random_icons, current_theme, data) before calling this function.

    Example:
        # Set up necessary global variables
        save_button = pygame.Rect(50, 400, 100, 40)
        generate_button = pygame.Rect(200, 400, 100, 40)
        data_set_buttons = [DataSetButton(100, 500, 120, 50, "Data Set 1")]
        phrases = [("Once upon a time...", (100, 200)), ("In a land far, far away...", (200, 300))]
        random_icons = [(icon_surface, _) for icon_surface, _ in random_icons]
        current_theme = "Fantasy"
        data = load_data(current_theme.lower() + ".json")

        # Call the handle_dragging function to manage user interactions
        pygame.event.get()  # Get Pygame events
        for event in pygame.event.get():
            handle_dragging(event)
    """
    global dragging, dragged_phrase_index, current_theme, data, random_icons
    if event.type == pygame.MOUSEBUTTONDOWN:
        if save_button.collidepoint(event.pos):
            save_state()
        elif generate_button.collidepoint(event.pos):
            phrases[:] = generate_phrases()
            random_icons = generate_icons()
        else:
            for button in data_set_buttons:
                if button.rect.collidepoint(event.pos):
                    current_theme = (
                        button.text.capitalize()
                    )  # This ensures the first letter is capitalized
                    data = load_data(
                        current_theme.lower() + ".json"
                    )  # Assuming the file names are lowercase
                    phrases[:] = generate_phrases()
                    random_icons = generate_icons()
                    button.toggle_select()
                    # Deselect all other buttons
                    for other_button in data_set_buttons:
                        if other_button != button:
                            other_button.selected = False
                    break
            for i, (_, pos) in enumerate(phrases):
                if pygame.Rect(pos, gothic_font.size(phrases[i][0])).collidepoint(
                    event.pos
                ):
                    dragging = True
                    dragged_phrase_index = i
                    break
    elif event.type == pygame.MOUSEBUTTONUP:
        dragging = False
        dragged_phrase_index = None
    elif event.type == pygame.MOUSEMOTION and dragging:
        if dragged_phrase_index is not None:
            phrases[dragged_phrase_index] = (
                phrases[dragged_phrase_index][0],
                event.pos,
            )


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        handle_dragging(event)

    draw_ui()
    pygame.display.flip()

pygame.quit()
