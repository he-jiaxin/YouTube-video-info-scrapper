
from tkinter import Tk, Label, Button, Entry, StringVar, messagebox, Frame
from tkinter.ttk import Progressbar
from Updated_Youtube_webscrappers import YouTubeScraper
import threading


class ScraperApp:

    def __init__(self, window):
        self.window = window
        self.window.title("YouTube Scraper")

        self.label = Label(window, text="Enter the YouTube channel URL:")
        self.label.pack(pady=10)

        self.url_var = StringVar()
        self.entry = Entry(window, textvariable=self.url_var, width=50)
        self.entry.pack(pady=10)

        # Adding a frame for progress bar and label
        self.progress_frame = Frame(window)
        self.progress_frame.pack(pady=20, fill='x')

        self.progress_label = Label(self.progress_frame, text="Progress:")
        self.progress_label.pack(side='left')

        self.progress = Progressbar(self.progress_frame, orient="horizontal", length=200, mode="determinate",
                                    maximum=100)
        self.progress.pack(side='right', fill='x', expand=True)

        # Initially setting progress bar to 0
        self.progress["value"] = 0

        self.scrape_btn = Button(window, text="Scrape", command=self.start_scrape_thread)
        self.scrape_btn.pack(pady=20)

    def start_scrape_thread(self):
        # Start the scrape in a separate thread to avoid freezing the UI
        threading.Thread(target=self.scrape_data).start()

    def scrape_data(self):
        url = self.url_var.get()
        if url:
            filename = url.replace("https://www.youtube.com/@", "").replace("/", "_") + ".csv"
            scraper = YouTubeScraper(url, self.update_progress)
            scraper.save_to_csv(filename)
            messagebox.showinfo("Success", f"Data saved to {filename}")
        else:
            messagebox.showwarning("Error", "Please enter a valid YouTube channel URL!")

    def update_progress(self, progress):
        self.progress["value"] = progress
        self.window.update()


if __name__ == "__main__":
    root = Tk()
    scraper_app = ScraperApp(root)
    root.mainloop()
