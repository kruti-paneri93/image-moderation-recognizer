import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RekognitionHelper:
    def __init__(self):
        """Initialize AWS Rekognition client"""
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
    
    def detect_moderation_labels(self, image_bytes, min_confidence=60):
        """
        Detect inappropriate content in image
        
        Args:
            image_bytes: Image in bytes format
            min_confidence: Minimum confidence threshold (0-100)
            
        Returns:
            dict: Moderation labels with confidence scores
        """
        try:
            response = self.client.detect_moderation_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=min_confidence
            )
            return response
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_safety(self, moderation_response, threshold=60):
        """
        Analyze if image is safe based on moderation labels
        
        Args:
            moderation_response: Response from detect_moderation_labels
            threshold: Confidence threshold for unsafe content
            
        Returns:
            dict: Safety analysis with verdict and details
        """
        if 'error' in moderation_response:
            return {
                'is_safe': None,
                'verdict': 'Error',
                'message': moderation_response['error'],
                'labels': []
            }
        
        labels = moderation_response.get('ModerationLabels', [])
        
        # Check if any high-confidence inappropriate content found
        unsafe_labels = [
            label for label in labels 
            if label['Confidence'] >= threshold
        ]
        
        is_safe = len(unsafe_labels) == 0
        
        if is_safe:
            verdict = "✅ SAFE"
            message = "No inappropriate content detected"
        else:
            verdict = "❌ UNSAFE"
            message = f"Found {len(unsafe_labels)} inappropriate content categories"
        
        return {
            'is_safe': is_safe,
            'verdict': verdict,
            'message': message,
            'labels': labels,
            'unsafe_count': len(unsafe_labels)
        }