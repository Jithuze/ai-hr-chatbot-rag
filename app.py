import flet as ft
import ollama
from functions import search, ptt, add_vector
import shutil
from collections import deque
import os

class ChatMessage(ft.Row):
    def __init__(self, message: str, is_bot: bool = False):
        super().__init__()
        self.message = message  # Store message for later updates
        self.controls = [
            ft.Text("Bot" if is_bot else "You", weight="bold"),
            ft.Text(message, selectable=True, expand=True, weight=ft.FontWeight.W_500),
        ]

    def update_message(self, new_message: str):
        # Update the text of the message
        self.controls[1].value = new_message
        self.controls[1].update()

def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Resume Bot"
    page.window.width = 1280
    page.window.height = 720
    theme_color = "#FF204E"
    bg_color = "#00224D"
    primary_color = "#007F73"
    secondary_color = "#4CCD99" 
    save_dir = "assets/uploaded_resumes"
    page.theme_mode = ft.ThemeMode.LIGHT

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    def summary(prompt, filename, user_query):
        response = ollama.chat(
            model='byte-s', 
            messages=[{'role': 'user', 'content': f'Return response in 200 words why you think {prompt} is a good {user_query}.'}],
            stream=True
        )

        # Add a message to indicate the bot is responding
        typing_message = ChatMessage("Bot is typing...", is_bot=True)
        chat.controls.append(typing_message)
        page.update()

        # Remove the "typing..." indicator and add the actual response
        response_text = ""
        for chunk in response:
            response_text += chunk['message']['content']
            typing_message.update_message(response_text)  # Update the typing message with accumulated text
            page.update()

        # After streaming is complete, replace the typing message with the final response
        chat.controls.remove(typing_message)
        chat.controls.append(ChatMessage(response_text, is_bot=True))

        # Add a button to link to the file
        file_button = ft.FilledTonalButton(
            text=f"File Name: {filename}",
            on_click=lambda e, fn=filename: open_file(fn),  # fn is passed to handle the button click correctly
        )
        chat.controls.append(file_button)
        page.update()

    snack_bar_queue = deque()

    snack_bar = ft.SnackBar(content=ft.Text(""), action="OK")
    page.overlay.append(snack_bar)

    dialog_modal = ft.AlertDialog(modal=True)
    file_to_handle = None

    def show_snack_bar():
        if snack_bar_queue:
            file_name = snack_bar_queue.popleft()
            snack_bar.content = ft.Text(f"Uploaded and saved: {file_name}")
            snack_bar.open = True
            page.update()

            def close_snack_bar(e):
                snack_bar.open = False
                page.update()
                if snack_bar_queue:
                    page.after(1000, show_snack_bar)
            
            snack_bar.on_dismiss = close_snack_bar
            page.update()

    def handle_file_replacement(file, action):
        if file is not None:
            file_path = os.path.join(save_dir, file.name)
            if action == "replace":
                shutil.copyfile(file.path, file_path)
                snack_bar_queue.append(file.name)
                show_snack_bar()
            elif action == "skip":
                snack_bar_queue.append(f"Skipped: {file.name}")
                show_snack_bar()

    def on_dialog_result(e):
        if file_to_handle is not None:
            if e.control.text == "Replace":
                handle_file_replacement(file_to_handle, "replace")
            elif e.control.text == "Skip":
                handle_file_replacement(file_to_handle, "skip")

        dialog_modal.open = False
        page.update()

    replace_button = ft.TextButton("Replace", on_click=on_dialog_result)
    skip_button = ft.TextButton("Skip", on_click=on_dialog_result)

    dialog_modal.title = ft.Text("File already exists")
    dialog_modal.content = ft.Text("The file already exists. Would you like to replace it or skip?")
    dialog_modal.actions = [replace_button, skip_button]
    dialog_modal.actions_alignment = ft.MainAxisAlignment.END

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        nonlocal file_to_handle
        if e.files:
            for file in e.files:
                file_path = os.path.join(save_dir, file.name)
                if os.path.exists(file_path):
                    file_to_handle = file
                    dialog_modal.open = True
                    page.dialog = dialog_modal
                    page.update()
                else:
                    shutil.copyfile(file.path, file_path)
                    snack_bar_queue.append(file.name)
                    show_snack_bar()
                update_vectordb(file_path, file.name)

    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker)

    def update_vectordb(file_path, file_name):
        text = ptt(f"./{file_path}")
        add_vector(file_name, text)

    def send_message_click(e):
        if new_message.value == "/clear":
            chat.controls.clear()
            new_message.value = ""
            page.update()
        elif new_message.value.strip():
            user_msg = new_message.value.strip()
            
            # Add user's message to chat
            chat.controls.append(ChatMessage(user_msg, is_bot=False))
            page.update()
            
            # Clear input field
            new_message.value = ""
            new_message.focus()

            # Call summary function for bot reply
            response = search(user_msg)
            if response is None:
                bot_message = "No relevant documents found for your query."
                chat.controls.append(ChatMessage(bot_message, is_bot=True))
                return

            data = response.get('documents', [])
            for i in range(len(data[0])):
                document = data[0][i]
                filename = response.get('metadatas', [])
                filename = filename[0][i]['item_id']
                summary(document, filename, user_msg)

    def open_file(file_name):
        file_path = os.path.join(save_dir, file_name)
        try:
            os.startfile(file_path)  # For Windows
        except AttributeError:
            os.system(f"open {file_path}")  # For macOS/Linux

        print(f"Opening file: {file_path}")
        
    def open_file_drawer(e):
        # Open the drawer and then update it
        page.open(file_drawer)
        # Add resume buttons to the drawer
        add_resume_buttons_to_drawer(file_drawer, save_dir)

    def add_resume_buttons_to_drawer(file_drawer, directory):
        """
        Adds a button for each PDF file in the specified directory to the file_drawer.
        
        Args:
        - file_drawer: The NavigationDrawer instance where buttons will be added.
        - directory: The directory containing the PDF files.
        """
        # Clear existing controls
        file_drawer.controls = [ft.Text("Uploaded Resumes", weight=ft.FontWeight.BOLD)]

        # List all PDF files in the directory
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                # Create a button for each PDF file
                file_button = ft.FilledTonalButton(
                    text=f"File Name: {filename}",
                    on_click=lambda e, fn=filename: open_file(fn),  # Pass filename to open_file function
                )
                # Add the button to the file_drawer
                file_drawer.controls.append(file_button)
        
        # Update the file_drawer to reflect changes
        file_drawer.update()

    # Create and add NavigationDrawer to the page
    file_drawer = ft.NavigationDrawer(
        elevation=3,
    )
    

    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    ft.FilledTonalButton(
                        "Upload Resume",
                        icon=ft.icons.UPLOAD_ROUNDED,
                        on_click=lambda _: file_picker.pick_files(allow_multiple=True, allowed_extensions=["pdf"]),
                    ),
                    ft.IconButton(icon=ft.icons.CLOUD_UPLOAD_ROUNDED, icon_color=ft.colors.BLACK, on_click=open_file_drawer),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ),
        ft.Container(content=chat, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=5, padding=10, expand=True),
        ft.Row([new_message, ft.IconButton(icon=ft.icons.SEND_ROUNDED, tooltip="Send message", on_click=send_message_click)]),
    )

    page.update()

ft.app(main, assets_dir='/assets')
