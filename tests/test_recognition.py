import io
import unittest
import numpy as np
from PIL import Image
from recognition.detector import ConnectorDetector, RecognitionError, decode

class RecognitionTests(unittest.TestCase):
    def test_threshold_rejected_before_loading_model(self):
        for threshold in [True, False, None, '0.5', 0, -1, 1.1, float('nan'), float('inf')]:
            with self.subTest(threshold=threshold):
                with self.assertRaises(RecognitionError) as error:
                    ConnectorDetector('missing-model-directory', threshold=threshold)
                self.assertEqual(error.exception.code, 'invalid_threshold')

    @classmethod
    def setUpClass(cls): cls.detector=ConnectorDetector()

    def test_actual_model_and_encoded_image(self):
        data=io.BytesIO();Image.new('RGB',(640,320),'white').save(data,format='PNG')
        result=self.detector.recognize(data.getvalue())
        self.assertEqual(result['image']['width'],640)
        self.assertFalse(result['model']['coversNineClasses'])
        self.assertFalse(result['compatibilityVerified'])
        self.assertIsInstance(result['detections'],list)

    def test_invalid_and_oversized_images(self):
        for data in [b'',b'not an image',b'X'*(15*1024*1024+1)]:
            with self.assertRaises(RecognitionError):self.detector.recognize(data)

    def test_animation_rejected(self):
        data=io.BytesIO();Image.new('RGB',(64,64),'white').save(data,format='GIF')
        with self.assertRaises(RecognitionError):self.detector.recognize(data.getvalue())

    def test_geometry_classwise_nms_and_invalid_scores(self):
        values=np.array([[[160,160,160,160],[160,160,160,160],[100,100,100,100],[50,50,50,50],[.9,.8,.1,np.nan],[.1,.1,.95,.1]]],dtype=np.float32)
        result=decode(values,['A','B'],640,320,320,160,0,80,.5)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]['bbox'],{'x':220.,'y':110.,'width':200.,'height':100.})
        self.assertEqual({r['classId'] for r in result},{'A','B'})

if __name__=='__main__':unittest.main()
