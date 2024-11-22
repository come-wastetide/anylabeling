from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject
from datetime import timedelta, datetime
from .db_actions.get_images import (
    download_unreviewed_scans,
    download_pictures_from_table,
)
from .db_actions.send_annotations import upload_all_scans
import os.path as osp


class GenericWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.func(*self.args, **self.kwargs)
        self.finished.emit()


class DownloadWorker(QThread):
    import_request = pyqtSignal(
        str, bool
    )  # Signal to request import_image_folder
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        current_path,
        filename,
        output_dir,
        last_open_dir,
        parent=None,
    ):
        super().__init__(parent)
        self.current_path = current_path
        self.filename = filename
        self.output_dir = (
            output_dir  # Save the argument as an instance variable
        )
        self.last_open_dir = last_open_dir

    def run(self):
        try:
            print("Fetching and downloading images...")
            limit_date = datetime.now() - timedelta(days=5)
            print(f"Limit date: {limit_date}")

            unreviewed_scans = download_unreviewed_scans(limit_date=limit_date)

            nb_images = len(unreviewed_scans["data"])
            print(f"Found {nb_images} unreviewed scans since last check.")

            default_output_dir = self.output_dir
            if default_output_dir is None and self.filename:
                default_output_dir = osp.dirname(self.filename)
            if default_output_dir is None:
                default_output_dir = self.current_path

            print(f"Output dir: {default_output_dir}")

            for i in range(nb_images // 5 + 1):
                print(f"Downloading images {i*5} to {(i+1)*5}")
                self.progress.emit(f"Downloading images {i*5} to {(i+1)*5}")
                batch = {"data": []}
                if i == nb_images // 5:
                    batch["data"] = unreviewed_scans["data"][i * 5 :]
                else:
                    batch["data"] = unreviewed_scans["data"][
                        i * 5 : (i + 1) * 5
                    ]

                download_pictures_from_table(
                    batch, destination=default_output_dir
                )

                self.import_request.emit(self.last_open_dir, False)

            self.progress.emit(
                f"Finished fetching and downloading {nb_images} images."
            )
            self.finished.emit()

        except Exception as e:
            # logging.error(f"Error getting/downloading images: {e}")
            print(f"Error getting/downloading images: {e}")
            self.progress.emit("Error getting/downloading images.")
            self.finished.emit()


class SendAnnotationWorker(QThread):
    import_request = pyqtSignal(
        str, bool
    )  # Signal to request import_image_folder
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        current_path,
        filename,
        output_dir,
        last_open_dir,
        parent=None,
    ):
        super().__init__(parent)
        self.current_path = current_path
        self.filename = filename
        self.output_dir = (
            output_dir  # Save the argument as an instance variable
        )
        self.last_open_dir = last_open_dir

    def run(self):
        try:
            default_output_dir = self.output_dir
            if default_output_dir is None and self.filename:
                default_output_dir = osp.dirname(self.filename)
            if default_output_dir is None:
                default_output_dir = self.current_path()

            print(f"Output dir: {default_output_dir}")

            self.progress.emit("Generating and sending annotations...")

            destination_dir = osp.join(default_output_dir, "reviewed_images")
            upload_all_scans(default_output_dir, destination_dir)

            # we refresh the image list
            self.import_request.emit(self.last_open_dir, False)

        except Exception as e:
            # logging.error(f"Error generating/sending annotations: {e}")
            print(f"Error generating/sending annotations : {e}")
            self.progress.emit(f"Error generating/sending annotations : {e}")
            self.finished.emit()
