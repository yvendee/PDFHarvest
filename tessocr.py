import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# img = cv2.imread("page_1.jpg")
img = cv2.imread("page_3.jpg")
# img = cv2.resize(img, (1190, 1684))
img = cv2.resize(img, (1050, 1680))
# img = cv2.resize(img, (2160, 4096))
# cv2.imshow("Image", img)
text = pytesseract.image_to_string(img)
print(text)
# cv2.waitKey(0)
# cv2.destroyAllWindows()