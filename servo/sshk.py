import sshkeyboard

def press(key):
    print(f"'{key}' pressed")

def release(key):
    print(f"'{key}' released")

if __name__ == "__main__":
    sshkeyboard.listen_keyboard(on_press=press, on_release=release)
