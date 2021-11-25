from PySide6.QtWidgets import QApplication
import sys
import argparse

from opacity_ui.opacity_window_logic import OpacityWindow


def main(args):
    app = QApplication([])

    window = OpacityWindow(args)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-p1", type=str,
                        default="C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI"
                                "\\Case5\\MRI\\Case5-T1.nii",
                        help="Path to first .nii file")
    parser.add_argument("-p2", type=str,
                        default="C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI"
                                "\\Case3\\MRI\\Case3-T1.nii",
                        help="Path to first .nii file")
    parser.add_argument("-p3", type=str,
                        default="C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI"
                                "\\Case6\\MRI\\Case6-T1.nii",
                        help="Path to first .nii file")

    params = parser.parse_args()

    main(params)
