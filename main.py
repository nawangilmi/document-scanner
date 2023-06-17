import cv2
import imutils
from skimage.filters import threshold_local
from transform import perspective_transform
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def scan_image():
    global warped, result_label, file_path, scan_button
    # Mengunci tombol scan
    scan_button.config(state=tk.DISABLED)

    original_img = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
    copy = original_img.copy()

    ratio = original_img.shape[0] / 500.0
    img_resize = imutils.resize(original_img, height=500)

    gray_image = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edged_img = cv2.Canny(blurred_image, 75, 200)

    cnts, _ = cv2.findContours(edged_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    
        if len(approx) == 4:
            doc = approx
            break
    p = []

    for d in doc:
        tuple_point = tuple(d[0])
        cv2.circle(img_resize, tuple_point, 3, (0, 0, 255), 4)
        p.append(tuple_point)

    warped_image = perspective_transform(copy, doc.reshape(4, 2) * ratio)
    warped_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

    T = threshold_local(warped_image, 11, offset=10, method="gaussian")
    warped = (warped_image > T).astype("uint8") * 255
    cv2.imwrite('./'+'scan_result.png', warped)

    # Menampilkan gambar hasil pemindaian pada jendela GUI
    result_image = imutils.resize(warped, height=500)
    result_photo = ImageTk.PhotoImage(Image.fromarray(result_image))
    result_label.configure(image=result_photo)
    result_label.image = result_photo

    # Membuka kunci tombol scan
    scan_button.config(state=tk.NORMAL)

def save_image():
    global file_path
    if file_path:
        initial_img = cv2.imread(file_path)
        cv2.imwrite('./'+'initial_image.png', initial_img)
        messagebox.showinfo("Save Image", "Image saved successfully!")
    else:
        messagebox.showwarning("Save Image", "No image to save.")

def save_scan():
    global warped
    if warped is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, warped)
            messagebox.showinfo("Save Scan", "Scanned image saved successfully!")
        else:
            messagebox.showwarning("Save Scan", "No file path selected.")
    else:
        messagebox.showwarning("Save Scan", "No Scanned image to save.")


def select_image():
    global file_path, initial_label

    # Membuka dialog untuk memilih berkas gambar
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

    if file_path:
        # Memuat gambar yang dipilih
        initial_img = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
        initial_img = imutils.resize(initial_img, height=500)
        initial_photo = ImageTk.PhotoImage(Image.fromarray(initial_img))

        # Memperbarui label gambar awal
        initial_label.configure(image=initial_photo)
        initial_label.image = initial_photo


# Membuat jendela tkinter
window = tk.Tk()
window.title("Document Scanner")

# Membuat menu strip
menubar = tk.Menu(window)

# Membuat menu "File"
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open Image", command=select_image)
file_menu.add_command(label="Save Image", command=save_image)
file_menu.add_command(label="Save Scanned Image", command=save_scan)
menubar.add_cascade(label="File", menu=file_menu)

# Menghubungkan menu strip
window.config(menu=menubar)

# Membuat frame untuk menampilkan label gambar awal dan label gambar hasil
image_frame = tk.Frame(window)
image_frame.pack()

# Membuat label untuk menampilkan gambar awal
initial_label = tk.Label(image_frame)
initial_label.pack(side=tk.LEFT, padx=10, pady=10)

# Membuat label untuk menampilkan gambar hasil
result_label = tk.Label(image_frame)
result_label.pack(side=tk.RIGHT, padx=10, pady=10)

# Membuat tombol untuk Scam
scan_button = tk.Button(window, text="Scan", command=scan_image)
scan_button.pack(pady=10)

# Memulai loop
window.mainloop()