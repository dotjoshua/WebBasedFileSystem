from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter#process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


def pdf_to_text(fp):

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)

    # Get text from StringIO
    text = sio.getvalue()

    # Cleanup
    device.close()
    sio.close()


    return text

def get_word_counts(content):
	vectorizer = CountVectorizer(min_df=1)
	X = vectorizer.fit_transform([content])
	word_counts = list(zip(vectorizer.get_feature_names(), np.asarray(X.sum(axis=0)).ravel()))
	filtered_word_counts = list(filter(lambda x: len(x[0]) > 4 , word_counts))
	return filtered_word_counts











