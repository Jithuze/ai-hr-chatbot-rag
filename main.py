import os
import shutil
import flet as ft
from collections import deque
from functions import summary,add_vector,search,ptt,gen_json
import json


class Message:
    def __init__(self, user_name: str, text: str):
        self.user_name = user_name
        self.text = text

class ChatMessage(ft.Row):
    def __init__(self, message: Message, is_bot=False, file_button=None):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        avatar_initials = "Bot" if is_bot else self.get_initials(message.user_name)
        
        # Add file button if it exists
        controls = [
            ft.Text("Bot" if is_bot else message.user_name, weight="bold"),
            ft.Text(message.text, selectable=True, no_wrap=False, width=1000),
        ]
        if file_button:
            controls.append(file_button)

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(avatar_initials),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.LIGHT_BLUE if is_bot else self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                controls,
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "U"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Resume Bot"
    page.window.width= 1280
    page.window.height = 720
    save_dir = "assets/uploaded_resumes"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

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
                # update_vectordb(file_path, file.name)
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
                update_vectordb(file_path,file.name)

    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker)
    

    def bot_reply(user_message):
        response = search(user_message)
        page.pubsub.send_all(Message("Bot", "Here is the top search results...."))
        if response is None:
            bot_message = "No relevant documents found for your query."
            page.pubsub.send_all(Message("Bot", bot_message))
            return

        data = response.get('documents', [])
        for i in range(len(data[0])):
            document = data[0][i]
            summary_response = summary(document)
            filename = response.get('metadatas', [])
            filename = filename[0][i]['item_id']

            # Create a button to link to the file
            file_button = ft.TextButton(
                text=f"File Name : {filename}",
                on_click=lambda e, fn=filename: open_file(fn),  # fn is passed to handle the button click correctly
            )
            
            # Adding the button along with the summary response
            # bot_message = f"{summary_response}"
            # page.pubsub.send_all(Message("Bot", bot_message))
            m = ChatMessage(Message("Bot", summary_response), is_bot=True, file_button=file_button)
            chat.controls.append(m)

            # page.add(ft.Row([file_button]))
            page.update()

    # Function to open the file when the button is clicked
    def open_file(file_name):
        file_path = os.path.join(save_dir, file_name)
        try:
            os.startfile(file_path)  # For Windows
        except AttributeError:
            os.system(f"open {file_path}")  # For macOS/Linux

        print(f"Opening file: {file_path}")


    def send_message_click(e):
        if new_message.value.strip():
            user_message = new_message.value.strip()
            page.pubsub.send_all(Message("User", user_message))
            new_message.value = ""
            new_message.focus()
            page.update()
            bot_reply(user_message)

    def on_message(message: Message):
        is_bot = message.user_name == "Bot"
        m = ChatMessage(message, is_bot=is_bot)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)

    def update_vectordb(file_path, file_name):
        text = ptt(f"./{file_path}")
        text = gen_json(text)
        print(text)
        add_vector(file_name, text)

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

    def open_settings_drawer(e):
        page.open(settings_drawer)

    settings_drawer = ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(label="General Settings", icon=ft.icons.SETTINGS),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(label="Help", icon=ft.icons.HELP),
            ft.NavigationDrawerDestination(label="About", icon=ft.icons.INFO),
        ],
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
                    ft.IconButton(icon=ft.icons.SETTINGS, icon_color=ft.colors.WHITE, on_click=open_settings_drawer),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ),
        ft.Container(content=chat, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=5, padding=10, expand=True),
        ft.Row([new_message, ft.IconButton(icon=ft.icons.SEND_ROUNDED, tooltip="Send message", on_click=send_message_click)]),
    )

ft.app(target=main,assets_dir='/assets')
