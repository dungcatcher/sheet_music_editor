from PIL import Image
import os
import json


def get_bounding_boxes():  # Run only once
    notes_dict = []
    directory = './Notes'

    done = 0

    sorted_pages = sorted(os.listdir(directory), key=lambda x: int(x.split('Page')[1]))
    for page in sorted_pages:
        page_dict = {
            'r': [], 'l': [], 'symbols': [], 'extra': []
        }
        page_dir = os.path.join(directory, page)
        for voice in os.listdir(page_dir):
            target_voice_dict = {'Extra': 'extra', 'LH': 'l', 'RH': 'r', 'Symbols': 'symbols'}
            target_voice_key = target_voice_dict[voice]
            voice_dir = os.path.join(page_dir, voice)

            sorted_notes = sorted(os.listdir(voice_dir), key=lambda x: int(x.replace('.png', '')[1:]))
            for note in sorted_notes:
                note_path = os.path.join(voice_dir, note)
                img = Image.open(note_path)
                bounding_box = img.getbbox()

                page_dict[target_voice_key].append(bounding_box)
                done += 1
                print(done)

        notes_dict.append(page_dict)

    with open('boxes.json', 'w') as f:
        json.dump(notes_dict, f)

