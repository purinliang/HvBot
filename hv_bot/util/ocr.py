import pytesseract
from PIL import Image


def ocr_single_line_text(image: Image) -> str:
    # TODO: add some try-except to protect
    # use pytesseract to ocr the image
    # it takes about 0.25 second to ocr only one line text!
    pytesseract.pytesseract.tesseract_cmd = "D:\\TesseractOCR\\tesseract.exe"
    gray_scale_image = image.convert("L")  # gray_scale_image has better result
    ocr_result_text = str(pytesseract.image_to_string(gray_scale_image, lang="eng", config='--psm 7')).strip()
    # print(f"ocr_result_text={ocr_result_text}")
    return ocr_result_text
