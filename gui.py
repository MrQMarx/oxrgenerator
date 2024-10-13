import customtkinter
from customtkinter import filedialog
from PIL import Image
import face_recognition
from imdb import Cinemagoer
import requests
import shutil
import os
import cv2
from datetime import timedelta
import re

customtkinter.set_appearance_mode("System")
# customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
root.geometry("500x500")
root.iconbitmap('img/xraylogo.ico')
root.title("Open X-Ray Generator")

value = 0.5
filename = ""
filmname = ""
tolerance_global = 0


def clean_up():
    write_to_textbox_then_refresh("===============")
    write_to_textbox_then_refresh("Cleanup Time")
    write_to_textbox_then_refresh("===============")
    try:
        headshots = os.listdir("img/actors")
        for file in headshots:
            file_path = os.path.join("img/actors", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        write_to_textbox_then_refresh("All headshots deleted successfully.")
    except OSError:
        write_to_textbox_then_refresh("Error occurred while deleting headshots.")
    update_progress_bars(0.5, 0.99)
    try:
        film_frames = os.listdir("img/film_frames")
        for file in film_frames:
            file_path = os.path.join("img/film_frames", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        write_to_textbox_then_refresh("All film frames deleted successfully.")
    except OSError:
        write_to_textbox_then_refresh("Error occurred while deleting film frames.")
    update_progress_bars(1, 1)
    write_to_textbox_then_refresh("===============")
    write_to_textbox_then_refresh("All Done!")


def run():
    global tolerance_global
    tolerance_global = slider_1.get()
    print(filename)
    # progressbar_1.set(value)
    # textbox.insert("0.0", "Some example text!\n")
    # creating instance of IMDb
    ia = Cinemagoer()

    film_name = entry_1.get()
    print(film_name)

    # Search for a film name on IMDB
    search = ia.search_movie(film_name)
    write_to_textbox_then_refresh(f"Top search result is {search[0]}")

    # Get a cast list from a film on IMDB
    code = search[0].movieID
    movie = ia.get_movie(code)
    write_to_textbox_then_refresh("===============")
    write_to_textbox_then_refresh(f"Cast for {search[0]}")
    write_to_textbox_then_refresh("===============")
    cast = movie['cast']
    # cast = movie[]
    for x in range(len(cast)):
        actor = cast[x]
        write_to_textbox_then_refresh(str(actor))
    # textbox.insert("0.0", "===============\n")

    # Download Headshots for each of the actors
    write_to_textbox_then_refresh("Downloading Headshots...")
    castWithHeadshots = []
    for x in range(len(cast)):
        # for x in range(2):
        # name
        name = cast[x]
        # searching the name
        # search = ia.search_person('Harry Styles')
        # Get person id
        # code = search[0].personID
        # getting person object
        actor = ia.get_person(cast[x].personID)
        # printing object it prints its name
        # print(actor)
        update_progress_bars((x/len(cast))/2, (x/len(cast))/20)
        # getting image
        try:
            image = actor['headshot']
        except:
            write_to_textbox_then_refresh(f"No Headshot available for {name}")
            continue
        # print(image)
        z = image.split("V1_")
        # image.split("_V1_")
        # print(z[0])
        full_image = z[0] + "V1_.jpg"
        # print(full_image)
        # print(image)
        # creating a image object (main image)
        res = requests.get(full_image, stream=True)

        if res.status_code == 200:
            with open(f"./img/actors/{name}.jpg", 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            write_to_textbox_then_refresh(f'Headshot for {name} successfully Downloaded: {image}')
            castWithHeadshots.append(cast[x])
        else:
            write_to_textbox_then_refresh(f'Headshot for {name} Couldn\'t be retrieved')

        # img_data = requests.get(image).content
        # with open(f"actors/{name}.jpg", 'wb') as handler:
        #    handler.write(img_data)
        # print(f"Headshot for {name} saved")
    write_to_textbox_then_refresh("===============")

    # Verify that there are in fact faces in these Headshots
    verifiedHeadshots = []
    for x in range(len(castWithHeadshots)):
        image = face_recognition.load_image_file(f'./img/actors/{castWithHeadshots[x]}.jpg')
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 1:
            # Get the coordinates of the first face (top, right, bottom, left)
            top, right, bottom, left = face_locations[0]

            # Convert the numpy array image to a PIL Image
            pil_image = Image.fromarray(image)

            # Adding a proportional border to stop CERTAIN actors (ie. Gil Bellows) breaking the system
            horBorder = (right - left) / 4
            if left - horBorder > 0:
                left = left - horBorder
            else:
                left = 0
            if right + horBorder < pil_image.width:
                right = right + horBorder
            else:
                right = pil_image.width
            # Should I do a vertical border?
            # Maybe, but it seems the face locations are normally square so there's no point.
            if top - horBorder > 0:
                top = top - horBorder
            else:
                top = 0
            if bottom + horBorder < pil_image.height:
                bottom = bottom + horBorder
            else:
                bottom = pil_image.height

            # Crop the image to the first face
            face_image = pil_image.crop((left, top, right, bottom))

            # Check if the cropped image is taller than 150 pixels
            if face_image.height > 150:
                # Resize the image while maintaining the aspect ratio
                aspect_ratio = face_image.width / face_image.height
                new_height = 150
                new_width = int(aspect_ratio * new_height)
                face_image = face_image.resize((new_width, new_height), Image.LANCZOS)

            # Save or show the resulting image
            face_image.save(f"./img/actors/{castWithHeadshots[x]}.jpg")  # You can also use face_image.show() to display
            image = face_recognition.load_image_file(f'./img/actors/{castWithHeadshots[x]}.jpg')
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 1:
                write_to_textbox_then_refresh(f"Verified headshot for {castWithHeadshots[x]}")
                verifiedHeadshots.append(castWithHeadshots[x])
                update_progress_bars((x / len(castWithHeadshots))/2+0.5, (x / len(castWithHeadshots)) / 20+0.05)
    write_to_textbox_then_refresh("===============")

    # Extract one frame per second
    write_to_textbox_then_refresh("Extracting One Frame Per Second")
    write_to_textbox_then_refresh("===============")

    pathOut = r"./img/film_frames/"
    vid = filename
    cap = cv2.VideoCapture(vid)
    count = 0
    success = True
    framerate = round(cap.get(cv2.CAP_PROP_FPS))
    totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    totalSeconds = round(totalFrames / framerate) + 300

    # print("totalSeconds should be 9520 but is " + str(totalSeconds))

    while success:
        success, image = cap.read()

        if not success or image is None:
            break
        # print('read a new frame:', success)
        if count % framerate == 0:
            cv2.imwrite(pathOut + '%s.jpg' % "{:05d}".format(int(int(count) / framerate)), image)
        count += 1
        update_progress_bars((int(int(count) / framerate) / totalSeconds),
                             (int(int(count) / framerate) / totalSeconds) / 20 + 0.1)
    cap.release()
    # Create subtitle file
    # They look like
    # 1
    # 00:00:07,114 --> 00:00:11,834
    # Lines
    #
    with open(f'{search[0]} ({movie["year"]}).OXR', 'w') as f:
        f.write('\n')

    # See how many faces are in a Frame
    script_directory = os.path.dirname(__file__)

    # Define the image folder in the same directory
    listing = os.path.join(script_directory, 'img', 'film_frames')
    frame_files = os.listdir(listing)

    # listing = '/img/film_frames'
    subtitleNum = 0
    facesInFrame = []
    for frame_image_file in frame_files:
        # Construct the full file path
        image_path = os.path.join(listing, frame_image_file)
        image = face_recognition.load_image_file(
            # listing + "/" + frame_image_file)
            # os.path.join(listing, frame_image_file))
            image_path)
        face_locations = face_recognition.face_locations(image)

        # Array of coords of each face
        # print(face_locations)
        write_to_textbox_then_refresh(str(frame_image_file))
        write_to_textbox_then_refresh(f"There are {len(face_locations)} people in this frame")
        write_to_textbox_then_refresh("===============")
        if len(face_locations) == 0:
            facesInFrame = []
            continue
        # If Frame is 75% the same as the last frame
        # Skip the Face Finding and reprint the previous frame's list
        sex = frame_image_file.split(".")
        tolerance = 10000  # between 100000 and 1000000
        # currentImage = cv2.imread("img/film_frames/" + "{:05d}".format(int()) + ".jpg")
        currentImage = cv2.imread(listing + "/" + "{:05d}".format(int(sex[0])) + ".jpg")
        # previousImage = cv2.imread("img/film_frames/" + "{:05d}".format(int(sex[0]) - 1) + ".jpg")
        previousImage = cv2.imread(listing + "/" + "{:05d}".format(int(sex[0]) - 1) + ".jpg")

        # print("currentImage is " + str(currentImage))
        # print("previousImage is " + str(previousImage))

        # Get image dimensions (height, width, channels)
        height, width, _ = currentImage.shape

        # Calculate the total number of pixels per channel
        total_pixels_per_channel = height * width

        # Set tolerance as a percentage (e.g., 75%)
        # tolerance_percentage = 75  # Tolerance as percentage
        # tolerance = (tolerance_percentage / 100) * total_pixels_per_channel
        tolerance = tolerance_global * total_pixels_per_channel

        difference = cv2.subtract(previousImage, currentImage)
        b, g, r = cv2.split(difference)
        if cv2.countNonZero(b) < tolerance and cv2.countNonZero(g) < tolerance and cv2.countNonZero(r) < tolerance \
                and (len(face_locations) == len(facesInFrame)):
            write_to_textbox_then_refresh("The images are close enough to Equal")
        else:
            # Compare face to known actor
            facesFound = 0
            facesLeft = len(face_locations)
            facesInFrame = []
            # for x in range(2):
            for x in range(len(verifiedHeadshots)):
                if facesLeft > 0:
                    write_to_textbox_then_refresh(f"Checking frame for {verifiedHeadshots[x]}")
                    actor_image = face_recognition.load_image_file(f'./img/actors/{verifiedHeadshots[x]}.jpg')
                    actor_face_encoding = face_recognition.face_encodings(actor_image)[0]

                    unknown_image = image
                    for y in range(len(face_locations) - 1, -1,
                                   -1):  # Iterate backwards to avoid index shift issues when popping

                        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[y]
                        # compare
                        results = face_recognition.compare_faces([actor_face_encoding], unknown_face_encoding)
                        write_to_textbox_then_refresh(str(results))
                        if results[0]:
                            facesFound = facesFound + 1
                            facesLeft = facesLeft - 1
                            facesInFrame.append(verifiedHeadshots[x])
                            face_locations.pop(y)
                            break  # Move to the next actor once a match is found for this actor

        secs = timedelta(seconds=int(sex[0]))
        with open(f'{search[0]} ({movie["year"]}).OXR', 'a') as f:
            subtitleNum = subtitleNum + 1
            f.write(str(subtitleNum))
            f.write('\n')
            f.write(str(secs) + ", 000 --> " + str(secs) + ", 999")
            f.write('\n')
            for y in range(len(facesInFrame)):
                f.write(facesInFrame[y]['name'])
                if y < len(facesInFrame):
                    f.write("||")
            f.write('\n')
            f.write('\n')

        update_progress_bars((int(sex[0]) / totalSeconds),
                             ((int(sex[0]) / totalSeconds) / 1.3) + 0.2)
    clean_up()


def write_to_textbox_then_refresh(text):
    textbox.insert("end", text + "\n")
    print(text)
    root.update()
    # root.mainloop()


def update_progress_bars(sectionalProgress, overallProgress):
    progressbar_1.set(sectionalProgress)
    progressbar_2.set(overallProgress)
    root.update()


def select_film():
    global filename
    filename = filedialog.askopenfilename()
    print(filename)
    # Step 1: Extract the file name
    film_name = os.path.basename(filename)

    # Step 2: Use regex to match everything up to the year and cut off the rest
    # This pattern captures everything before and including the year
    match = re.match(r"^(.*?)(\d{4})", film_name)

    if match:
        # Get the part before and including the year
        truncated_name = match.group(0)
        print(truncated_name)
        entry_1.insert(0, truncated_name.replace('.', ' '))
    else:
        print("No valid year found in the file name.")
        entry_1.insert(0, film_name)
    button_2.configure(state='normal')


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=10, padx=60, fill="both", expand=True)

label_1 = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Open X-Ray Generator")
label_1.pack(pady=10, padx=10)

button_1 = customtkinter.CTkButton(master=frame, command=select_film, text="Select Video File")
button_1.pack(pady=10, padx=10)

entry_1 = customtkinter.CTkEntry(master=frame, placeholder_text="Film Title")
entry_1.pack(pady=10, padx=10)

label_2 = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Similarity "
                                                                                "to last frame to discard as duplicate")
label_2.pack(pady=0, padx=10)
slider_1 = customtkinter.CTkSlider(master=frame, from_=0, to=1)
slider_1.pack(pady=10, padx=10)
slider_1.set(0.75)

button_2 = customtkinter.CTkButton(master=frame, command=run, text="Run", state='disabled')
button_2.pack(pady=10, padx=10)

label_3 = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Step Progress")
label_3.pack(pady=0, padx=10)
progressbar_1 = customtkinter.CTkProgressBar(master=frame)
progressbar_1.pack(pady=10, padx=10)
progressbar_1.set(0)

label_4 = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Overall Progress")
label_4.pack(pady=0, padx=10)
progressbar_2 = customtkinter.CTkProgressBar(master=frame)
progressbar_2.pack(pady=10, padx=10)
progressbar_2.set(0)

textbox = customtkinter.CTkTextbox(master=frame, corner_radius=0, width=450)
textbox.pack(pady=10, padx=10)

root.mainloop()

